from django.shortcuts import render
from django.http import HttpResponse
from .models import Usuario, Aluno, Empresa, Biblioteca, PerfilAluno
from django.shortcuts import redirect
from hashlib import sha256
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import logout as auth_logout
from django.db import IntegrityError  
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as auth_logout
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from hashlib import sha256
from django.db import IntegrityError
from .models import Biblioteca


def conta_aluno(request):
    return render(request, 'conta_aluno.html')

@require_POST
def adicionar_favorito(request, curso_id):
    if 'aluno' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Não autenticado'}, status=403)
    
    try:
        curso = Curso.objects.get(id=curso_id)
        aluno = Aluno.objects.get(id=request.session['aluno'])
        
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
    return render(request, 'login_aluno.html', {'status':status})

def aluno(request):
    if 'aluno' not in request.session:
        return redirect('/auth/Login_aluno?status=4')  
    
    try:
        aluno = Aluno.objects.get(id=request.session['aluno'])
        aluno = get_object_or_404(Aluno, id=request.session['aluno'])
        perfil, created = PerfilAluno.objects.get_or_create(aluno=aluno)
        return render(request, 'aluno.html', {'aluno_logado': True, 'aluno_nome': aluno.nome, 'perfil': perfil})
    except Aluno.DoesNotExist:
        return redirect('/auth/Login_aluno?status=4')
        
def Logout(request):
    print(">>> Logout view executada")

    try:
        if 'aluno' in request.session:
            del request.session['aluno']

        auth_logout(request)

        return HttpResponseRedirect('/auth/Login_aluno/?status=5')
    
    except Exception as e:
        print("Erro no logout:", e)
        return HttpResponseRedirect('/auth/Login_aluno/?status=erro')


def valida_cadastro_aluno(request):
    nome = request.POST.get('nome')
    email = request.POST.get('email')  
    senha = request.POST.get('senha')
    confirmar_senha = request.POST.get('confirmar_senha')
    
    aluno = Aluno.objects.filter(email=email)
    
    if len(nome.strip()) == 0 or len(senha.strip()) == 0:
        return redirect('/auth/registro_aluno?status=1')
    
    if len(senha) < 8:
        return redirect('/auth/registro_aluno?status=2')
    
    if senha != confirmar_senha: 
        return redirect('/auth/registro_aluno?status=5')
    
    if len(aluno) > 0:
        return redirect('/auth/registro_aluno?status=3')
    
    try:
        senha_hash = sha256(senha.encode()).hexdigest()
        aluno = Aluno(nome=nome, email=email, senha=senha_hash)
        aluno.save()
        
        # Enviar e-mail de boas-vindas
        enviar_email_boas_vindas(nome, email)
        
        return redirect('/auth/registro_aluno?status=0')
    
    except Exception as e:
        print(f"Erro ao cadastrar aluno: {e}")
        return redirect('/auth/registro_aluno?status=4')

def enviar_email_boas_vindas(nome, email):
    assunto = "Bem-vindo à Plataforma Educangola!"
    
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

def valida_login_aluno(request):
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    # Verifica se os campos estão vazios
    if not email or not senha:
        return redirect('/auth/Login_aluno?status=1')
    
    try:
        senha_hash = sha256(senha.encode()).hexdigest()
        aluno = Aluno.objects.get(email=email)
        
        # Verifica se a conta está ativa
        if not aluno.ativo:
            return redirect('/auth/Login_aluno?status=2')
            
        # Verifica a senha
        if aluno.senha != senha_hash:
            return redirect('/auth/Login_aluno?status=1')
            
        # Login bem-sucedido
        request.session['aluno'] = aluno.id
        return redirect('/auth/aluno?status=0')  # Status 0 para sucesso
        
    except Aluno.DoesNotExist:
        return redirect('/auth/Login_aluno?status=1')  # Email não existe
    except Exception as e:
        return redirect('/auth/Login_aluno?status=3')  # Erro interno
        
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

        # Validações básicas
        if not all([nome, email, senha, confirmar_senha, nif, ramo_atuacao, numero_funcionarios]):
            return redirect('/auth/registro_empresa?status=1')

        if len(senha) < 8:
            return redirect('/auth/registro_empresa?status=2')

        if senha != confirmar_senha:
            return redirect('/auth/registro_empresa?status=5')

        # Verifica se email ou NIF já existem
        if Empresa.objects.filter(email=email).exists():
            return redirect('/auth/registro_empresa?status=3')

        if Empresa.objects.filter(nif=nif).exists():
            return redirect('/auth/registro_empresa?status=6')

        # Cria a empresa
        senha_hash = sha256(senha.encode()).hexdigest()
        
        # Converter valores numéricos
        try:
            experiencia = int(experiencia_anos.split('-')[0]) if '-' in experiencia_anos else int(experiencia_anos)
            funcionarios = int(numero_funcionarios.split('-')[0]) if '-' in numero_funcionarios else int(numero_funcionarios)
        except (ValueError, AttributeError):
            experiencia = 0
            funcionarios = 1

        empresa = Empresa(
            nome=nome,
            email=email,
            senha=senha_hash,
            telefone=telefone,
            experiencia_anos=experiencia,
            nif=nif,
            ramo_atuacao=ramo_atuacao,
            numero_funcionarios=funcionarios
        )
        empresa.save()
        
        # Enviar e-mail de boas-vindas para empresa
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
        senha_hash = sha256(senha.encode()).hexdigest()
        empresa = Empresa.objects.get(email=email)
        
        if hasattr(empresa, 'ativo') and not empresa.ativo:
            return redirect('/auth/login_empresa?status=2')
            
        if empresa.senha != senha_hash:
            return redirect('/auth/login_empresa?status=1')
            
        request.session['empresa'] = empresa.id
        return redirect('/auth/conta_empresa?status=0')
        
    except Empresa.DoesNotExist:
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

        # Validações básicas
        if not all([nome, email, senha, confirmar_senha, tipo]):
            return redirect('/auth/Login_biblioteca?status=1')

        if len(senha) < 8:
            return redirect('/auth/Login_biblioteca?status=2')

        if senha != confirmar_senha:
            return redirect('/auth/Login_biblioteca?status=5')

        if Biblioteca.objects.filter(email=email).exists():
            return redirect('/auth/Login_biblioteca?status=3')

        if codigo_registro and Biblioteca.objects.filter(codigo_registro=codigo_registro).exists():
            return redirect('/auth/Login_biblioteca?status=7')

        senha_hash = sha256(senha.encode()).hexdigest()

        biblioteca = Biblioteca(
            nome=nome,
            email=email,
            senha=senha_hash,
            telefone=telefone,
            codigo_registro=codigo_registro if codigo_registro else None,
            tipo=tipo
        )
        biblioteca.save()

        enviar_email_boas_vindas_biblioteca(nome, email, tipo)

        return redirect('/auth/Login_biblioteca?status=0')
    
    except IntegrityError as e:
        print(f"Erro de integridade no cadastro: {e}")
        return redirect('/auth/Login_biblioteca?status=4')
    except ValueError as e:
        print(f"Erro de valor: {e}")
        return redirect('/auth/Login_biblioteca?status=4')
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
    
    # Verifica se os campos estão vazios
    if not email or not senha:
        return redirect('/auth/login_biblioteca?status=1')
    
    try:
        senha_hash = sha256(senha.encode()).hexdigest()
        biblioteca = Biblioteca.objects.get(email=email)
        
        # Verifica se a conta está ativa (adicionar campo 'ativo' no modelo se necessário)
        # if not biblioteca.ativo:
        #     return redirect('/auth/login_biblioteca?status=2')
            
        if biblioteca.senha != senha_hash:
            return redirect('/auth/login_biblioteca?status=1')
            
        request.session['biblioteca'] = biblioteca.id
        request.session['tipo_usuario'] = 'biblioteca'  
        return redirect('/auth/conta_biblioteca?status=10') 
    
    except Biblioteca.DoesNotExist:
        return redirect('/auth/login_biblioteca?status=1')  # Email não existe
    except Exception as e:
        print(f"Erro no login da biblioteca: {e}")
        return redirect('/auth/login_biblioteca?status=3')
        
def valida_login_biblioteca(request):
    pass

    
def Login_instrutor(request):
    return render(request, 'login_instrutor.html')

def Login_escola(request):
    return render(request, 'login_escola.html')

from django.shortcuts import redirect

def Logout(request):
    if 'aluno' in request.session:
        del request.session['aluno']
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