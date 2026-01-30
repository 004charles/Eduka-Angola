from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Usuario, Aluno, Empresa, Biblioteca, PerfilAluno, CentroSeguimento, CodigoVerificacao
from gestoreduka.models import CentroDeFormacao
from cursos_app.models import Curso
from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.views.decorators.http import require_POST
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
    return render(request, 'conta_aluno.html')

@require_POST
def adicionar_favorito(request, curso_id):
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

def Login_aluno(request):
    status = request.GET.get('status')
    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    return render(request, 'login_aluno.html', {'status':status, 'cursos_destaque':cursos_destaque})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from gestoreduka.models import CentroDeFormacao
from usuarios.models import Aluno, PerfilAluno

@aluno_logado_e_centros
def aluno(request):
    # Aqui você deve ter acesso aos atributos adicionados pelo decorator
    return render(request, 'aluno.html', {
        'aluno_logado': True,
        'aluno_nome': request.aluno_obj.nome,
        'perfil': request.perfil,
        'centros': request.centros,
    })

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.gis.geos import Point

@csrf_exempt
def atualizar_localizacao(request):
    if request.method == "POST" and request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        data = json.loads(request.body)
        lat = data.get("lat")
        lng = data.get("lng")

        if lat and lng:
            aluno = request.user.aluno_profile
            perfil, created = PerfilAluno.objects.get_or_create(aluno=aluno)
            perfil.localizacao = Point(float(lng), float(lat), srid=4326)
            perfil.save()
            return JsonResponse({"status": "sucesso"})
    return JsonResponse({"status": "erro"}, status=400)

        


def valida_cadastro_aluno(request):
    nome = request.POST.get('nome')
    email = request.POST.get('email')  
    senha = request.POST.get('senha')
    confirmar_senha = request.POST.get('confirmar_senha')
    
    if len(nome.strip()) == 0 or len(senha.strip()) == 0:
        return redirect('/auth/registro_aluno?status=1')
    
    if len(senha) < 8:
        return redirect('/auth/registro_aluno?status=2')
    
    if senha != confirmar_senha: 
        return redirect('/auth/registro_aluno?status=5')
    
    if Usuario.objects.filter(email=email).exists():
        return redirect('/auth/registro_aluno?status=3')
    
    try:
        # Create Usuario
        usuario = Usuario.objects.create_user(
            email=email,
            nome=nome,
            password=senha,
            tipo_usuario='ALUNO'
        )
        usuario.is_active = False # Deactivate until email verification
        usuario.save()

        # Create Aluno profile
        aluno = Aluno.objects.create(
            usuario=usuario,
            nome=nome,
            ativo=False
        )
        
        # Enviar código de verificação
        enviar_codigo_verificacao(email, 'CADASTRO')
        request.session['email_verificacao'] = email
        
        return redirect('verificar_email')
    
    except Exception as e:
        print(f"Erro ao cadastrar aluno: {e}")
        return redirect('/auth/registro_aluno?status=4')
        
def enviar_email_boas_vindas(nome, email):
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
    
    # Criar o e-mail
    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=text_content,
        from_email='nao-responda@educangola.com',
        to=[email],
    )
    email_msg.attach_alternative(html_content, "text/html")
    

    try:
        email_msg.send()
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def enviar_codigo_verificacao(email, tipo):
    codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    CodigoVerificacao.objects.create(email=email, codigo=codigo, tipo=tipo)
    
    assunto = "Código de Verificação - Edukangola"
    mensagem = f"Seu código de verificação é: {codigo}"
    
    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=mensagem,
        from_email='nao-responda@educangola.com',
        to=[email],
    )
    try:
        email_msg.send()
    except Exception as e:
        print(f"Erro ao enviar código: {e}")

def verificar_email(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        email = request.session.get('email_verificacao')
        
        if not email:
            return redirect('/auth/Login_aluno')
            
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
            enviar_email_boas_vindas(usuario.nome, usuario.email)
            
            return redirect('/auth/Login_aluno?status=0')
        except (CodigoVerificacao.DoesNotExist, Usuario.DoesNotExist):
            return render(request, 'verificar_codigo.html', {'error': 'Código inválido ou expirado'})
            
    return render(request, 'verificar_codigo.html')

def esqueci_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Aluno.objects.filter(email=email).exists():
            enviar_codigo_verificacao(email, 'RECUPERACAO')
            request.session['email_recuperacao'] = email
            return redirect('redefinir_senha')
        else:
             # Por segurança, não informamos se o email existe ou não, ou informamos msg generica
             return render(request, 'esqueci_senha.html', {'message': 'Se o email existir, um código foi enviado.'})
             
    return render(request, 'esqueci_senha.html')

def redefinir_senha(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nova_senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        email = request.session.get('email_recuperacao')
        
        if not email:
            return redirect('esqueci_senha')
            
        if nova_senha != confirmar_senha:
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
                
            return redirect('/auth/Login_aluno?status=senha_redefinida')
            
        except CodigoVerificacao.DoesNotExist:
            return render(request, 'redefinir_senha.html', {'error': 'Código inválido'})
            
    return render(request, 'redefinir_senha.html')

from django.contrib.auth import authenticate, login

def valida_login_aluno(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    if not email or not senha:
        return redirect('/auth/Login_aluno?status=1')
    
    try:
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            if user.tipo_usuario != 'ALUNO':
                return redirect('/auth/Login_aluno?status=1') # Or specific error for wrong account type
            
            if not user.is_active:
                return redirect('/auth/Login_aluno?status=2')
                
            login(request, user)
            return redirect('/auth/aluno?status=0')
        else:
            return redirect('/auth/Login_aluno?status=1')
            
    except Exception as e:
        print(f"Erro no login: {e}")
        return redirect('/auth/Login_aluno?status=3')
        
#-----------------------------fim validacao aluno----------------------------------

#-----------------------------validacao empresa----------------------------------
def Login_empresa(request):
    return render(request, 'login_empresa.html')

def valida_cadastro_empresa(request):
    if request.method != 'POST':
        return redirect('/auth/registro_empresa?status=6') 
    
    try:
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        telefone = request.POST.get('telefone')
        experiencia_anos = request.POST.get('experiencia_anos')
        nif = request.POST.get('nif')
        ramo_atuacao = request.POST.get('ramo_atuacao')
        numero_funcionarios = request.POST.get('numero_funcionarios')

        if not all([nome, email, senha, confirmar_senha, nif, ramo_atuacao, numero_funcionarios]):
            return redirect('/auth/registro_empresa?status=1')

        if len(senha) < 8:
            return redirect('/auth/registro_empresa?status=2')

        if senha != confirmar_senha:
            return redirect('/auth/registro_empresa?status=5')

        if Usuario.objects.filter(email=email).exists():
            return redirect('/auth/registro_empresa?status=3')

        if Empresa.objects.filter(nif=nif).exists():
            return redirect('/auth/registro_empresa?status=6')

        # Create Usuario
        usuario = Usuario.objects.create_user(
            email=email,
            nome=nome,
            password=senha,
            tipo_usuario='EMPRESA'
        )
        
        # Converter valores numéricos
        try:
            experiencia = int(experiencia_anos.split('-')[0]) if '-' in experiencia_anos else int(experiencia_anos)
            funcionarios = int(numero_funcionarios.split('-')[0]) if '-' in numero_funcionarios else int(numero_funcionarios)
        except (ValueError, AttributeError):
            experiencia = 0
            funcionarios = 1

        # Create Empresa profile
        empresa = Empresa.objects.create(
            usuario=usuario,
            nome=nome,
            telefone=telefone,
            experiencia_anos=experiencia,
            nif=nif,
            ramo_atuacao=ramo_atuacao,
            numero_funcionarios=funcionarios
        )
        
        enviar_email_boas_vindas_empresa(nome, email, ramo_atuacao)
        
        return redirect('/auth/registro_empresa?status=0')
    
    except Exception as e:
        print(f"Erro no cadastro da empresa: {e}")
        return redirect('/auth/registro_empresa?status=4')

def enviar_email_boas_vindas_empresa(nome, email, ramo_atuacao):
    assunto = f"Bem-vindo à EducAngola, {nome}!"
    
    # Contexto para o template
    contexto = {
        'nome': nome,
        'ramo': ramo_atuacao,
        'plataforma': 'EducAngola',
        'cor_primaria': '#333333',  # Cinza escuro
        'cor_secundaria': '#000000',  # Preto
    }
    
    # Renderizar o template HTML
    html_content = render_to_string('bem_vinda_empresa.html', contexto)
    text_content = strip_tags(html_content)  # Versão texto simples
    
    # Criar o e-mail
    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=text_content,
        from_email='parcerias@educangola.com',
        to=[email],
    )
    email_msg.attach_alternative(html_content, "text/html")
    
    try:
        email_msg.send()
    except Exception as e:
        print(f"Erro ao enviar e-mail para empresa: {e}")

def valida_login_empresa(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    if not email or not senha:
        return redirect('/auth/login_empresa?status=1')
    
    try:
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            if user.tipo_usuario != 'EMPRESA':
                return redirect('/auth/login_empresa?status=1')
            
            if not user.is_active:
                return redirect('/auth/login_empresa?status=2')
                
            login(request, user)
            return redirect('/auth/conta_empresa?status=0')
        else:
            return redirect('/auth/login_empresa?status=1')
            
    except Exception as e:
        print(f"Erro no login da empresa: {e}")
        return redirect('/auth/login_empresa?status=3')
    
    
def Login_biblioteca(request):
    return render(request, 'login_biblioteca.html')

def registro_biblioteca(request):
    return render(request, 'cadastro_biblioteca.html')


def valida_cadastro_biblioteca(request):
    if request.method != 'POST':
        return redirect('/auth/Login_biblioteca?status=6')
    
    try:
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        telefone = request.POST.get('telefone')
        codigo_registro = request.POST.get('codigo_registro', '').strip()
        tipo = request.POST.get('tipo')

        if not all([nome, email, senha, confirmar_senha, tipo]):
            return redirect('/auth/Login_biblioteca?status=1')

        if len(senha) < 8:
            return redirect('/auth/Login_biblioteca?status=2')

        if senha != confirmar_senha:
            return redirect('/auth/Login_biblioteca?status=5')

        if Usuario.objects.filter(email=email).exists():
            return redirect('/auth/Login_biblioteca?status=3')

        if codigo_registro and Biblioteca.objects.filter(codigo_registro=codigo_registro).exists():
            return redirect('/auth/Login_biblioteca?status=7')

        # Create Usuario
        usuario = Usuario.objects.create_user(
            email=email,
            nome=nome,
            password=senha,
            tipo_usuario='BIBLIOTECA'
        )

        # Create Biblioteca profile
        biblioteca = Biblioteca.objects.create(
            usuario=usuario,
            nome=nome,
            telefone=telefone,
            codigo_registro=codigo_registro if codigo_registro else None,
            tipo=tipo
        )

        enviar_email_boas_vindas_biblioteca(nome, email, tipo)

        return redirect('/auth/Login_biblioteca?status=0')
    
    except Exception as e:
        print(f"Erro inesperado no cadastro: {e}")
        return redirect('/auth/Login_biblioteca?status=4')


def enviar_email_boas_vindas_biblioteca(nome, email, tipo):
    assunto = f"Bem-vindo à EducAngola, {nome}!"
    
    # Mapear tipos de biblioteca para nomes mais amigáveis
    tipo_map = {
        'PUBLICA': 'Pública',
        'ESCOLAR': 'Escolar',
        'UNVERSITARIA': 'Universitária',
        'ESPECIALIZADA': 'Especializada',
        'COMUNITARIA': 'Comunitária'
    }
    tipo_display = tipo_map.get(tipo, tipo)
    
    # Contexto para o template
    contexto = {
        'nome': nome,
        'tipo': tipo_display,
        'plataforma': 'EducAngola',
        'cor_primaria': '#333333',
        'cor_secundaria': '#000000',
    }
    
    # Renderizar o template HTML
    html_content = render_to_string('boas_vindas_biblioteca.html', contexto)
    text_content = strip_tags(html_content)
    
    # Criar o e-mail
    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=text_content,
        from_email='bibliotecas@educangola.com',
        to=[email],
    )
    email_msg.attach_alternative(html_content, "text/html")
    
    try:
        email_msg.send()
    except Exception as e:
        print(f"Erro ao enviar e-mail para biblioteca: {e}")
        
        

def valida_login_biblioteca(request):
    if request.method != 'POST':
        return redirect('/auth/login_biblioteca?status=6')
    
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    if not email or not senha:
        return redirect('/auth/login_biblioteca?status=1')
    
    try:
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            if user.tipo_usuario != 'BIBLIOTECA':
                return redirect('/auth/login_biblioteca?status=1')
            
            if not user.is_active:
                return redirect('/auth/login_biblioteca?status=2')
                
            login(request, user)
            return redirect('/auth/conta_biblioteca?status=10')
        else:
            return redirect('/auth/login_biblioteca?status=1')
            
    except Exception as e:
        print(f"Erro no login da biblioteca: {e}")
        return redirect('/auth/login_biblioteca?status=3')

    
def Login_instrutor(request):
    return render(request, 'login_instrutor.html')

def Login_escola(request):
    return render(request, 'login_escola.html')

from django.shortcuts import redirect

def Logout(request):
    auth_logout(request)
    return redirect('/')
  

def tipo_user(request):
    status = request.POST.get('status')
    return render(request, 'logon.html', {'status':status})

def Registro_aluno(request):
    status = request.GET.get('status')
    return render(request, 'cadastro_aluno.html')

def Registro_empresa(request):
    return render(request, 'cadastro_empresa.html')

def Registro_instrutor(request):
    return render(request, 'cadastro_instrutor.html')

def Redefinir_senha(request):
    pass 

def Solicitacao_enviada(request):
    pass 


from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

def cadastro_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin:login')
    else:
        form = UserCreationForm()
    return render(request, 'admin/cadastro.html', {'form': form})


def seguir_centro(request, centro_id):
    # Verifica se o aluno está logado
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'status': 'erro', 'mensagem': 'É necessário estar logado para seguir um centro.'}, status=401)

    centro = get_object_or_404(CentroDeFormacao, id=centro_id)

    try:
        aluno = request.user.aluno_profile
    except Aluno.DoesNotExist:
        return JsonResponse({'status': 'erro', 'mensagem': 'Aluno não encontrado.'}, status=404)

    seguimento, criado = CentroSeguimento.objects.get_or_create(aluno=aluno, centro=centro)

    if criado:
        return JsonResponse({
            'status': 'sucesso',
            'mensagem': f"Agora você está seguindo o centro {centro.nome}."
        })
    else:
        return JsonResponse({
            'status': 'info',
            'mensagem': f"Você já segue o centro {centro.nome}."
        })


def user_profile(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return redirect('/auth/Login_aluno?status=4')  
    aluno = request.user.aluno_profile
    
    return render(request, 'user_profile.html', {'aluno': aluno})


from django.shortcuts import redirect
from django.contrib import messages

def editar_perfil(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return redirect('/auth/Login_aluno?status=4')
    
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
    return render(request, 'configuracao_user.html')