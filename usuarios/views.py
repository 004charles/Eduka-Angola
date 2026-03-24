from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Usuario, Aluno, Escola, PerfilAluno, CodigoVerificacao
from gestoreduka.models import CentroDeFormacao, CentroSeguimento
from cursos_app.models import Curso, Favorito
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import IntegrityError
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
    Renderiza a página de login do aluno com cursos em destaque.
    """
    status = request.GET.get('status')
    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    return render(request, 'login_aluno.html', {'status':status, 'cursos_destaque':cursos_destaque})



@aluno_logado_e_centros
def aluno(request):
    """
    Área principal do perfil do aluno. Os dados são enriquecidos pelo decorador aluno_logado_e_centros.
    """
    return render(request, 'aluno.html', {
        'aluno_logado': True,
        'aluno_nome': request.aluno_obj.nome,
        'perfil': request.perfil,
        'centros': request.centros,
    })



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
            aluno = request.user.aluno_profile
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
        return redirect('/auth/registro_aluno?status=1')
    
    if len(senha) < 8:
        if is_ajax: return JsonResponse({'success': False, 'error': 'A senha deve ter pelo menos 8 caracteres.'})
        return redirect('/auth/registro_aluno?status=2')
    
    if senha != confirmar_senha: 
        if is_ajax: return JsonResponse({'success': False, 'error': 'As senhas não coincidem.'})
        return redirect('/auth/registro_aluno?status=5')
    
    if Usuario.objects.filter(email=email).exists():
        if is_ajax: return JsonResponse({'success': False, 'error': 'Este e-mail já está registado.'})
        return redirect('/auth/registro_aluno?status=3')
    
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
            return JsonResponse({'success': True, 'redirect': '/auth/verificar_email'})
        return redirect('verificar_email')
    
    except Exception as e:
        print(f"Erro ao cadastrar aluno: {e}")
        if is_ajax: return JsonResponse({'success': False, 'error': 'Erro no servidor. Tente novamente.'})
        return redirect('/auth/registro_aluno?status=4')
        
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
    View para a etapa de verificação de e-mail usando o código de 6 dígitos.
    """
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        email = request.session.get('email_verificacao')
        
        if not email:
            return redirect('/auth/login_aluno')
            
        try:
            verificacao = CodigoVerificacao.objects.filter(email=email, codigo=codigo, tipo='CADASTRO').latest('criado_em')
            usuario = Usuario.objects.get(email=email)
            usuario.is_active = True
            usuario.save()
            
            # Update Aluno profile as well if it exists
            try:
                aluno = Aluno.objects.get(usuario=usuario)
                aluno.ativo = True
                aluno.save()
            except Aluno.DoesNotExist:
                pass
            
            # Limpar códigos
            CodigoVerificacao.objects.filter(email=email).delete()
            del request.session['email_verificacao']
            
            # Enviar boas vindas agora que ativou
            enviar_email_confirmacao_aluno(usuario.nome, usuario.email)
            
            return redirect('/auth/login_aluno?status=0')
        except (CodigoVerificacao.DoesNotExist, Usuario.DoesNotExist):
            return render(request, 'verificar_codigo.html', {'error': 'Código inválido ou expirado'})
            
    return render(request, 'verificar_codigo.html')

def esqueci_senha(request):
    """
    Inicia o fluxo de 'Esqueci a Senha' enviando um código.
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
            return render(request, 'esqueci_senha.html', {'message': 'Se o email existir, um código foi enviado.'})
             
    return render(request, 'esqueci_senha.html')

def redefinir_senha(request):
    """
    Valida o código de recuperação e permite definir uma nova senha.
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
            return render(request, 'redefinir_senha.html', {'error': 'Senhas não conferem'})
            
        try:
            verificacao = CodigoVerificacao.objects.filter(email=email, codigo=codigo, tipo='RECUPERACAO').latest('criado_em')
            
            # Atualizar senha
            usuario = Usuario.objects.get(email=email)
            usuario.set_password(nova_senha)
            usuario.save()
            
            # Limpar
            CodigoVerificacao.objects.filter(email=email).delete()
            if 'email_recuperacao' in request.session:
                del request.session['email_recuperacao']
                
            if is_ajax: return JsonResponse({'success': True, 'message': 'Senha redefinida com sucesso!'})
            return redirect('/auth/login_aluno?status=senha_redefinida')
            
        except CodigoVerificacao.DoesNotExist:
            if is_ajax: return JsonResponse({'success': False, 'error': 'Código inválido.'})
            return render(request, 'redefinir_senha.html', {'error': 'Código inválido'})
            
    return render(request, 'redefinir_senha.html')

from django.contrib.auth import authenticate, login

def valida_login(request):
    """
    Valida as credenciais do usuário usando o sistema de autenticação do Django.
    """
    email = request.POST.get('email', '').strip()
    senha = request.POST.get('senha', '').strip()
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if not email or not senha:
        if is_ajax: return JsonResponse({'success': False, 'error': 'Credenciais em falta.'})
        return redirect('/auth/login_aluno?status=1')
    
    try:
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            if user.tipo_usuario != 'ALUNO':
                if is_ajax: return JsonResponse({'success': False, 'error': 'Apenas alunos podem aceder aqui.'})
                return redirect('/auth/login_aluno?status=1') 
            
            if not user.is_active:
                if is_ajax: return JsonResponse({'success': False, 'error': 'Conta inativa. Verifique o seu e-mail.'})
                return redirect('/auth/login_aluno?status=2')
                
            login(request, user)
            if is_ajax: return JsonResponse({'success': True, 'redirect': '/auth/aluno?status=0'})
            return redirect('/auth/aluno?status=0')
        else:
            if is_ajax: return JsonResponse({'success': False, 'error': 'E-mail ou senha incorretos.'})
            return redirect('/auth/login_aluno?status=1')
            
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

def login_escola(request):
    """
    Renderiza a página de login da escola.
    """
    return render(request, 'login_escola.html')

def logout_usuario(request):
    """
    View de logout geral para todos os usuários.
    """
    auth_logout(request)
    return redirect('/')
  
def tipo_user(request):
    """
    Página de seleção do tipo de conta antes do registro.
    """
    status = request.POST.get('status')
    return render(request, 'logon.html', {'status':status})

def registro_aluno(request):
    """
    Renderiza a página de registro para novos alunos.
    """
    status = request.GET.get('status')
    return render(request, 'cadastro_aluno.html')

def registro_instrutor(request):
    """
    Renderiza a página de registro de instrutores.
    """
    return render(request, 'cadastro_instrutor.html')

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
        
        aluno.save()
        perfil.save()
        
        messages.success(request, "Perfil atualizado com sucesso!")
        return redirect('/auth/aluno')  

    return redirect('/auth/aluno')

def configuracao_user(request):
    """
    Página de configuração geral para o usuário.
    """
    return render(request, 'configuracao_user.html')

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
            
    return render(request, 'aluno_chat.html', {
        'aluno_logado': True,
        'aluno_nome': request.aluno_obj.nome if hasattr(request, 'aluno_obj') else aluno.nome,
        'perfil': getattr(request, 'perfil', None),
        'centros': getattr(request, 'centros', []),
        'conversas': conversas,
        'conversa_atual': conversa_atual,
        'mensagens': mensagens,
    })