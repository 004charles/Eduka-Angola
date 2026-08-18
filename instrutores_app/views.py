from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
import json
from .forms import InstrutorSignupForm
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

def instrutor_signup(request):
    if request.method == 'POST':
        form = InstrutorSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cadastro realizado com sucesso! Aguarde a aprovação da administração para acessar sua conta.")
            return render(request, 'instrutores/signup_success.html')
    else:
        form = InstrutorSignupForm()
    return render(request, 'instrutores/signup.html', {'form': form})

def instrutor_login(request):
    if request.method == 'GET':
        return redirect('/formador')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.tipo_usuario == 'INSTRUTOR':
                if user.is_active:
                    login(request, user)
                    return redirect('/formador')
                else:
                    messages.error(request, "Sua conta ainda não foi ativada pela administração.")
            else:
                messages.error(request, "Esta conta não é de um instrutor.")
        else:
            messages.error(request, "E-mail ou senha incorretos.")
    else:
        form = AuthenticationForm()
    return render(request, 'instrutores/login.html', {'form': form})

from cursovideoapp.models import Curso_video, ComentarioAula, Aula
from cursos_app.models import Categoria, Instrutor
from django.db.models import Count, Sum

def get_instrutor(user):
    return getattr(user, 'instrutor_profile', None)


def _api_instrutor(request):
    if not request.user.is_authenticated:
        return None, JsonResponse({'detail': 'Inicie sessão como formador para continuar.'}, status=401)
    if getattr(request.user, 'tipo_usuario', None) != 'INSTRUTOR':
        return None, JsonResponse({'detail': 'Esta área é exclusiva para formadores.'}, status=403)
    instrutor = get_instrutor(request.user)
    if not instrutor or not instrutor.ativo:
        return None, JsonResponse({'detail': 'O perfil de formador não está disponível.'}, status=403)
    return instrutor, None


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except (AttributeError, UnicodeDecodeError, json.JSONDecodeError):
        return {}


@require_POST
def api_react_login(request):
    payload = _json_body(request)
    email = str(payload.get('email', '')).strip().lower()
    password = str(payload.get('password', ''))
    user = authenticate(request, username=email, password=password)
    if not user:
        return JsonResponse({'detail': 'E-mail ou palavra-passe incorrectos.'}, status=401)
    if user.tipo_usuario != 'INSTRUTOR':
        return JsonResponse({'detail': 'Esta conta não é de formador.'}, status=403)
    if not user.is_active or not get_instrutor(user) or not get_instrutor(user).ativo:
        return JsonResponse({'detail': 'A conta de formador ainda não está activa.'}, status=403)
    login(request, user)
    return JsonResponse({'ok': True})


@require_GET
def api_react_candidatura_opcoes(request):
    return JsonResponse({
        'ok': True,
        'areas': [{'valor': valor, 'nome': nome} for valor, nome in Instrutor.TIPO_CHOICES_ESPECIALIZACAO],
    })


@require_POST
def api_react_candidatura(request):
    form = InstrutorSignupForm(_json_body(request))
    if not form.is_valid():
        errors = {campo: [str(erro) for erro in erros] for campo, erros in form.errors.items()}
        return JsonResponse({
            'detail': 'Revise os dados da candidatura e tente novamente.',
            'errors': errors,
        }, status=400)
    instrutor = form.save()
    return JsonResponse({
        'ok': True,
        'instrutor': {'id': instrutor.id, 'nome': instrutor.nome},
        'message': 'Recebemos a sua candidatura. A equipa Edukangola vai analisar o perfil antes de activar o acesso.',
    }, status=201)


def _curso_payload(curso):
    return {
        'id': curso.id,
        'titulo': curso.titulo,
        'descricao': curso.descricao,
        'slug': curso.slug,
        'categoria': curso.categoria.nome if curso.categoria_id else 'Sem categoria',
        'categoria_id': curso.categoria_id,
        'capa_url': curso.get_imagem_url,
        'is_pago': curso.is_pago,
        'preco': float(curso.preco),
        'inscritos': curso.inscritos.count(),
        'aulas': curso.aulas.count(),
        'avaliacao_media': curso.get_media_avaliacoes,
        'destaque': curso.destaque,
    }


@require_GET
def api_react_dashboard(request):
    instrutor, error = _api_instrutor(request)
    if error:
        return error
    cursos = Curso_video.objects.filter(instrutor=instrutor).select_related('categoria').prefetch_related('inscritos', 'aulas').order_by('-data_publicacao')
    questoes = ComentarioAula.objects.filter(aula__curso__instrutor=instrutor, parent__isnull=True).select_related('aluno', 'aula__curso').prefetch_related('respostas').order_by('-data_criacao')[:30]
    return JsonResponse({
        'ok': True,
        'instrutor': {'id': instrutor.id, 'nome': instrutor.nome, 'titulo': instrutor.titulo or 'Formador', 'biografia': instrutor.biografia, 'foto_url': instrutor.foto.url if instrutor.foto else '', 'nota_media': float(instrutor.nota_media)},
        'metricas': {'cursos': cursos.count(), 'alunos': sum(curso.inscritos.count() for curso in cursos), 'aulas': sum(curso.aulas.count() for curso in cursos), 'duvidas_pendentes': sum(1 for questao in questoes if not questao.respostas.exists())},
        'cursos': [_curso_payload(curso) for curso in cursos],
        'categorias': [{'id': categoria.id, 'nome': categoria.nome} for categoria in Categoria.objects.order_by('nome')],
        'duvidas': [{'id': questao.id, 'texto': questao.texto, 'aluno': questao.aluno.nome if questao.aluno else 'Aluno', 'aula': questao.aula.titulo, 'curso': questao.aula.curso.titulo, 'criada_em': questao.data_criacao.isoformat(), 'respondida': questao.respostas.exists(), 'resolvida': questao.resolvida, 'respostas': [{'id': resposta.id, 'texto': resposta.texto, 'autor': resposta.instrutor.nome if resposta.instrutor else (resposta.aluno.nome if resposta.aluno else 'Equipa Edukangola'), 'criada_em': resposta.data_criacao.isoformat()} for resposta in questao.respostas.all()] } for questao in questoes],
    })


@require_POST
def api_react_criar_curso(request):
    instrutor, error = _api_instrutor(request)
    if error:
        return error
    payload = _json_body(request)
    titulo = str(payload.get('titulo', '')).strip()
    descricao = str(payload.get('descricao', '')).strip()
    categoria = Categoria.objects.filter(pk=payload.get('categoria_id')).first()
    if len(titulo) < 3 or len(descricao) < 20 or not categoria:
        return JsonResponse({'detail': 'Indique título, descrição com pelo menos 20 caracteres e categoria.'}, status=400)
    try:
        preco = max(0, float(payload.get('preco') or 0))
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'Indique um preço válido.'}, status=400)
    curso = Curso_video.objects.create(titulo=titulo, descricao=descricao, categoria=categoria, instrutor=instrutor, is_pago=bool(payload.get('is_pago')), preco=preco)
    return JsonResponse({'ok': True, 'curso': _curso_payload(curso)}, status=201)


@require_POST
def api_react_criar_aula(request, curso_id):
    instrutor, error = _api_instrutor(request)
    if error:
        return error
    curso = get_object_or_404(Curso_video, pk=curso_id, instrutor=instrutor)
    payload = _json_body(request)
    titulo = str(payload.get('titulo', '')).strip()
    video_url = str(payload.get('video_url', '')).strip()
    if len(titulo) < 3 or not video_url:
        return JsonResponse({'detail': 'Indique o título e a ligação de vídeo da aula.'}, status=400)
    ordem = (curso.aulas.order_by('-ordem').values_list('ordem', flat=True).first() or 0) + 1
    aula = Aula.objects.create(curso=curso, titulo=titulo, video_url=video_url, ordem=ordem, descricao=str(payload.get('descricao', '')).strip())
    return JsonResponse({'ok': True, 'aula': {'id': aula.id, 'titulo': aula.titulo, 'ordem': aula.ordem, 'video_url': aula.video_url}}, status=201)


@require_POST
def api_react_responder_duvida(request, duvida_id):
    instrutor, error = _api_instrutor(request)
    if error:
        return error
    duvida = get_object_or_404(ComentarioAula, pk=duvida_id, parent__isnull=True, aula__curso__instrutor=instrutor)
    texto = str(_json_body(request).get('texto', '')).strip()
    if not texto:
        return JsonResponse({'detail': 'Escreva uma resposta antes de enviar.'}, status=400)
    resposta = ComentarioAula.objects.create(instrutor=instrutor, aula=duvida.aula, texto=texto, parent=duvida)
    duvida.resolvida = True
    duvida.save(update_fields=['resolvida'])
    return JsonResponse({'ok': True, 'resposta': {'id': resposta.id, 'texto': resposta.texto, 'autor': instrutor.nome, 'criada_em': resposta.data_criacao.isoformat()}})

def instrutor_dashboard(request):
    return redirect('/formador')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    # Métricas Reais
    cursos = Curso_video.objects.filter(instrutor=instrutor)
    total_cursos = cursos.count()
    total_aulas = Aula.objects.filter(curso__in=cursos).count()
    
    # Calcular total de alunos únicos inscritos nos cursos deste instrutor
    # (Considerando que Curso_video tem uma relação com alunos via progresso ou inscrições)
    # Por enquanto vamos usar uma contagem simples de progresso
    from cursovideoapp.models import ProgressoAula
    total_alunos = ProgressoAula.objects.filter(aula__curso__in=cursos).values('aluno').distinct().count()

    # Calcular métricas educacionais
    from django.db.models import Avg
    
    # 1. Média de avaliações de todos os cursos
    todas_avaliacoes = [c.get_media_avaliacoes for c in cursos if c.get_media_avaliacoes > 0]
    nota_media_geral = round(sum(todas_avaliacoes) / len(todas_avaliacoes), 1) if todas_avaliacoes else 0.0
    
    # 2. Curso mais popular
    curso_pop = cursos.annotate(num_inscritos=Count('inscritos')).order_by('-num_inscritos').first()
    curso_popular = curso_pop.titulo if curso_pop else "Nenhum"

    questoes_pendentes = ComentarioAula.objects.filter(aula__curso__in=cursos, parent__isnull=True).order_by('-data_criacao')[:5]
    total_questoes = ComentarioAula.objects.filter(aula__curso__in=cursos, parent__isnull=True).count()

    context = {
        'instrutor': instrutor,
        'total_cursos': total_cursos,
        'total_aulas': total_aulas,
        'total_alunos': total_alunos,
        'nota_media_geral': nota_media_geral,
        'curso_popular': curso_popular,
        'questoes_recentes': questoes_pendentes,
        'total_questoes': total_questoes,
    }
    return render(request, 'instrutores/dashboard.html', context)

def listar_questoes(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    cursos = Curso_video.objects.filter(instrutor=instrutor)
    questoes = ComentarioAula.objects.filter(aula__curso__in=cursos, parent__isnull=True).order_by('-data_criacao')
    
    return render(request, 'instrutores/questoes.html', {'questoes': questoes})

def responder_questao(request, questao_id):
    if request.method == 'POST':
        questao = get_object_or_404(ComentarioAula, id=questao_id)
        instrutor = get_instrutor(request.user)
        
        texto = request.POST.get('resposta')
        if texto:
            ComentarioAula.objects.create(
                instrutor=instrutor,
                aula=questao.aula,
                texto=texto,
                parent=questao
            )
            messages.success(request, "Resposta enviada com sucesso!")
        
    return redirect('instrutores_app:listar_questoes')

from .forms import CursoVideoForm

def listar_cursos(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    cursos = Curso_video.objects.filter(instrutor=instrutor).order_by('-id')
    return render(request, 'instrutores/cursos.html', {'cursos': cursos})

def criar_curso(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado. Contacte o suporte.")
        return redirect('index')

    if request.method == 'POST':
        form = CursoVideoForm(request.POST, request.FILES)
        if form.is_valid():
            curso = form.save(commit=False)
            curso.instrutor = instrutor
            curso.save()
            messages.success(request, "Curso criado com sucesso! Agora adicione as aulas.")
            return redirect('instrutores_app:detalhe_curso', curso_id=curso.id)
    else:
        form = CursoVideoForm()
    
    return render(request, 'instrutores/form_curso.html', {'form': form, 'title': 'Criar Novo Curso'})

def editar_curso(request, curso_id):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    curso = get_object_or_404(Curso_video, id=curso_id, instrutor=instrutor)
    
    if request.method == 'POST':
        form = CursoVideoForm(request.POST, request.FILES, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, "Curso atualizado com sucesso!")
            return redirect('instrutores_app:listar_cursos')
    else:
        form = CursoVideoForm(instance=curso)
    
    return render(request, 'instrutores/form_curso.html', {'form': form, 'title': 'Editar Curso', 'curso': curso})

def detalhe_curso(request, curso_id):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    curso = get_object_or_404(Curso_video, id=curso_id, instrutor=instrutor)
    aulas = Aula.objects.filter(curso=curso).order_by('ordem')
    
    return render(request, 'instrutores/detalhe_curso.html', {'curso': curso, 'aulas': aulas})
from .forms import CursoVideoForm, AulaForm

def adicionar_aula(request, curso_id):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    curso = get_object_or_404(Curso_video, id=curso_id, instrutor=instrutor)
    
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            aula = form.save(commit=False)
            aula.curso = curso
            aula.save()
            messages.success(request, "Aula adicionada com sucesso!")
            return redirect('instrutores_app:detalhe_curso', curso_id=curso.id)
    else:
        # Sugerir a próxima ordem
        ultima_ordem = Aula.objects.filter(curso=curso).order_by('-ordem').first()
        proxima_ordem = (ultima_ordem.ordem + 1) if ultima_ordem else 1
        form = AulaForm(initial={'ordem': proxima_ordem})
    
    return render(request, 'instrutores/form_aula.html', {'form': form, 'curso': curso, 'title': 'Adicionar Aula'})

def editar_aula(request, aula_id):
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')
    
    aula = get_object_or_404(Aula, id=aula_id, curso__instrutor=instrutor)
    
    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            messages.success(request, "Aula atualizada com sucesso!")
            return redirect('instrutores_app:detalhe_curso', curso_id=aula.curso.id)
    else:
        form = AulaForm(instance=aula)
    
    return render(request, 'instrutores/form_aula.html', {'form': form, 'curso': aula.curso, 'title': 'Editar Aula'})

def remover_aula(request, aula_id):
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')
    
    aula = get_object_or_404(Aula, id=aula_id, curso__instrutor=instrutor)
    curso_id = aula.curso.id
    aula.delete()
    messages.success(request, "Aula removida com sucesso!")
    return redirect('instrutores_app:detalhe_curso', curso_id=curso_id)
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CursoVideoForm, AulaForm, InstrutorProfileForm, MaterialAulaForm, AvisoCursoForm, MaterialCursoForm
from cursovideoapp.models import MaterialAula, AvisoCurso, ProgressoAula, Exercicio, Questao, Alternativa, MaterialCurso
# from inteligencia.ai_utils import gerar_exercicios_ia

def listar_alunos(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    cursos = Curso_video.objects.filter(instrutor=instrutor)
    
    # Pegar todos os alunos únicos inscritos em qualquer curso deste instrutor
    from usuarios.models import Aluno
    alunos_ids = []
    for c in cursos:
        alunos_ids.extend(c.inscritos.values_list('id', flat=True))
    
    alunos = Aluno.objects.filter(id__in=set(alunos_ids)).order_by('nome')
    
    # Preparar dados de progresso por curso
    lista_alunos_data = []
    for aluno in alunos:
        dados_aluno = {
            'aluno': aluno,
            'cursos_inscritos': []
        }
        for curso in cursos:
            if curso.inscritos.filter(id=aluno.id).exists():
                total_aulas = curso.aulas.count()
                concluidas = ProgressoAula.objects.filter(aluno=aluno, aula__curso=curso, concluida=True).count()
                progresso = int((concluidas / total_aulas) * 100) if total_aulas > 0 else 0
                dados_aluno['cursos_inscritos'].append({
                    'curso': curso.titulo,
                    'progresso': progresso
                })
        lista_alunos_data.append(dados_aluno)

    return render(request, 'instrutores/alunos.html', {
        'alunos': lista_alunos_data,
        'cursos': cursos
    })

def enviar_aviso(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if request.method == 'POST':
        form = AvisoCursoForm(request.POST)
        curso_id = request.POST.get('curso_id')
        curso = get_object_or_404(Curso_video, id=curso_id, instrutor=instrutor)
        
        if form.is_valid():
            aviso = form.save(commit=False)
            aviso.curso = curso
            aviso.save()
            messages.success(request, f"Aviso enviado com sucesso para os alunos de '{curso.titulo}'!")
    
    return redirect('instrutores_app:listar_alunos')

def adicionar_material_curso(request, curso_id):
    instrutor = get_instrutor(request.user)
    curso = get_object_or_404(Curso_video, id=curso_id, instrutor=instrutor)
    if request.method == 'POST':
        form = MaterialCursoForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.curso = curso
            material.save()
            messages.success(request, "Material do curso adicionado com sucesso!")
    return redirect('instrutores_app:detalhe_curso', curso_id=curso.id)

def remover_material_curso(request, material_id):
    instrutor = get_instrutor(request.user)
    material = get_object_or_404(MaterialCurso, id=material_id, curso__instrutor=instrutor)
    curso_id = material.curso.id
    material.delete()
    messages.success(request, "Material do curso removido!")
    return redirect('instrutores_app:detalhe_curso', curso_id=curso_id)

def adicionar_material(request, aula_id):
    aula = get_object_or_404(Aula, id=aula_id, curso__instrutor=get_instrutor(request.user))
    if request.method == 'POST':
        form = MaterialAulaForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.aula = aula
            material.save()
            messages.success(request, "Material adicionado com sucesso!")
    return redirect('instrutores_app:editar_aula', aula_id=aula.id)

def remover_material(request, material_id):
    material = get_object_or_404(MaterialAula, id=material_id, aula__curso__instrutor=get_instrutor(request.user))
    aula_id = material.aula.id
    material.delete()
    messages.success(request, "Material removido com sucesso!")
    return redirect('instrutores_app:editar_aula', aula_id=aula_id)

def configuracoes(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')
    
    if request.method == 'POST':
        # Identificar qual formulário foi enviado
        if 'update_profile' in request.POST:
            profile_form = InstrutorProfileForm(request.POST, request.FILES, instance=instrutor)
            password_form = PasswordChangeForm(request.user)
            if profile_form.is_valid():
                profile_form.save()
                # Atualizar o nome no objeto Usuario também se mudou
                request.user.nome = profile_form.cleaned_data['nome']
                request.user.save()
                messages.success(request, "Perfil atualizado com sucesso!")
                return redirect('instrutores_app:configuracoes')
        
        elif 'change_password' in request.POST:
            profile_form = InstrutorProfileForm(instance=instrutor)
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Mantém o usuário logado
                messages.success(request, "Senha alterada com sucesso!")
                return redirect('instrutores_app:configuracoes')
    else:
        profile_form = InstrutorProfileForm(instance=instrutor)
        password_form = PasswordChangeForm(request.user)

    return render(request, 'instrutores/configuracoes.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'instrutor': instrutor
    })

def gerar_exercicio_aula(request, aula_id):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    aula = get_object_or_404(Aula, id=aula_id, curso__instrutor=instrutor)
    
    # Se a descrição estiver vazia, gera uma via IA primeiro
    if not aula.descricao or len(aula.descricao.strip()) < 10:
        from inteligencia.ai_utils import gerar_descricao_aula_ia
        descricao_ia = gerar_descricao_aula_ia(aula.titulo)
        if descricao_ia:
            aula.descricao = descricao_ia
            aula.save()

    # Gerar exercícios com IA
    resultado = gerar_exercicios_ia(aula.titulo, aula.descricao)
    
    # GERAR RESUMO IA TAMBÉM
    from inteligencia.ai_utils import gerar_resumo_ia
    resumo = gerar_resumo_ia(aula.titulo, aula.descricao)
    if not resumo.startswith("Erro:"):
        aula.resumo_ia = resumo
        aula.save()
    
    if "error" in resultado:
        messages.error(request, f"Erro ao gerar exercícios: {resultado['error']}")
    else:
        # Criar o Exercício
        exercicio, created = Exercicio.objects.get_or_create(aula=aula)
        
        # Remover questões antigas se houver
        if not created:
            exercicio.questoes.all().delete()
            
        # Criar Novas Questões
        for q_data in resultado.get('questoes', []):
            questao = Questao.objects.create(
                exercicio=exercicio,
                texto=q_data['texto'],
                explicacao=q_data.get('explicacao', '')
            )
            for a_data in q_data.get('alternativas', []):
                Alternativa.objects.create(
                    questao=questao,
                    texto=a_data['texto'],
                    is_correta=a_data['correta']
                )
        
        messages.success(request, f"Foram geradas {len(resultado.get('questoes', []))} questões para a aula '{aula.titulo}' com sucesso!")
    
    return redirect('instrutores_app:detalhe_curso', curso_id=aula.curso.id)

def gerenciar_exercicio(request, aula_id):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    aula = get_object_or_404(Aula, id=aula_id, curso__instrutor=instrutor)
    exercicio = get_object_or_404(Exercicio, aula=aula)
    
    if request.method == 'POST':
        # Lógica de salvamento manual
        for q in exercicio.questoes.all():
            q.texto = request.POST.get(f'q_{q.id}_texto')
            q.explicacao = request.POST.get(f'q_{q.id}_explicacao')
            q.save()
            
            for alt in q.alternativas.all():
                alt.texto = request.POST.get(f'alt_{alt.id}_texto')
                # A lógica de qual é correta vem de um radio button por questão
                alt.is_correta = (request.POST.get(f'q_{q.id}_correct') == str(alt.id))
                alt.save()
        
        messages.success(request, "Exercício atualizado manualmente com sucesso!")
        return redirect('instrutores_app:gerenciar_exercicio', aula_id=aula.id)

    return render(request, 'instrutores/gerenciar_exercicio.html', {
        'aula': aula,
        'exercicio': exercicio
    })

def gerar_exercicios_curso(request, curso_id):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
    if not instrutor:
        messages.error(request, "Perfil de instrutor não encontrado.")
        return redirect('index')

    curso = get_object_or_404(Curso_video, id=curso_id, instrutor=instrutor)
    aulas = Aula.objects.filter(curso=curso)
    
    from inteligencia.ai_utils import gerar_exercicios_ia, gerar_resumo_ia, gerar_descricao_aula_ia
    
    import time
    contador = 0
    for aula in aulas:
        # Pausa curta para evitar erro 429 de quota
        time.sleep(2)
        
        # 1. Gerar descrição se vazia
        if not aula.descricao or len(aula.descricao.strip()) < 10:
            descricao_ia = gerar_descricao_aula_ia(aula.titulo)
            if descricao_ia:
                aula.descricao = descricao_ia
                aula.save()
        
        # 2. Gerar exercícios (apenas se ainda não tiver)
        if not hasattr(aula, 'exercicio'):
            resultado = gerar_exercicios_ia(aula.titulo, aula.descricao)
            if "error" not in resultado:
                exercicio = Exercicio.objects.create(aula=aula)
                for q_data in resultado.get('questoes', []):
                    questao = Questao.objects.create(
                        exercicio=exercicio,
                        texto=q_data['texto'],
                        explicacao=q_data.get('explicacao', '')
                    )
                    for a_data in q_data.get('alternativas', []):
                        Alternativa.objects.create(
                            questao=questao,
                            texto=a_data['texto'],
                            is_correta=a_data['correta']
                        )
                contador += 1

        # 3. Gerar resumo se vazio
        if not aula.resumo_ia:
            resumo = gerar_resumo_ia(aula.titulo, aula.descricao)
            if resumo and not resumo.startswith("Erro:"):
                aula.resumo_ia = resumo
                aula.save()

    if contador > 0:
        messages.success(request, f"Sucesso! IA processou {contador} aulas novas com exercícios, resumos e descrições.")
    else:
        messages.info(request, "Todas as aulas já possuem conteúdo gerado ou foram atualizadas com novos resumos/descrições.")
        
    return redirect('instrutores_app:detalhe_curso', curso_id=curso.id)
