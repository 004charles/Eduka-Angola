from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Usuario, Aluno, PerfilAluno, CodigoVerificacao
from gestoreduka.models import CentroDeFormacao, CentroSeguimento, Depoimento
from cursos_app.models import Curso, Favorito, Categoria, Inscricao
from bolsas.models import Bolsa, CandidaturaBolsa
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import IntegrityError, models
from django.core.exceptions import ValidationError
from hashlib import sha256
from .decorators import aluno_logado_e_centros
import random
import json



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
            'id': curso.id
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
        'inscricoes_com_progresso': inscricoes_com_progresso[:4], 
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
    
    if Usuario.objects.filter(email=email).exists():
        if is_ajax: return JsonResponse({'success': False, 'error': 'Este e-mail já está registado.'})
        return redirect('/auth/registro_aluno/?status=3')
    
    try:
        # Criar Usuario
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
    assunto = "Bem-vindo à Plataforma Edukangola!"
    
    # Contexto para o template
    contexto = {
        'nome': nome,
        'plataforma': 'Edukangola',
        'cor_primaria': '#333333',  # Cinza escuro
        'cor_secundaria': '#000000',  # Preto
    }
    
    # Renderizar o template HTML
    html_content = render_to_string('bem_vindo.html', contexto)
    text_content = strip_tags(html_content)  # Versão texto simples
    
    from django.conf import settings
    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    email_msg.attach_alternative(html_content, "text/html")
    

    try:
        email_msg.send()
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def enviar_codigo_verificacao(email, tipo):
    """
    Função auxiliar para gerar e enviar códigos de verificação por e-mail.
    """
    codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    CodigoVerificacao.objects.create(email=email, codigo=codigo, tipo=tipo)
    
    assunto = "Código de Verificação - Edukangola"
    mensagem = f"Seu código de verificação é: {codigo}"
    
    from django.conf import settings
    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=mensagem,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    try:
        email_msg.send()
    except Exception as e:
        print(f"Erro ao enviar código: {e}")

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
            return render(request, 'core/verify_gate.html', {'error': _('O código introduzido é inválido ou já expirou. Por favor, tente novamente ou solicite um novo.')})
            
    return render(request, 'core/verify_gate.html')

def reenviar_codigo(request):
    """
    View para reenviar o código de verificação para o e-mail na sessão.
    """
    email = request.session.get('email_verificacao')
    if not email:
        return redirect('/auth/login_aluno/')
    
    enviar_codigo_verificacao(email, 'CADASTRO')
    return render(request, 'core/verify_gate.html', {
        'message': _('Um novo código foi enviado com sucesso para o seu e-mail.')
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

def logout_usuario(request):
    """
    View de logout geral para todos os usuários.
    """
    auth_logout(request)
    return redirect('/')
  
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

from gestoreduka.models import Conversa, Mensagem

@aluno_logado_e_centros
def aluno_chat(request):
    """
    Renderiza a interface de chat para o aluno.
    """
    aluno = getattr(request.user, 'aluno_profile', None)
    if not aluno:
        return redirect('/auth/login_aluno')
        
    conversas = Conversa.objects.filter(aluno=aluno).order_by('-ultima_mensagem')
    
    conversa_id = request.GET.get('conversa_id')
    conversa_atual = None
    mensagens = []
    
    if conversa_id:
        try:
            conversa_atual = conversas.get(id=conversa_id)
            mensagens = conversa_atual.mensagens.all().order_by('data_envio')
        except Conversa.DoesNotExist:
            pass
            
    cursos_centro = []
    if conversa_atual:
        cursos_centro = conversa_atual.centro.cursos.filter(ativo=True, publicado=True).order_by('-destaque', '-data_criacao')[:6]
            
    return render(request, 'aluno_chat.html', {
        'aluno_logado': True,
        'aluno_nome': request.aluno_obj.nome if hasattr(request, 'aluno_obj') else aluno.nome,
        'perfil': getattr(request, 'perfil', None),
        'centros': getattr(request, 'centros', []),
        'conversas': conversas,
        'conversa_atual': conversa_atual,
        'mensagens': mensagens,
        'cursos_centro': cursos_centro,
    })

@login_required
def get_mensagens_aluno_ajax(request, conversa_id):
    """
    Retorna apenas o fragmento HTML das mensagens para o polling do portal do aluno.
    """
    aluno = getattr(request.user, 'aluno_profile', None)
    if not aluno:
        return JsonResponse({'error': 'Acesso negado'}, status=403)
        
    conversa = get_object_or_404(Conversa, id=conversa_id, aluno=aluno)
    mensagens = conversa.mensagens.all().order_by('data_envio')
    
    # NOVO: Carregar cursos para o catálogo inicial
    cursos_centro = conversa.centro.cursos.filter(ativo=True, publicado=True).order_by('-destaque', '-data_criacao')[:6]
    
    # Marcar mensagens recebidas do centro como lidas
    mensagens.filter(remetente_centro__isnull=False, lida=False).update(lida=True)
    
    return render(request, 'include/aluno_messages_fragment.html', {
        'mensagens': mensagens,
        'conversa_atual': conversa,
        'cursos_centro': cursos_centro,
    })

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
