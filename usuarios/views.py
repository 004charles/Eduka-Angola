from django.shortcuts import render, redirect, get_object_or_404
import os

from django.utils.translation import gettext as _
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Usuario, Aluno, PerfilAluno, CodigoVerificacao, PreferenciaNotificacaoAluno, NotificacaoAluno, CandidaturaFormador
from gestoreduka.models import CentroDeFormacao, CentroSeguimento, Conversa, Depoimento, Mensagem
from cursos_app.models import Curso, Favorito, Categoria, Inscricao
from bolsas.models import Bolsa, CandidaturaBolsa
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import IntegrityError, models
from django.core.exceptions import ValidationError
from django.urls import reverse
from hashlib import sha256
from .decorators import aluno_logado_e_centros
import random
import hmac
import json
from datetime import timedelta
from django.utils import timezone


def _dados_json(request):
    """Lê com segurança o corpo JSON usado pelo frontend público React."""
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except (TypeError, ValueError, UnicodeDecodeError):
        return {}


def _destino_publico_seguro(destino):
    """Permite apenas caminhos locais ao concluir uma ação pública."""
    destino = str(destino or '').strip()
    return destino if destino.startswith('/') and not destino.startswith('//') else '/'


_TESTE_FORMADOR = [
    {
        'id': 'aprendizagem',
        'pergunta': 'Qual é uma boa prática ao preparar uma aula em vídeo?',
        'opcoes': [
            {'id': 'A', 'texto': 'Publicar sem objectivos definidos.'},
            {'id': 'B', 'texto': 'Definir objectivos claros e uma sequência de aprendizagem.'},
            {'id': 'C', 'texto': 'Evitar exemplos e exercícios.'},
        ],
        'correta': 'B',
    },
    {
        'id': 'inclusao',
        'pergunta': 'Como deve um formador lidar com dúvidas dos alunos?',
        'opcoes': [
            {'id': 'A', 'texto': 'Responder com respeito e orientar com clareza.'},
            {'id': 'B', 'texto': 'Ignorar dúvidas repetidas.'},
            {'id': 'C', 'texto': 'Partilhar dados pessoais de outros alunos.'},
        ],
        'correta': 'A',
    },
    {
        'id': 'conteudo',
        'pergunta': 'O conteúdo de um curso deve ser:',
        'opcoes': [
            {'id': 'A', 'texto': 'Copiado sem autorização de outras fontes.'},
            {'id': 'B', 'texto': 'Relevante, exacto e com respeito por direitos de autor.'},
            {'id': 'C', 'texto': 'Prometido sem conseguir ser leccionado.'},
        ],
        'correta': 'B',
    },
]


def _cursos_video_concluidos(aluno):
    cursos = aluno.cursos_inscritos_video.prefetch_related('aulas').all()
    return sum(1 for curso in cursos if curso.verificar_conclusao(aluno))


def _formador_estado(aluno):
    concluidos = _cursos_video_concluidos(aluno)
    candidatura = getattr(aluno, 'candidatura_formador', None)
    if concluidos < 2 and not candidatura:
        return None
    return {
        'elegivel': concluidos >= 2,
        'estado': candidatura.estado if candidatura else 'ELEGIVEL',
        'titulo_profissional': candidatura.titulo_profissional if candidatura else '',
    }


def _aluno_api_autenticado(request):
    if not request.user.is_authenticated:
        return None, JsonResponse({'ok': False, 'code': 'NAO_AUTENTICADO', 'message': 'Entre para consultar as suas mensagens.'}, status=401)
    if request.user.tipo_usuario != 'ALUNO':
        return None, JsonResponse({'ok': False, 'message': 'Esta área é exclusiva para alunos.'}, status=403)
    aluno = getattr(request.user, 'aluno_profile', None)
    if not aluno:
        return None, JsonResponse({'ok': False, 'message': 'Não encontrámos o perfil de aluno desta conta.'}, status=404)
    return aluno, None


def _payload_mensagem_aluno(mensagem):
    try:
        arquivo_url = mensagem.arquivo.url if mensagem.arquivo else ''
    except ValueError:
        arquivo_url = ''
    return {
        'id': mensagem.id,
        'texto': mensagem.mensagem,
        'tipo': mensagem.tipo,
        'arquivo_url': arquivo_url,
        'data': mensagem.data_envio.isoformat(),
        'autor': 'CENTRO' if mensagem.remetente_centro_id else 'ALUNO',
    }


@require_GET
def api_react_aluno_conversas(request):
    """Lista as conversas de atendimento acessíveis ao aluno autenticado."""
    aluno, erro = _aluno_api_autenticado(request)
    if erro:
        return erro
    conversas = Conversa.objects.filter(aluno=aluno, ativa=True).select_related('centro').order_by('-ultima_mensagem')
    itens = []
    for conversa in conversas:
        ultima = Mensagem.objects.filter(conversa=conversa, digitando=False).order_by('-data_envio').first()
        nao_lidas = Mensagem.objects.filter(conversa=conversa, remetente_centro__isnull=False, lida=False, digitando=False).count()
        itens.append({
            'id': conversa.id,
            'centro_id': conversa.centro_id,
            'centro': conversa.centro.nome,
            'ultima_atividade': conversa.ultima_mensagem.isoformat(),
            'ultima_mensagem': (ultima.mensagem if ultima else '')[:100],
            'nao_lidas': nao_lidas,
        })
    return JsonResponse({'ok': True, 'conversas': itens, 'total_nao_lidas': sum(item['nao_lidas'] for item in itens)})


@require_POST
def api_react_aluno_conversa_iniciar(request):
    """Cria ou abre a conversa exclusiva entre o aluno e um centro de formação."""
    aluno, erro = _aluno_api_autenticado(request)
    if erro:
        return erro
    dados = _dados_json(request)
    centro_id = dados.get('centro_id')
    try:
        centro = CentroDeFormacao.objects.get(id=int(centro_id), ativo=True)
    except (TypeError, ValueError, CentroDeFormacao.DoesNotExist):
        return JsonResponse({'ok': False, 'message': 'O centro seleccionado não está disponível para atendimento.'}, status=404)
    conversa, criada = Conversa.objects.get_or_create(centro=centro, aluno=aluno, defaults={'ativa': True})
    if not conversa.ativa:
        conversa.ativa = True
        conversa.save(update_fields=['ativa'])
    return JsonResponse({'ok': True, 'criada': criada, 'conversa': {'id': conversa.id, 'centro_id': centro.id, 'centro': centro.nome}}, status=201 if criada else 200)


@require_GET
def api_react_aluno_conversa_detalhe(request, conversa_id):
    """Devolve o histórico de uma conversa do aluno e marca respostas do centro como lidas."""
    aluno, erro = _aluno_api_autenticado(request)
    if erro:
        return erro
    conversa = get_object_or_404(Conversa.objects.select_related('centro'), id=conversa_id, aluno=aluno, ativa=True)
    mensagens = Mensagem.objects.filter(conversa=conversa, digitando=False).select_related('remetente_aluno', 'remetente_centro').order_by('data_envio')
    mensagens.filter(remetente_centro__isnull=False, lida=False).update(lida=True)
    NotificacaoAluno.objects.filter(aluno=aluno, tipo='CHAT', lida=False).update(lida=True)
    return JsonResponse({'ok': True, 'conversa': {'id': conversa.id, 'centro_id': conversa.centro_id, 'centro': conversa.centro.nome}, 'mensagens': [_payload_mensagem_aluno(item) for item in mensagens]})


@require_POST
def api_react_aluno_conversa_mensagem(request, conversa_id):
    """Envia uma mensagem do aluno para o centro associado à conversa."""
    aluno, erro = _aluno_api_autenticado(request)
    if erro:
        return erro
    conversa = get_object_or_404(Conversa, id=conversa_id, aluno=aluno, ativa=True)
    dados = _dados_json(request)
    texto = str(dados.get('mensagem', '')).strip()
    if not texto:
        return JsonResponse({'ok': False, 'message': 'Escreva uma mensagem antes de enviar.'}, status=400)
    if len(texto) > 4000:
        return JsonResponse({'ok': False, 'message': 'A mensagem não pode ultrapassar 4 000 caracteres.'}, status=400)
    mensagem = Mensagem.objects.create(conversa=conversa, remetente_aluno=aluno, mensagem=texto, tipo='TEXTO')
    return JsonResponse({'ok': True, 'mensagem': _payload_mensagem_aluno(mensagem)}, status=201)


@ensure_csrf_cookie
def api_auth_csrf(request):
    """Emite o cookie CSRF para formulários React servidos pelo proxy local."""
    return JsonResponse({'ok': True})


@require_GET
def api_auth_aluno_resumo(request):
    """Resumo autenticado da jornada do aluno consumido pelo painel React."""
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'code': 'NAO_AUTENTICADO', 'message': 'Entre para consultar a sua área.'}, status=401)
    if request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'ok': False, 'message': 'Esta área é exclusiva para alunos.'}, status=403)

    aluno = getattr(request.user, 'aluno_profile', None)
    if not aluno:
        return JsonResponse({'ok': False, 'message': 'Não encontrámos o perfil de aluno desta conta.'}, status=404)

    from cursovideoapp.models import ProgressoAula

    def imagem_curso(curso):
        try:
            return curso.get_imagem_url
        except Exception:
            return ''

    inscricoes = Inscricao.objects.filter(aluno=aluno).select_related(
        'curso', 'curso__centro', 'turma_escolhida'
    ).order_by('-data_inscricao')
    presenciais = []
    for inscricao in inscricoes:
        turma = inscricao.turma_escolhida
        presenciais.append({
            'id': f'presencial-{inscricao.id}',
            'is_video': False,
            'titulo': inscricao.curso.titulo,
            'centro': inscricao.curso.centro.nome if inscricao.curso.centro else 'Centro de formação',
            'imagem_url': imagem_curso(inscricao.curso),
            'status': inscricao.status,
            'status_label': inscricao.get_status_display(),
            'turma': turma.nome if turma else '',
            'inicio': turma.data_inicio.isoformat() if turma and turma.data_inicio else '',
            'inicio_formatado': turma.data_inicio.strftime('%d/%m/%Y') if turma and turma.data_inicio else '',
            'horario': turma.horario_formatado if turma else '',
            'local': turma.local if turma else '',
            'valor_pago': float(inscricao.valor_pago or 0),
            'valor_pago_formatado': f"{inscricao.valor_pago:,.0f} Kz".replace(',', ' ') if inscricao.valor_pago else 'Sem valor pago registado',
            'detalhe_url': f'/cursos/{inscricao.curso_id}',
            'ficha_url': reverse('baixar_ficha_inscricao', kwargs={'inscricao_id': inscricao.id}),
        })

    videos = aluno.cursos_inscritos_video.select_related('centro', 'categoria').prefetch_related('aulas').all()
    video_itens = []
    for curso in videos:
        total_aulas = curso.aulas.count()
        concluidas = ProgressoAula.objects.filter(aluno=aluno, aula__curso=curso, concluida=True).count()
        progresso = int((concluidas / total_aulas) * 100) if total_aulas else 0
        video_itens.append({
            'id': f'video-{curso.id}',
            'is_video': True,
            'titulo': curso.titulo,
            'centro': curso.centro.nome if curso.centro else 'Edukangola',
            'imagem_url': imagem_curso(curso),
            'progresso': progresso,
            'aulas_concluidas': concluidas,
            'total_aulas': total_aulas,
            'detalhe_url': f'/video-cursos/{curso.slug}',
        })

    ativos = [item for item in presenciais if item['status'] == 'A'] + video_itens
    pendentes = [item for item in presenciais if item['status'] == 'P']
    total_certificados = aluno.certificados.filter(status='EMITIDO').count() if hasattr(aluno, 'certificados') else 0

    return JsonResponse({
        'ok': True,
        'aluno': {'nome': aluno.nome or request.user.nome or request.user.email.split('@')[0], 'email': request.user.email},
        'resumo': {
            'cursos_ativos': len(ativos),
            'inscricoes_pendentes': len(pendentes),
            'certificados': total_certificados,
        },
        'continuar_aprender': (video_itens + [item for item in presenciais if item['status'] == 'A'])[:6],
        'inscricoes': presenciais[:12],
    })


@require_POST
def api_auth_login(request):
    dados = _dados_json(request)
    email = str(dados.get('email') or '').strip().lower()
    senha = str(dados.get('senha') or '')
    destino = _destino_publico_seguro(dados.get('next'))

    if not email or not senha:
        return JsonResponse({'ok': False, 'message': 'Indique o e-mail e a palavra-passe.'}, status=400)

    user = authenticate(request, username=email, password=senha)
    if user is None:
        return JsonResponse({'ok': False, 'message': 'E-mail ou palavra-passe incorretos.'}, status=401)
    if user.tipo_usuario != 'ALUNO':
        return JsonResponse({'ok': False, 'message': 'Esta área de acesso é exclusiva para alunos.'}, status=403)
    if not user.is_active:
        request.session['email_verificacao'] = user.email
        request.session['public_auth_next'] = destino
        return JsonResponse({
            'ok': False,
            'code': 'EMAIL_NAO_VERIFICADO',
            'message': 'Confirme o código enviado para o seu e-mail antes de entrar.',
        }, status=403)

    login(request, user)
    return JsonResponse({'ok': True, 'redirect': destino, 'nome': user.nome or ''})


@require_POST
def api_auth_admin_login(request):
    """Inicia a sessão isolada usada exclusivamente pelo painel React em /admin."""
    dados = _dados_json(request)
    email = str(dados.get('email') or '').strip().lower()
    senha = str(dados.get('senha') or '')

    if not email or not senha:
        return JsonResponse({'ok': False, 'message': 'Indique o e-mail e a palavra-passe.'}, status=400)

    user = authenticate(request, username=email, password=senha)
    if user is None or not user.is_active or not (user.is_staff or user.is_superuser):
        return JsonResponse({'ok': False, 'message': 'Não foi possível iniciar a sessão administrativa com estes dados.'}, status=401)

    login(request, user)
    return JsonResponse({'ok': True, 'redirect': '/admin', 'nome': user.nome or ''})


@require_POST
def api_auth_admin_recuperar_senha(request):
    """Envia um código de recuperação sem revelar se há uma conta administrativa."""
    dados = _dados_json(request)
    email = str(dados.get('email') or '').strip().lower()
    usuario = Usuario.objects.filter(
        email=email,
        is_active=True,
    ).filter(models.Q(is_staff=True) | models.Q(is_superuser=True)).first()

    if usuario:
        try:
            enviar_codigo_verificacao(email, 'RECUPERACAO')
            request.session['email_recuperacao_admin'] = email
        except Exception:
            return JsonResponse({'ok': False, 'message': 'Não foi possível enviar o código. Tente novamente.'}, status=500)

    return JsonResponse({'ok': True, 'message': 'Se existir uma conta administrativa com este e-mail, enviámos um código de recuperação.'})


@require_POST
def api_auth_admin_redefinir_senha(request):
    """Valida o código administrativo, substitui a palavra-passe e inicia a sessão isolada."""
    dados = _dados_json(request)
    codigo = str(dados.get('codigo') or '').strip()
    senha = str(dados.get('senha') or '')
    confirmar_senha = str(dados.get('confirmar_senha') or '')
    email = request.session.get('email_recuperacao_admin')

    if not email:
        return JsonResponse({'ok': False, 'message': 'A sessão de recuperação expirou. Comece novamente.'}, status=400)
    if len(senha) < 8:
        return JsonResponse({'ok': False, 'message': 'A palavra-passe deve ter pelo menos 8 caracteres.'}, status=400)
    if senha != confirmar_senha:
        return JsonResponse({'ok': False, 'message': 'As palavras-passe não coincidem.'}, status=400)

    verificacao = CodigoVerificacao.objects.filter(
        email=email,
        codigo=codigo,
        tipo='RECUPERACAO',
        criado_em__gte=timezone.now() - timedelta(minutes=10),
    ).order_by('-criado_em').first()
    usuario = Usuario.objects.filter(email=email, is_active=True).filter(
        models.Q(is_staff=True) | models.Q(is_superuser=True)
    ).first()
    if not verificacao or not usuario:
        return JsonResponse({'ok': False, 'message': 'O código é inválido ou expirou. Peça um novo código.'}, status=400)

    usuario.set_password(senha)
    usuario.save(update_fields=['password'])
    CodigoVerificacao.objects.filter(email=email, tipo='RECUPERACAO').delete()
    request.session.pop('email_recuperacao_admin', None)
    login(request, usuario, backend='usuarios.backends.EmailBackend')
    return JsonResponse({'ok': True, 'redirect': '/admin'})


@require_POST
def api_auth_admin_bootstrap(request):
    """Cria temporariamente o primeiro administrador mediante token definido só no ambiente."""
    token_esperado = os.getenv('ADMIN_BOOTSTRAP_TOKEN', '')
    if not token_esperado:
        return JsonResponse({'ok': False, 'message': 'A criação temporária de administrador não está activa.'}, status=403)

    dados = _dados_json(request)
    token = str(dados.get('token') or '')
    if not hmac.compare_digest(token, token_esperado):
        return JsonResponse({'ok': False, 'message': 'Não foi possível validar a autorização de criação.'}, status=403)

    nome = str(dados.get('nome') or '').strip()
    email = str(dados.get('email') or '').strip().lower()
    senha = str(dados.get('senha') or '')
    confirmar_senha = str(dados.get('confirmar_senha') or '')
    if not nome or not email or not senha:
        return JsonResponse({'ok': False, 'message': 'Preencha nome, e-mail e palavra-passe.'}, status=400)
    if len(senha) < 12:
        return JsonResponse({'ok': False, 'message': 'A palavra-passe deve ter pelo menos 12 caracteres.'}, status=400)
    if senha != confirmar_senha:
        return JsonResponse({'ok': False, 'message': 'As palavras-passe não coincidem.'}, status=400)
    if Usuario.objects.filter(email=email).exists():
        return JsonResponse({'ok': False, 'message': 'Já existe uma conta com este e-mail.'}, status=409)

    admin = Usuario.objects.create_superuser(email=email, nome=nome, password=senha)
    if admin.tipo_usuario != 'ADMIN':
        admin.tipo_usuario = 'ADMIN'
        admin.save(update_fields=['tipo_usuario'])
    login(request, admin, backend='usuarios.backends.EmailBackend')
    return JsonResponse({'ok': True, 'redirect': '/admin', 'nome': admin.nome})


@require_POST
def api_auth_registro(request):
    dados = _dados_json(request)
    nome = str(dados.get('nome') or '').strip()
    email = str(dados.get('email') or '').strip().lower()
    senha = str(dados.get('senha') or '')
    confirmar_senha = str(dados.get('confirmar_senha') or '')
    destino = _destino_publico_seguro(dados.get('next'))

    if not nome or not email or not senha:
        return JsonResponse({'ok': False, 'message': 'Preencha nome, e-mail e palavra-passe.'}, status=400)
    if len(senha) < 8:
        return JsonResponse({'ok': False, 'message': 'A palavra-passe deve ter pelo menos 8 caracteres.'}, status=400)
    if senha != confirmar_senha:
        return JsonResponse({'ok': False, 'message': 'As palavras-passe não coincidem.'}, status=400)

    usuario = Usuario.objects.filter(email=email).first()
    if usuario and usuario.tipo_usuario != 'ALUNO':
        return JsonResponse({'ok': False, 'message': 'Este e-mail está associado a uma conta de centro ou administração.'}, status=409)
    if usuario and usuario.is_active and usuario.has_usable_password():
        return JsonResponse({
            'ok': False,
            'code': 'CONTA_EXISTENTE',
            'message': 'Já existe uma conta ativa com este e-mail. Entre para continuar.',
        }, status=409)

    try:
        if usuario is None:
            usuario = Usuario.objects.create_user(email=email, nome=nome, password=senha, tipo_usuario='ALUNO')
        else:
            usuario.nome = nome
            usuario.set_password(senha)

        # Uma conta criada automaticamente numa inscrição de visitante ganha
        # palavra-passe somente depois de o e-mail ser confirmado.
        usuario.is_active = False
        usuario.save()
        aluno, _ = Aluno.objects.get_or_create(usuario=usuario, defaults={'nome': nome, 'ativo': False})
        aluno.nome = nome
        aluno.ativo = False
        aluno.save(update_fields=['nome', 'ativo'])
        PerfilAluno.objects.get_or_create(aluno=aluno)
    except Exception:
        return JsonResponse({'ok': False, 'message': 'Não foi possível criar a conta. Tente novamente.'}, status=500)

    try:
        enviar_codigo_verificacao(email, 'CADASTRO')
        request.session['email_verificacao'] = email
        request.session['public_auth_next'] = destino
        return JsonResponse({'ok': True, 'requires_verification': True, 'email': email})
    except Exception:
        return JsonResponse({'ok': False, 'message': 'A conta foi preparada, mas não foi possível enviar o código. Tente reenviar.'}, status=500)


@require_POST
def api_auth_verificar_email(request):
    dados = _dados_json(request)
    codigo = str(dados.get('codigo') or '').strip()
    email = request.session.get('email_verificacao')
    if not email:
        return JsonResponse({'ok': False, 'message': 'A sessão de verificação expirou. Crie a conta novamente.'}, status=400)
    if len(codigo) != 6 or not codigo.isdigit():
        return JsonResponse({'ok': False, 'message': 'Introduza o código de seis dígitos enviado por e-mail.'}, status=400)

    verificacao = CodigoVerificacao.objects.filter(
        email=email,
        codigo=codigo,
        tipo='CADASTRO',
        criado_em__gte=timezone.now() - timedelta(minutes=10),
    ).order_by('-criado_em').first()
    if not verificacao:
        return JsonResponse({'ok': False, 'message': 'O código é inválido ou expirou. Peça um novo código.'}, status=400)

    usuario = Usuario.objects.filter(email=email, tipo_usuario='ALUNO').first()
    if not usuario:
        return JsonResponse({'ok': False, 'message': 'Não encontrámos a conta associada a este código.'}, status=404)
    usuario.is_active = True
    usuario.save(update_fields=['is_active'])
    Aluno.objects.filter(usuario=usuario).update(ativo=True)
    CodigoVerificacao.objects.filter(email=email, tipo='CADASTRO').delete()
    request.session.pop('email_verificacao', None)
    destino = _destino_publico_seguro(request.session.pop('public_auth_next', '/'))
    login(request, usuario, backend='usuarios.backends.EmailBackend')
    try:
        enviar_email_confirmacao_aluno(usuario.nome, usuario.email)
    except Exception:
        pass
    return JsonResponse({'ok': True, 'redirect': destino})


@require_POST
def api_auth_reenviar_codigo(request):
    email = request.session.get('email_verificacao')
    if not email:
        return JsonResponse({'ok': False, 'message': 'A sessão de verificação expirou. Crie a conta novamente.'}, status=400)
    try:
        enviar_codigo_verificacao(email, 'CADASTRO')
        return JsonResponse({'ok': True, 'message': 'Enviámos um novo código para o seu e-mail.'})
    except Exception:
        return JsonResponse({'ok': False, 'message': 'Não foi possível reenviar o código. Tente novamente.'}, status=500)


@require_POST
def api_auth_recuperar_senha(request):
    dados = _dados_json(request)
    email = str(dados.get('email') or '').strip().lower()
    destino = _destino_publico_seguro(dados.get('next'))
    usuario = Usuario.objects.filter(email=email, tipo_usuario='ALUNO').first()
    if usuario:
        try:
            enviar_codigo_verificacao(email, 'RECUPERACAO')
            request.session['email_recuperacao'] = email
            request.session['public_auth_next'] = destino
        except Exception:
            return JsonResponse({'ok': False, 'message': 'Não foi possível enviar o código. Tente novamente.'}, status=500)
    # A resposta não revela se um e-mail está ou não associado a uma conta.
    return JsonResponse({'ok': True, 'message': 'Se existir uma conta com este e-mail, enviámos um código de recuperação.'})


@require_POST
def api_auth_redefinir_senha(request):
    dados = _dados_json(request)
    codigo = str(dados.get('codigo') or '').strip()
    senha = str(dados.get('senha') or '')
    confirmar_senha = str(dados.get('confirmar_senha') or '')
    email = request.session.get('email_recuperacao')
    if not email:
        return JsonResponse({'ok': False, 'message': 'A sessão de recuperação expirou. Comece novamente.'}, status=400)
    if len(senha) < 8:
        return JsonResponse({'ok': False, 'message': 'A palavra-passe deve ter pelo menos 8 caracteres.'}, status=400)
    if senha != confirmar_senha:
        return JsonResponse({'ok': False, 'message': 'As palavras-passe não coincidem.'}, status=400)

    verificacao = CodigoVerificacao.objects.filter(
        email=email,
        codigo=codigo,
        tipo='RECUPERACAO',
        criado_em__gte=timezone.now() - timedelta(minutes=10),
    ).order_by('-criado_em').first()
    if not verificacao:
        return JsonResponse({'ok': False, 'message': 'O código é inválido ou expirou. Peça um novo código.'}, status=400)

    usuario = Usuario.objects.filter(email=email, tipo_usuario='ALUNO').first()
    if not usuario:
        return JsonResponse({'ok': False, 'message': 'Não encontrámos a conta associada a este código.'}, status=404)
    usuario.set_password(senha)
    usuario.save(update_fields=['password'])
    CodigoVerificacao.objects.filter(email=email, tipo='RECUPERACAO').delete()
    request.session.pop('email_recuperacao', None)
    destino = _destino_publico_seguro(request.session.pop('public_auth_next', '/'))
    login(request, usuario, backend='usuarios.backends.EmailBackend')
    return JsonResponse({'ok': True, 'redirect': destino})


def api_notificacoes_nao_lidas(request):
    """Retorna o número de notificações não lidas e as últimas 5 notificações para o polling do frontend."""
    if not request.user.is_authenticated:
        return JsonResponse({'count': 0, 'notificacoes': []})
        
    user = request.user
    dados = {
        'count': 0,
        'chat_count': 0,
        'notificacoes': []
    }
    
    if user.tipo_usuario in ['GESTOR', 'GESTOR_FILIAL']:
        from gestoreduka.models import NotificacaoGestor, Filial
        centro = None
        if user.tipo_usuario == 'GESTOR':
            centro = getattr(user, 'centro_formacao', None)
        else:
            filial = Filial.objects.filter(usuario=user).first()
            if filial:
                centro = filial.centro_principal
                
        if centro:
            nao_lidas = NotificacaoGestor.objects.filter(centro=centro, lida=False)
            dados['count'] = nao_lidas.count()
            for notif in nao_lidas.order_by('-data_criacao')[:5]:
                dados['notificacoes'].append({
                    'id': notif.id,
                    'titulo': notif.titulo,
                    'mensagem': notif.mensagem,
                    'link': notif.link or '#',
                    'tipo': notif.tipo,
                    'data': notif.data_criacao.strftime('%d/%m/%Y %H:%M')
                })
                
    elif user.tipo_usuario == 'ALUNO':
        from usuarios.models import NotificacaoAluno
        aluno = getattr(user, 'aluno_profile', None)
        if aluno:
            nao_lidas = NotificacaoAluno.objects.filter(aluno=aluno, lida=False)
            dados['count'] = nao_lidas.count()
            dados['chat_count'] = nao_lidas.filter(tipo='CHAT').count()
            for notif in nao_lidas.order_by('-data_criacao')[:5]:
                dados['notificacoes'].append({
                    'id': notif.id,
                    'titulo': notif.titulo,
                    'mensagem': notif.mensagem,
                    'link': notif.link or '#',
                    'tipo': notif.tipo,
                    'data': notif.data_criacao.strftime('%d/%m/%Y %H:%M')
                })
                
    return JsonResponse(dados)


@require_POST
def api_notificacoes_chat_lidas(request):
    """Marca apenas os avisos de conversa como lidos, preservando os restantes alertas da conta."""
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'ok': False, 'message': 'Entre como aluno para actualizar notificações.'}, status=401)
    aluno = getattr(request.user, 'aluno_profile', None)
    if not aluno:
        return JsonResponse({'ok': False, 'message': 'Perfil de aluno indisponível.'}, status=404)
    total, _ = NotificacaoAluno.objects.filter(aluno=aluno, tipo='CHAT', lida=False).update(lida=True)
    return JsonResponse({'ok': True, 'actualizadas': total})


@require_POST
def api_interna_criar_notificacao(request):
    """Cria uma notificação na plataforma a pedido do serviço separado."""
    segredo = os.getenv('NOTIFICATION_SERVICE_DJANGO_SECRET', '')
    apresentado = request.headers.get('X-Notification-Service-Key', '')
    if not segredo:
        return JsonResponse({'detail': 'Serviço interno não configurado.'}, status=503)
    if not hmac.compare_digest(apresentado, segredo):
        return JsonResponse({'detail': 'Não autorizado.'}, status=401)
    dados = _dados_json(request)
    aluno_id = dados.get('aluno_id')
    titulo = str(dados.get('titulo', '')).strip()[:150]
    mensagem = str(dados.get('mensagem', '')).strip()
    if not aluno_id or not titulo or not mensagem:
        return JsonResponse({'detail': 'aluno_id, titulo e mensagem são obrigatórios.'}, status=400)
    aluno = Aluno.objects.filter(pk=aluno_id, ativo=True).first()
    if not aluno:
        return JsonResponse({'detail': 'Aluno não encontrado.'}, status=404)
    from usuarios.models import NotificacaoAluno
    notificacao = NotificacaoAluno.objects.create(
        aluno=aluno,
        titulo=titulo,
        mensagem=mensagem[:4000],
        link=str(dados.get('link', '')).strip()[:255] or None,
        tipo=str(dados.get('tipo', 'SISTEMA')).strip()[:20] or 'SISTEMA',
    )
    return JsonResponse({'ok': True, 'id': notificacao.id}, status=201)


@require_GET
def api_interna_destinatarios_notificacao(request):
    """Resolve destinatários para o serviço separado sem expor a API publicamente."""
    segredo = os.getenv('NOTIFICATION_SERVICE_DJANGO_SECRET', '')
    apresentado = request.headers.get('X-Notification-Service-Key', '')
    if not segredo:
        return JsonResponse({'detail': 'Serviço interno não configurado.'}, status=503)
    if not hmac.compare_digest(apresentado, segredo):
        return JsonResponse({'detail': 'Não autorizado.'}, status=401)
    tipos_para_preferencia = {
        'course.published': 'novos_cursos',
        'class.opened': 'novas_turmas',
        'book.published': 'novos_livros',
        'event.published': 'novos_eventos',
        'learning.reminder': 'atualizacoes_aprendizagem',
        'calendar.notice': 'calendario_e_feriados',
        'weekly.digest.requested': 'resumo_semanal',
    }
    event_type = request.GET.get('event_type', '').strip()
    preferencia = tipos_para_preferencia.get(event_type)
    if not preferencia:
        return JsonResponse({'detail': 'Tipo de evento não suportado.'}, status=400)
    channel = request.GET.get('channel', 'platform').strip().lower()
    if channel not in ('platform', 'email'):
        return JsonResponse({'detail': 'Canal não suportado.'}, status=400)
    canal_preferencia = 'receber_na_plataforma' if channel == 'platform' else 'receber_por_email'
    alunos = Aluno.objects.filter(ativo=True, usuario__is_active=True, **{f'preferencias_notificacao__{canal_preferencia}': True, f'preferencias_notificacao__{preferencia}': True}).select_related('usuario', 'preferencias_notificacao')
    recipient_id = request.GET.get('recipient_id')
    if recipient_id:
        alunos = alunos.filter(pk=recipient_id)
    destinatarios = [{'id': aluno.id, 'nome': aluno.nome, 'email': aluno.usuario.email} for aluno in alunos if aluno.usuario.email]
    return JsonResponse({'event_type': event_type, 'channel': channel, 'destinatarios': destinatarios})


def conta_aluno(request):
    """
    Renderiza o painel principal da conta do aluno.
    """
    return render(request, 'conta_aluno.html')

@require_POST
def adicionar_favorito(request, curso_id):
    """
    View AJAX para alternar um curso na lista de favoritos do aluno.
    """
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'status': 'error', 'message': 'Não autenticado'}, status=403)
    
    try:
        curso = Curso.objects.get(id=curso_id)
        aluno = request.user.aluno_profile
        
        favorito, created = Favorito.objects.get_or_create(
            aluno=aluno,
            curso=curso
        )
        
        if created:
            return JsonResponse({'status': 'added', 'message': 'Curso adicionado aos favoritos'})
        else:
            favorito.delete()
            return JsonResponse({'status': 'removed', 'message': 'Curso removido dos favoritos'})
            
    except Curso.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Curso não encontrado'}, status=404)
    except Aluno.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Aluno não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

#-----------------------------validacao aluno----------------------------------



def login_aluno(request):
    """
    Renderiza o Portal de Entrada (Landing Gate) para login e registro.
    """
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        return redirect('aluno')
        
    status = request.GET.get('status', '')
    next_url = request.GET.get('next', '')
    
    context = {}
    if status:
        context['status'] = status
    if next_url:
        context['next'] = next_url
        
    return render(request, 'core/landing_gate.html', context)



from cursos_app.models import Favorito, Inscricao

def get_aluno_common_context(request):
    """Retorna o contexto comum para todas as páginas do aluno."""
    aluno = request.aluno_obj
    perfil = request.perfil
    inscricoes_reais = Inscricao.objects.filter(aluno=aluno).select_related('curso', 'curso__centro')
    
    return {
        'aluno_logado': True,
        'aluno_nome': aluno.nome,
        'aluno_obj': aluno,
        'perfil': perfil,
        'inscricoes_reais': inscricoes_reais,
        'hide_sidebar': True,
    }

@aluno_logado_e_centros
def aluno_dashboard(request):
    from cursovideoapp.models import ProgressoAula
    context = get_aluno_common_context(request)
    aluno = context['aluno_obj']
    
    # Check Onboarding
    if not hasattr(aluno, 'perfil') or not aluno.perfil.onboarding_completo:
        return redirect('aluno_onboarding')
    
    inscricoes_com_progresso = []
    
    # Cursos do catálogo presencial/híbrido
    for inscricao in context['inscricoes_reais']:
        curso = inscricao.curso
        progresso = 0
        total_aulas = 0
        concluidas = 0
        
        inscricoes_com_progresso.append({
            'is_video': False,
            'inscricao': inscricao,
            'curso': curso,
            'progresso': progresso,
            'total_aulas': total_aulas,
            'concluidas': concluidas,
            'imagem_url': curso.imagem.url if curso.imagem else None,
            'titulo': curso.titulo,
            'id': curso.id,
            'turma': getattr(inscricao, 'turma_escolhida', None),
            'status_label': 'Inscrição ativa' if inscricao.status == 'A' else inscricao.get_status_display(),
            'inscricao_status': inscricao.status,
        })
        
    # Cursos do catálogo em vídeo
    cursos_videos = aluno.cursos_inscritos_video.all()
    for curso_video in cursos_videos:
        total_aulas = curso_video.aulas.count()
        concluidas = ProgressoAula.objects.filter(aluno=aluno, aula__curso=curso_video, concluida=True).count()
        progresso = int((concluidas / total_aulas * 100)) if total_aulas > 0 else 0
        
        inscricoes_com_progresso.append({
            'is_video': True,
            'curso': curso_video,
            'progresso': progresso,
            'total_aulas': total_aulas,
            'concluidas': concluidas,
            'imagem_url': curso_video.capa.url if curso_video.capa else None,
            'titulo': curso_video.titulo,
            'slug': curso_video.slug
        })
    
    total_cursos_ativos = context['inscricoes_reais'].filter(status='A').count() + cursos_videos.count()
    cursos_inscritos_ids = context['inscricoes_reais'].values_list('curso_id', flat=True)
    cursos_recomendados = Curso.objects.filter(
        publicado=True,
        ativo=True,
    ).exclude(id__in=cursos_inscritos_ids).select_related('centro', 'categoria').order_by('-destaque', '-data_criacao')[:4]
    
    # Contar certificados
    total_certificados = 0
    if hasattr(aluno, 'certificados'):
        total_certificados = aluno.certificados.count()
    
    from cursovideoapp.models import FavoritoCursoVideo
    
    favoritos_presencial = Favorito.objects.filter(aluno=request.aluno_obj).select_related('curso')
    favoritos_video = FavoritoCursoVideo.objects.filter(aluno=request.aluno_obj).select_related('curso')
    
    favoritos_dashboard = []
    for f in favoritos_presencial:
        favoritos_dashboard.append({'curso': f.curso, 'is_video': False})
    for f in favoritos_video:
        favoritos_dashboard.append({'curso': f.curso, 'is_video': True})

    # Dados do Fundo de Bolsas
    bolsas_aluno = Bolsa.objects.filter(aluno=aluno).select_related('patrocinador', 'curso')
    candidaturas_aluno = CandidaturaBolsa.objects.filter(aluno=aluno).select_related('curso_pretendido')

    # Competências do Aluno (Skills)
    from carreira.models import AlunoSkill, Skill
    minhas_skills = AlunoSkill.objects.filter(aluno=aluno).select_related('skill')
    skills_comprovadas = minhas_skills.filter(comprovada=True)
    
    # Skills sugeridas baseadas nos cursos em andamento
    skills_em_desenvolvimento = Skill.objects.filter(
        models.Q(cursos_relacionados__inscricoes__aluno=aluno, cursos_relacionados__inscricoes__status='A') |
        models.Q(cursos_video_relacionados__inscritos=aluno)
    ).distinct().exclude(id__in=minhas_skills.values_list('skill_id', flat=True))

    context.update({
        'current_page': 'dashboard',
        'total_cursos': context['inscricoes_reais'].count() + cursos_videos.count(),
        'total_cursos_ativos': total_cursos_ativos,
        'total_certificados': total_certificados,
        'total_cursos_concluidos': total_certificados,
        'inscricoes_com_progresso': inscricoes_com_progresso,
        'curso_em_destaque': inscricoes_com_progresso[0] if inscricoes_com_progresso else None,
        'cursos_recomendados': cursos_recomendados,
        'favoritos_dashboard': favoritos_dashboard,
        'bolsas_aluno': bolsas_aluno,
        'candidaturas_aluno': candidaturas_aluno,
        'skills_comprovadas': skills_comprovadas,
        'skills_em_desenvolvimento': skills_em_desenvolvimento[:5],
        'total_skills': skills_comprovadas.count(),
    })
    return render(request, 'aluno/dashboard.html', context)

@aluno_logado_e_centros
def aluno_cursos(request):
    context = get_aluno_common_context(request)
    context['current_page'] = 'cursos'
    context['inscricoes_cursos'] = context['inscricoes_reais']
    context['cursos_videos_inscritos'] = request.aluno_obj.cursos_inscritos_video.all()
    return render(request, 'aluno/cursos.html', context)

@aluno_logado_e_centros
def aluno_favoritos(request):
    from cursovideoapp.models import FavoritoCursoVideo
    context = get_aluno_common_context(request)
    context['current_page'] = 'favoritos'
    
    favoritos_presencial = Favorito.objects.filter(aluno=request.aluno_obj).select_related('curso')
    favoritos_video = FavoritoCursoVideo.objects.filter(aluno=request.aluno_obj).select_related('curso')
    
    # Criar uma lista única de cursos para o template
    lista_unificada = []
    for f in favoritos_presencial:
        lista_unificada.append({'curso': f.curso, 'is_video': False})
    for f in favoritos_video:
        lista_unificada.append({'curso': f.curso, 'is_video': True})
        
    context['favoritos_lista'] = lista_unificada
    return render(request, 'aluno/favoritos.html', context)

@aluno_logado_e_centros
def aluno_depoimento(request):
    context = get_aluno_common_context(request)
    context['current_page'] = 'depoimento'
    context['meus_depoimentos'] = Depoimento.objects.filter(aluno=request.aluno_obj).order_by('-data')
    context['centros_inscritos'] = CentroDeFormacao.objects.filter(cursos__inscricoes__aluno=request.aluno_obj).distinct()
    return render(request, 'aluno/depoimento.html', context)

@aluno_logado_e_centros
def aluno_perfil(request):
    context = get_aluno_common_context(request)
    context['current_page'] = 'perfil'
    return render(request, 'aluno/perfil.html', context)

@aluno_logado_e_centros
def aluno_configuracoes(request):
    context = get_aluno_common_context(request)
    context['current_page'] = 'configuracoes'
    return render(request, 'aluno/settings.html', context)

@aluno_logado_e_centros
def enviar_depoimento(request):
    """
    Processa o envio de um novo depoimento pelo aluno.
    """
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        centro_id = request.POST.get('centro')
        texto = request.POST.get('texto')
        nota = request.POST.get('nota', 5)
        
        depoimento = Depoimento(
            aluno=request.aluno_obj,
            nome=request.aluno_obj.nome,
            tipo=tipo,
            texto=texto,
            nota=nota,
            aprovado=False
        )
        
        if tipo == 'CENTRO' and centro_id:
            try:
                depoimento.centro = CentroDeFormacao.objects.get(id=centro_id)
            except CentroDeFormacao.DoesNotExist:
                pass
        
        # Se o aluno tiver foto, usa no depoimento
        if request.perfil.foto_de_perfil:
            depoimento.foto = request.perfil.foto_de_perfil
            
        depoimento.save()
        messages.success(request, "Seu depoimento foi enviado com sucesso e está aguardando revisão!")
        return redirect('aluno_depoimento')
        
    return redirect('aluno_dashboard')



@csrf_exempt
def atualizar_localizacao(request):
    """
    View AJAX para atualizar a localização geográfica do aluno para buscas espaciais.
    """
    if request.method == "POST" and request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        data = json.loads(request.body)
        lat = data.get("lat")
        lng = data.get("lng")

        if lat and lng:
            # Garante que usamos getattr para evitar erro 'RelatedObjectDoesNotExist'
            aluno = getattr(request.user, 'aluno_profile', None)
            if not aluno:
                return JsonResponse({"status": "erro", "message": "Apenas alunos podem atualizar localização."}, status=403)
                
            perfil, created = PerfilAluno.objects.get_or_create(aluno=aluno)

            try:
                from django.contrib.gis.geos import Point
                perfil.localizacao = Point(float(lng), float(lat), srid=4326)
            except Exception:
                pass # Ignorar se GIS não estiver disponível
            
            perfil.save()
            return JsonResponse({"status": "sucesso"})
    return JsonResponse({"status": "erro"}, status=400)

        


def valida_cadastro_aluno(request):
    """
    Processa o formulário de registro de aluno. Cria Usuario e perfil de Aluno. E inicia a verificação de e-mail.
    """
    nome = request.POST.get('nome', '').strip()
    email = request.POST.get('email', '').strip()
    senha = request.POST.get('senha', '').strip()
    confirmar_senha = request.POST.get('confirmar_senha')
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if len(nome.strip()) == 0 or len(senha.strip()) == 0:
        if is_ajax: return JsonResponse({'success': False, 'error': 'Nome e senha são obrigatórios.'})
        return redirect('/auth/registro_aluno/?status=1')
    
    if len(senha) < 8:
        if is_ajax: return JsonResponse({'success': False, 'error': 'A senha deve ter pelo menos 8 caracteres.'})
        return redirect('/auth/registro_aluno/?status=2')
    
    if senha != confirmar_senha: 
        if is_ajax: return JsonResponse({'success': False, 'error': 'As senhas não coincidem.'})
        return redirect('/auth/registro_aluno/?status=5')
    
    usuario_existente = Usuario.objects.filter(email=email).first()
    
    if usuario_existente:
        # Se o usuário já existe mas está INATIVO (ex: criado via inscrição manual no centro)
        if not usuario_existente.is_active:
            usuario_existente.nome = nome
            usuario_existente.set_password(senha)
            usuario_existente.save()
            
            # Garante que o Aluno existe e atualiza o nome
            aluno, created = Aluno.objects.get_or_create(usuario=usuario_existente, defaults={'nome': nome, 'ativo': False})
            if not created:
                aluno.nome = nome
                aluno.save()
                
            usuario = usuario_existente
        else:
            if is_ajax: return JsonResponse({'success': False, 'error': 'Este e-mail já está registado e ativo na plataforma.'})
            return redirect('/auth/registro_aluno/?status=3')
    else:
        try:
            # Criar Usuario Novo
            usuario = Usuario.objects.create_user(
                email=email,
                nome=nome,
                password=senha,
                tipo_usuario='ALUNO'
            )
            usuario.is_active = False # Desativar até verificação de email
            usuario.save()
    
            # Criar perfil de Aluno
            aluno = Aluno.objects.create(
                usuario=usuario,
                nome=nome,
                ativo=False
            )
        except Exception as e:
            print(f"Erro ao cadastrar aluno: {e}")
            if is_ajax: return JsonResponse({'success': False, 'error': 'Erro no servidor. Tente novamente.'})
            return redirect('/auth/registro_aluno/?status=4')
            
    try:
        
        # Enviar código de verificação
        enviar_codigo_verificacao(email, 'CADASTRO')
        request.session['email_verificacao'] = email
        
        if is_ajax:
            return JsonResponse({'success': True, 'redirect': '/auth/verificar_email/'})
        return redirect('verificar_email')
    
    except Exception as e:
        print(f"Erro ao cadastrar aluno: {e}")
        if is_ajax: return JsonResponse({'success': False, 'error': 'Erro no servidor. Tente novamente.'})
        return redirect('/auth/registro_aluno/?status=4')
        
def enviar_email_confirmacao_aluno(nome, email):
    """
    Envia um email de boas-vindas após o registro bem-sucedido do aluno.
    """
    from core.email_utils import enviar_email_brevo
    
    assunto = "🎓 Bem-vindo ao EdukAngola, {}!".format(nome)
    contexto = {'nome': nome}
    html_content = render_to_string('bem_vindo.html', contexto)
    text_content = strip_tags(html_content)
    
    enviar_email_brevo(
        to_email=email,
        to_name=nome,
        subject=assunto,
        html_content=html_content,
        text_content=text_content
    )


def enviar_codigo_verificacao(email, tipo):
    """
    Função auxiliar para gerar e enviar códigos de verificação por e-mail.
    Usa Brevo HTTP API (porta 443) para evitar bloqueio SMTP no Render.
    """
    from core.email_utils import enviar_email_brevo
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    
    codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    CodigoVerificacao.objects.create(email=email, codigo=codigo, tipo=tipo)
    
    html_content = render_to_string('emails/codigo_verificacao.html', {'codigo': codigo})
    text_content = f"O seu código de verificação EdukAngola é: {codigo}\n\nEste código é válido por 10 minutos."
    
    enviado = enviar_email_brevo(
        to_email=email,
        subject="EdukAngola — Código de Verificação",
        html_content=html_content,
        text_content=text_content
    )
    if not enviado:
        raise RuntimeError('O serviço de e-mail não aceitou o envio do código.')
    return codigo



def verificar_email(request):
    """
    View para a etapa de verificação de e-mail usando o novo Portal de Verificação.
    """
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        email = request.session.get('email_verificacao')
        
        if not email:
            return redirect('/auth/login_aluno/')
            
        try:
            verificacao = CodigoVerificacao.objects.filter(email=email, codigo=codigo, tipo='CADASTRO').latest('criado_em')
            usuario = Usuario.objects.get(email=email)
            usuario.is_active = True
            usuario.save()
            
            try:
                aluno = Aluno.objects.get(usuario=usuario)
                aluno.ativo = True
                aluno.save()
            except Aluno.DoesNotExist:
                pass
            
            CodigoVerificacao.objects.filter(email=email).delete()
            if 'email_verificacao' in request.session:
                del request.session['email_verificacao']
            
            enviar_email_confirmacao_aluno(usuario.nome, usuario.email)
            return redirect('/auth/login_aluno/?status=0')
        except (CodigoVerificacao.DoesNotExist, Usuario.DoesNotExist):
            return render(request, 'core/verify_gate.html', {
                'error': _('O código introduzido é inválido ou já expirou. Por favor, tente novamente ou solicite um novo.'),
                'email_destino': email,
            })
            
    email = request.session.get('email_verificacao', '')
    return render(request, 'core/verify_gate.html', {'email_destino': email})

def reenviar_codigo(request):
    """
    View para reenviar o código de verificação para o e-mail na sessão.
    """
    email = request.session.get('email_verificacao')
    if not email:
        return redirect('/auth/login_aluno/')
    
    enviar_codigo_verificacao(email, 'CADASTRO')
    return render(request, 'core/verify_gate.html', {
        'message': _('Um novo código foi enviado com sucesso para o seu e-mail.'),
        'email_destino': email,
    })

def esqueci_senha(request):
    """
    Inicia o fluxo de 'Esqueci a Senha' enviando um código (Gate Premium).
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if Aluno.objects.filter(usuario__email=email).exists():
            enviar_codigo_verificacao(email, 'RECUPERACAO')
            request.session['email_recuperacao'] = email
            if is_ajax: return JsonResponse({'success': True, 'step': 2, 'message': 'Código enviado para o seu e-mail.'})
            return redirect('redefinir_senha')
        else:
            if is_ajax: return JsonResponse({'success': False, 'error': 'E-mail não encontrado.'})
            return render(request, 'core/forgot_password_gate.html', {'message': 'Se o email existir, um código foi enviado.'})
             
    return render(request, 'core/forgot_password_gate.html')

def redefinir_senha(request):
    """
    Valida o código de recuperação e permite definir uma nova senha (Reset Gate).
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()
        nova_senha = request.POST.get('senha', '').strip()
        confirmar_senha = request.POST.get('confirmar_senha', '').strip()
        email = request.session.get('email_recuperacao')
        
        if not email:
            if is_ajax: return JsonResponse({'success': False, 'error': 'Sessão expirada. Tente novamente.'})
            return redirect('esqueci_senha')
            
        if nova_senha != confirmar_senha:
            if is_ajax: return JsonResponse({'success': False, 'error': 'As senhas não coincidem.'})
            return render(request, 'core/reset_password_gate.html', {'error': 'Senhas não conferem'})
            
        try:
            verificacao = CodigoVerificacao.objects.filter(email=email, codigo=codigo, tipo='RECUPERACAO').latest('criado_em')
            usuario = Usuario.objects.get(email=email)
            usuario.set_password(nova_senha)
            usuario.save()
            
            CodigoVerificacao.objects.filter(email=email).delete()
            if 'email_recuperacao' in request.session:
                del request.session['email_recuperacao']
                
            if is_ajax: return JsonResponse({'success': True, 'message': 'Senha redefinida com sucesso!'})
            return redirect('/auth/login_aluno?status=senha_redefinida')
            
        except CodigoVerificacao.DoesNotExist:
            if is_ajax: return JsonResponse({'success': False, 'error': 'Código inválido.'})
            return render(request, 'core/reset_password_gate.html', {'error': 'Código inválido'})
            
    return render(request, 'core/reset_password_gate.html')

def valida_login(request):
    """
    Valida as credenciais do usuário usando o sistema de autenticação do Django.
    """
    email = request.POST.get('email', '').strip()
    senha = request.POST.get('senha', '').strip()
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if not email or not senha:
        if is_ajax: return JsonResponse({'success': False, 'error': 'Credenciais em falta.'})
        return redirect('/auth/login_aluno/?status=1')
    
    try:
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            if user.tipo_usuario != 'ALUNO':
                if is_ajax: return JsonResponse({'success': False, 'error': 'Apenas alunos podem aceder aqui.'})
                return redirect('/auth/login_aluno/?status=1') 
            
            if not user.is_active:
                if is_ajax: return JsonResponse({'success': False, 'error': 'Conta inativa. Verifique o seu e-mail.'})
                return redirect('/auth/login_aluno/?status=2')
                
            login(request, user)
            
            # Suporte ao parâmetro next
            next_url = request.POST.get('next') or request.GET.get('next') or '/auth/aluno/?status=0'
            
            if is_ajax: return JsonResponse({'success': True, 'redirect': next_url})
            return redirect(next_url)
        else:
            if is_ajax: return JsonResponse({'success': False, 'error': 'E-mail ou senha incorretos.'})
            return redirect('/auth/login_aluno/?status=1')
            
    except Exception as e:
        print(f"Erro no login: {e}")
        if is_ajax: return JsonResponse({'success': False, 'error': 'Erro interno. Tente novamente.'})
        return redirect('/auth/login_aluno?status=3')
        
#-----------------------------fim validacao aluno----------------------------------

# Empresa and Biblioteca views removed from here.
# Empresa views deleted.
# Biblioteca views moved to biblioteca/views.py

    
def login_instrutor(request):
    """
    Renderiza a página de login centralizada.
    """
    return render(request, 'login_instrutor.html')


def login_generico(request):
    """
    Login genérico para qualquer tipo de usuário (aluno, instrutor, representante de escola, etc).
    """
    if request.user.is_authenticated:
        return redirect('index')
    
    next_url = request.GET.get('next', '')
    context = {'next': next_url}
    
    return render(request, 'core/login_generico.html', context)


def valida_login_generico(request):
    """
    Valida as credenciais para login genérico (sem restrição de tipo de usuário).
    """
    email = request.POST.get('email', '').strip()
    senha = request.POST.get('senha', '').strip()
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if not email or not senha:
        if is_ajax: 
            return JsonResponse({'success': False, 'error': 'Email e senha são obrigatórios.'})
        messages.error(request, 'Email e senha são obrigatórios.')
        return redirect('login_generico')
    
    try:
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            if not user.is_active:
                if is_ajax: 
                    return JsonResponse({'success': False, 'error': 'Conta inativa. Verifique o seu e-mail.'})
                messages.error(request, 'Conta inativa. Verifique o seu e-mail.')
                return redirect('login_generico')
                
            login(request, user)
            
            # Suporte ao parâmetro next
            next_url = request.POST.get('next') or request.GET.get('next')
            
            # Se não houver redirect específico ou for um redirecionamento genérico à home, direciona por papel/perfil
            if not next_url or next_url in ['/', 'index', 'None', '']:
                from django.urls import reverse
                from escolas.models import RepresentanteEscola
                if RepresentanteEscola.objects.filter(user=user, ativo=True).exists():
                    next_url = reverse('escolas:dashboard_representante')
                elif user.tipo_usuario in ['GESTOR', 'GESTOR_FILIAL']:
                    next_url = reverse('centro_dashboard')
                elif user.tipo_usuario == 'ALUNO':
                    next_url = reverse('aluno')
                else:
                    next_url = reverse('index')
            
            if is_ajax: 
                return JsonResponse({'success': True, 'redirect': next_url})
            return redirect(next_url)
        else:
            if is_ajax: 
                return JsonResponse({'success': False, 'error': 'Email ou senha incorretos.'})
            messages.error(request, 'Email ou senha incorretos.')
            return redirect('login_generico')
            
    except Exception as e:
        print(f"Erro no login: {e}")
        if is_ajax: 
            return JsonResponse({'success': False, 'error': 'Erro interno. Tente novamente.'})
        messages.error(request, 'Erro interno. Tente novamente.')
        return redirect('login_generico')


def logout_usuario(request):
    """
    View de logout geral para todos os usuários.
    """
    auth_logout(request)
    return redirect('/')


@require_POST
def api_react_logout(request):
    auth_logout(request)
    return JsonResponse({'ok': True, 'message': 'Sessão terminada.'})
  
def tipo_user(request):
    """
    REMOVIDO: Página de seleção de tipo. Redireciona direto para o novo cadastro.
    """
    return redirect('registro_aluno')

def registro_aluno(request):
    """
    Renderiza o novo Portal de Cadastro (Register Gate).
    """
    status = request.GET.get('status')
    return render(request, 'core/register_gate.html', {'status': status})

def registro_instrutor(request):
    """
    Redireciona para o cadastro padrão (simplificação).
    """
    return redirect('registro_aluno')

def solicitacao_enviada(request):
    """
    Página de confirmação de que uma solicitação foi enviada.
    """
    pass 


from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render



def user_profile(request):
    """
    Exibe o perfil do aluno logado.
    """
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return redirect('/auth/login_aluno?status=4')  
    aluno = request.user.aluno_profile
    
    return render(request, 'user_profile.html', {'aluno': aluno})

def editar_perfil(request):
    """
    Lida com atualizações de perfil (nome, biografia, foto, etc.).
    """
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return redirect('/auth/login_aluno?status=4')
    
    aluno = request.user.aluno_profile
    perfil, created = PerfilAluno.objects.get_or_create(aluno=aluno)

    if request.method == 'POST':
        aluno.nome = request.POST.get('nome')
        perfil.telefone = request.POST.get('telefone')
        perfil.biografia = request.POST.get('biografia')
        perfil.linkedin = request.POST.get('linkedin')
        perfil.github = request.POST.get('github')

        if 'foto_de_perfil' in request.FILES:
            perfil.foto_de_perfil = request.FILES['foto_de_perfil']
            
        if 'foto_de_capa' in request.FILES:
            perfil.foto_de_capa = request.FILES['foto_de_capa']
            
        if 'bilhete_frente' in request.FILES:
            perfil.bilhete_frente = request.FILES['bilhete_frente']
            
        if 'bilhete_verso' in request.FILES:
            perfil.bilhete_verso = request.FILES['bilhete_verso']
        
        aluno.save()
        perfil.save()
        
        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect('aluno_perfil')
    
    return redirect('aluno_dashboard')

def configuracao_user(request):
    """
    Lida com as configurações do usuário enviadas via tabs.
    """
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return redirect('/auth/login_aluno')
    
    aluno = request.user.aluno_profile
    perfil, _ = PerfilAluno.objects.get_or_create(aluno=aluno)
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            aluno.nome = request.POST.get('nome')
            perfil.telefone = request.POST.get('telefone')
            perfil.biografia = request.POST.get('biografia')
            aluno.save()
            perfil.save()
            messages.success(request, "Perfil atualizado!")
            
        elif form_type == 'social':
            perfil.linkedin = request.POST.get('linkedin')
            perfil.github = request.POST.get('github')
            perfil.save()
            messages.success(request, "Redes sociais atualizadas!")
            
        elif form_type == 'password':
            current_password = request.POST.get('currentpassword')
            new_password = request.POST.get('newpassword')
            retype_new_password = request.POST.get('retypenewpassword')
            
            user = request.user
            if user.check_password(current_password):
                if new_password == retype_new_password:
                    if len(new_password) >= 8:
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)  # Mantém o usuário logado
                        messages.success(request, "Sua senha foi alterada com sucesso!")
                    else:
                        messages.error(request, "A nova senha deve ter pelo menos 8 caracteres.")
                else:
                    messages.error(request, "As novas senhas não coincidem.")
            else:
                messages.error(request, "A senha atual está incorreta.")
            
        return redirect('aluno_configuracoes')


@login_required
def aluno_onboarding(request):
    """
    View para o fluxo de onboarding do aluno.
    Coleta interesses, nível de conhecimento e completa o perfil inicial.
    """
    if request.user.tipo_usuario != 'ALUNO':
        return redirect('index')
    
    try:
        aluno = request.user.aluno_profile
        perfil = aluno.perfil
    except (AttributeError, PerfilAluno.DoesNotExist):
        # Fallback caso o perfil ainda não exista por algum motivo
        if hasattr(request.user, 'aluno_profile'):
            perfil = PerfilAluno.objects.create(aluno=request.user.aluno_profile)
        else:
            messages.error(request, "Perfil de aluno não encontrado.")
            return redirect('index')

    if request.method == 'POST':
        # 1. Processar Interesses
        categorias_ids = request.POST.getlist('interesses')
        if categorias_ids:
            perfil.interesses.set(Categoria.objects.filter(id__in=categorias_ids))
        
        # 2. Processar Nível de Conhecimento
        nivel = request.POST.get('nivel_conhecimento')
        if nivel in ['B', 'I', 'A']:
            perfil.nivel_conhecimento = nivel
        
        # 3. Processar Bio Opcional
        biografia = request.POST.get('biografia')
        if biografia:
            perfil.biografia = biografia
            
        # 4. Foto de Perfil Opcional
        if 'foto_perfil' in request.FILES:
            perfil.foto_de_perfil = request.FILES['foto_perfil']
            
        perfil.onboarding_completo = True
        perfil.save()
        
        messages.success(request, f"Bem-vindo, {aluno.nome}! Teu perfil foi personalizado.")
        return redirect('index')

    categorias = Categoria.objects.all()
    context = {
        'categorias': categorias,
        'perfil': perfil,
        'niveis': PerfilAluno.NIVEL_CONHECIMENTO_CHOICES,
    }
    return render(request, 'aluno/onboarding.html', context)

@login_required(login_url='/login_aluno/')
def baixar_ficha_inscricao(request, inscricao_id):
    import weasyprint
    from django.utils import timezone
    from django.http import HttpResponse
    
    aluno = get_object_or_404(Aluno, usuario=request.user)
    inscricao = get_object_or_404(Inscricao, id=inscricao_id, aluno=aluno)
    
    if inscricao.status != 'A':
        messages.error(request, "A ficha de inscrição só está disponível para inscrições pagas/aprovadas.")
        return redirect('aluno_cursos')
        
    context = {
        'inscricao': inscricao,
        'aluno': aluno,
        'curso': inscricao.curso,
        'centro': inscricao.curso.centro,
        'data_atual': timezone.now()
    }
    
    html_string = render_to_string('usuarios/ficha_inscricao_pdf.html', context)
    html = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Ficha_Inscricao_{inscricao.codigo_inscricao}.pdf"'
    return response

@require_GET
@login_required
def api_react_aluno_configuracoes(request):
    if getattr(request.user, 'tipo_usuario', None) != 'ALUNO':
        return JsonResponse({'detail': 'Inicie sessão como aluno para abrir as configurações.'}, status=401)
    aluno = getattr(request.user, 'aluno_profile', None)
    if not aluno:
        return JsonResponse({'detail': 'Perfil de aluno não encontrado.'}, status=404)
    preferencias, _ = PreferenciaNotificacaoAluno.objects.get_or_create(aluno=aluno)
    campos = ('receber_na_plataforma', 'receber_por_email', 'novos_cursos', 'novas_turmas', 'novos_livros', 'novos_eventos', 'atualizacoes_aprendizagem', 'calendario_e_feriados', 'resumo_semanal')
    return JsonResponse({
        'ok': True,
        'conta': {'nome': aluno.nome, 'email': request.user.email},
        'notificacoes': {campo: bool(getattr(preferencias, campo)) for campo in campos},
        'formador': _formador_estado(aluno),
    })


@require_POST
@login_required
def api_react_formador_enviar_codigo(request):
    aluno, erro = _aluno_api_autenticado(request)
    if erro:
        return erro
    if _cursos_video_concluidos(aluno) < 2:
        return JsonResponse({'detail': 'A candidatura de formador ainda não está disponível para esta conta.'}, status=403)
    candidatura = getattr(aluno, 'candidatura_formador', None)
    if candidatura and candidatura.estado in {'PENDENTE_ANALISE', 'APROVADA'}:
        return JsonResponse({'detail': 'Já existe uma candidatura em acompanhamento para esta conta.'}, status=409)
    CodigoVerificacao.objects.filter(email=request.user.email, tipo='FORMADOR').delete()
    try:
        enviar_codigo_verificacao(request.user.email, 'FORMADOR')
    except Exception:
        return JsonResponse({'detail': 'Não foi possível enviar o código. Tente novamente.'}, status=502)
    request.session['formador_codigo_email'] = request.user.email
    return JsonResponse({'ok': True, 'message': 'Enviámos um código de confirmação para o seu e-mail.'})


@require_POST
@login_required
def api_react_formador_candidatar(request):
    aluno, erro = _aluno_api_autenticado(request)
    if erro:
        return erro
    if _cursos_video_concluidos(aluno) < 2:
        return JsonResponse({'detail': 'A candidatura de formador ainda não está disponível para esta conta.'}, status=403)
    dados = _dados_json(request)
    codigo = str(dados.get('codigo') or '').strip()
    titulo = str(dados.get('titulo_profissional') or '').strip()
    area = str(dados.get('area_especializacao') or '').strip()
    biografia = str(dados.get('biografia') or '').strip()
    proposta = str(dados.get('proposta_curso') or '').strip()
    respostas = dados.get('respostas_teste') or {}
    if request.session.get('formador_codigo_email') != request.user.email:
        return JsonResponse({'detail': 'Peça um novo código de confirmação antes de continuar.'}, status=400)
    verificacao = CodigoVerificacao.objects.filter(
        email=request.user.email, codigo=codigo, tipo='FORMADOR', criado_em__gte=timezone.now() - timedelta(minutes=10)
    ).order_by('-criado_em').first()
    if not verificacao:
        return JsonResponse({'detail': 'O código é inválido ou expirou. Peça um novo código.'}, status=400)
    if not titulo or not area or len(biografia) < 40 or len(proposta) < 40:
        return JsonResponse({'detail': 'Preencha o título profissional, a área, a experiência e a proposta de curso.'}, status=400)
    areas_validas = {valor for valor, _ in CandidaturaFormador._meta.get_field('area_especializacao').choices}
    if area not in areas_validas:
        return JsonResponse({'detail': 'Seleccione uma área de especialização válida.'}, status=400)
    pontuacao = sum(1 for questao in _TESTE_FORMADOR if respostas.get(questao['id']) == questao['correta'])
    if pontuacao < 3:
        return JsonResponse({'detail': 'Ainda não atingiu a pontuação necessária no teste. Reveja as boas práticas e tente novamente.'}, status=400)
    candidatura, _ = CandidaturaFormador.objects.update_or_create(
        aluno=aluno,
        defaults={
            'titulo_profissional': titulo,
            'area_especializacao': area,
            'biografia': biografia,
            'proposta_curso': proposta,
            'teste_aprovado': True,
            'pontuacao_teste': pontuacao,
            'codigo_confirmado_em': timezone.now(),
            'estado': 'PENDENTE_ANALISE',
        },
    )
    CodigoVerificacao.objects.filter(email=request.user.email, tipo='FORMADOR').delete()
    request.session.pop('formador_codigo_email', None)
    return JsonResponse({'ok': True, 'estado': candidatura.estado, 'message': 'Recebemos a sua candidatura. A equipa Edukangola irá analisá-la.'}, status=201)


@require_GET
@login_required
def api_react_formador_teste(request):
    aluno, erro = _aluno_api_autenticado(request)
    if erro:
        return erro
    if _cursos_video_concluidos(aluno) < 2:
        return JsonResponse({'detail': 'A candidatura de formador ainda não está disponível para esta conta.'}, status=403)
    return JsonResponse({'ok': True, 'questoes': [{chave: valor for chave, valor in questao.items() if chave != 'correta'} for questao in _TESTE_FORMADOR]})


@require_POST
@login_required
def api_react_aluno_configuracoes_actualizar(request):
    if getattr(request.user, 'tipo_usuario', None) != 'ALUNO':
        return JsonResponse({'detail': 'Inicie sessão como aluno para guardar configurações.'}, status=401)
    aluno = getattr(request.user, 'aluno_profile', None)
    if not aluno:
        return JsonResponse({'detail': 'Perfil de aluno não encontrado.'}, status=404)
    dados = _dados_json(request)
    preferencias, _ = PreferenciaNotificacaoAluno.objects.get_or_create(aluno=aluno)
    campos = ('receber_na_plataforma', 'receber_por_email', 'novos_cursos', 'novas_turmas', 'novos_livros', 'novos_eventos', 'atualizacoes_aprendizagem', 'calendario_e_feriados', 'resumo_semanal')
    for campo in campos:
        if campo in dados:
            setattr(preferencias, campo, bool(dados[campo]))
    preferencias.save(update_fields=[*campos, 'atualizado_em'])
    return JsonResponse({'ok': True, 'message': 'Configurações guardadas.', 'notificacoes': {campo: bool(getattr(preferencias, campo)) for campo in campos}})
