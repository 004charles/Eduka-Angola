from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import ConviteCentro
from django.http import JsonResponse 


from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .models import CentroDeFormacao, ConviteCentro
import re

def centro_dashboard(request):
    # Verificar se o centro está logado na sessão
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar o dashboard.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        return render(request, 'centro_dashboard.html', {'centro': centro})
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import CentroDeFormacao, ConviteCentro
import re

def confirmar_cadastro(request, token):
    convite = get_object_or_404(ConviteCentro, token=token, usado=False)

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        senha = request.POST.get("senha", "").strip()
        confirm_senha = request.POST.get("confirm_senha", "").strip()

        # Validações completas
        errors = []

        # Validar nome
        if not nome:
            errors.append("O nome é obrigatório.")
        elif nome.isspace():
            errors.append("O nome não pode conter apenas espaços em branco.")
        elif len(nome) < 2:
            errors.append("O nome deve ter pelo menos 2 caracteres.")
        elif len(nome) > 100:
            errors.append("O nome deve ter no máximo 100 caracteres.")

        # Validar senha
        if not senha:
            errors.append("A senha é obrigatória.")
        elif senha.isspace():
            errors.append("A senha não pode conter apenas espaços em branco.")
        elif len(senha) < 8:
            errors.append("A senha deve ter pelo menos 8 caracteres.")
        elif len(senha) > 128:
            errors.append("A senha deve ter no máximo 128 caracteres.")
        else:
            # Verificar força da senha
            if not re.search(r'[A-Z]', senha):
                errors.append("A senha deve conter pelo menos uma letra maiúscula.")
            if not re.search(r'[a-z]', senha):
                errors.append("A senha deve conter pelo menos uma letra minúscula.")
            if not re.search(r'[0-9]', senha):
                errors.append("A senha deve conter pelo menos um número.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
                errors.append("A senha deve conter pelo menos um caractere especial.")

        # Validar confirmação de senha
        if not confirm_senha:
            errors.append("A confirmação de senha é obrigatória.")
        elif senha != confirm_senha:
            errors.append("As senhas não coincidem.")

        # Se houver erros, mostrar todos
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "confirmar_cadastro.html", {
                "convite": convite,
                "nome_value": nome,  # Manter valores preenchidos
                "senha_value": senha,
                "confirm_senha_value": confirm_senha
            })

        try:
            # Verificar se o centro ainda existe
            centro = convite.centro
            if not centro:
                messages.error(request, "Centro não encontrado.")
                return render(request, "confirmar_cadastro.html", {"convite": convite})

            # Atualizar o centro
            centro.nome = nome
            centro.senha_hash = make_password(senha)
            centro.ativo = True
            centro.save()

            # Marcar convite como usado
            convite.usado = True
            convite.save()

            messages.success(request, "Cadastro concluído com sucesso! Agora você pode fazer login com seu email e senha.")
            return redirect("login_gestor")

        except Exception as e:
            messages.error(request, f"Erro ao processar cadastro: {str(e)}")
            return render(request, "confirmar_cadastro.html", {
                "convite": convite,
                "nome_value": nome,
                "senha_value": senha,
                "confirm_senha_value": confirm_senha
            })

    # GET request - mostrar formulário vazio
    return render(request, "confirmar_cadastro.html", {"convite": convite})

    
def login_gestor(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "").strip()

        # Validações fortes
        if not email or email.isspace():
            messages.error(request, "O email não pode estar em branco.")
            return render(request, "login_gestor.html")

        if not senha or senha.isspace():
            messages.error(request, "A senha não pode estar em branco.")
            return render(request, "login_gestor.html")

        # Validar formato do email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messages.error(request, "Formato de email inválido.")
            return render(request, "login_gestor.html")

        try:
            # Buscar centro pelo email
            centro = CentroDeFormacao.objects.get(email=email, ativo=True)
            
            # Verificar se tem senha definida (já confirmou cadastro)
            if not hasattr(centro, 'senha_hash') or not centro.senha_hash:
                messages.error(request, "Complete seu cadastro primeiro. Verifique seu email.")
                return render(request, "login_gestor.html")
            
            # Verificar senha
            if check_password(senha, centro.senha_hash):
                # Login bem-sucedido - criar sessão
                request.session['centro_id'] = centro.id
                request.session['centro_nome'] = centro.nome
                request.session['centro_email'] = centro.email
                request.session['login_time'] = timezone.now().isoformat()
                
                messages.success(request, f"Bem-vindo, {centro.nome}!")
                return redirect("centro_dashboard")
            else:
                messages.error(request, "Senha inválida.")
                
        except CentroDeFormacao.DoesNotExist:
            messages.error(request, "Centro não encontrado ou inativo.")

    return render(request, "login_gestor.html")

def logout_gestor(request):
    # Limpar sessão
    session_keys = ['centro_id', 'centro_nome', 'centro_email', 'login_time']
    for key in session_keys:
        if key in request.session:
            del request.session[key]
    
    messages.success(request, "Logout realizado com sucesso!")
    return redirect('login_gestor')


def configuracao_gestor(request):
    return render(request, 'configuracao_gestor.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from .models import CentroDeFormacao, PerfilCentroDeFormacao, ConviteCentro
import os
import re

def configuracao_gestor(request):
    # Verificar se o centro está logado
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        perfil, created = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
        
        # Determinar tab ativa
        active_tab = request.GET.get('tab', 'details')
        
        context = {
            'centro': centro,
            'perfil': perfil,
            'active_tab': active_tab
        }
        return render(request, 'configuracao_gestor.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def atualizar_dados_pessoais(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            perfil, created = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
            
            # Dados básicos do centro
            centro.nome = request.POST.get('nome', centro.nome)
            centro.telefone = request.POST.get('telefone', centro.telefone)
            centro.endereco = request.POST.get('endereco', centro.endereco)
            centro.site = request.POST.get('site', centro.site)
            centro.save()
            
            # Dados do perfil
            perfil.dono = request.POST.get('dono', perfil.dono)
            perfil.descricao = request.POST.get('descricao', perfil.descricao)
            perfil.tipo = request.POST.get('tipo', perfil.tipo)
            perfil.modalidade = request.POST.get('modalidade', perfil.modalidade)
            
            # Upload de vídeo de apresentação
            if 'video_apresentacao' in request.FILES:
                # Remover vídeo antigo se existir
                if perfil.video_apresentacao:
                    if os.path.isfile(perfil.video_apresentacao.path):
                        os.remove(perfil.video_apresentacao.path)
                perfil.video_apresentacao = request.FILES['video_apresentacao']
            
            perfil.save()
            
            # Atualizar sessão se o nome mudou
            if centro.nome:
                request.session['centro_nome'] = centro.nome
            
            messages.success(request, 'Dados atualizados com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar dados: {str(e)}')
    
    return redirect(reverse('configuracao_gestor') + '?tab=details')

def atualizar_senha(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            senha_atual = request.POST.get('senha_atual', '').strip()
            nova_senha = request.POST.get('nova_senha', '').strip()
            confirmar_senha = request.POST.get('confirmar_senha', '').strip()
            
            # Validações
            if not senha_atual or not nova_senha or not confirmar_senha:
                messages.error(request, "Todos os campos são obrigatórios.")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            # Verificar senha atual
            if not centro.verificar_senha(senha_atual):
                messages.error(request, "Senha atual incorreta!")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            # Verificar se novas senhas coincidem
            if nova_senha != confirmar_senha:
                messages.error(request, "As novas senhas não coincidem!")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            # Validar força da nova senha
            if len(nova_senha) < 8:
                messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            # Atualizar senha
            centro.set_senha(nova_senha)
            centro.save()
            
            messages.success(request, 'Senha atualizada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar senha: {str(e)}')
    
    return redirect(reverse('configuracao_gestor') + '?tab=password')

def atualizar_redes_sociais(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            perfil = PerfilCentroDeFormacao.objects.get(centro=centro)
            
            perfil.facebook = request.POST.get('facebook', '')
            perfil.instagram = request.POST.get('instagram', '')
            perfil.whatsapp = request.POST.get('whatsapp', '')
            perfil.save()
            
            messages.success(request, 'Redes sociais atualizadas com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar redes sociais: {str(e)}')
    
    return redirect(reverse('configuracao_gestor') + '?tab=profile')

def upload_imagem_perfil(request):
    if request.method == 'POST' and request.FILES.get('imagem_perfil'):
        centro_id = request.session.get('centro_id')
        if not centro_id:
            return JsonResponse({'success': False, 'error': 'Sessão expirada'})
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            perfil, created = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
            
            # Remover imagem antiga se existir
            if perfil.imagem:
                if os.path.isfile(perfil.imagem.path):
                    os.remove(perfil.imagem.path)
            
            perfil.imagem = request.FILES['imagem_perfil']
            perfil.save()
            
            return JsonResponse({
                'success': True, 
                'url': perfil.imagem.url,
                'message': 'Imagem atualizada com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})

def upload_banner(request):
    if request.method == 'POST' and request.FILES.get('banner'):
        centro_id = request.session.get('centro_id')
        if not centro_id:
            return JsonResponse({'success': False, 'error': 'Sessão expirada'})
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            perfil, created = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
            
            # Remover banner antigo se existir
            if perfil.banner:
                if os.path.isfile(perfil.banner.path):
                    os.remove(perfil.banner.path)
            
            perfil.banner = request.FILES['banner']
            perfil.save()
            
            return JsonResponse({
                'success': True, 
                'url': perfil.banner.url,
                'message': 'Banner atualizado com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})





from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from cursos_app.models import Curso, Categoria, Instrutor
from .forms import CursoForm

def criar_curso(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para criar cursos.")
        return redirect('login_gestor')
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
    
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES, centro=centro)
        if form.is_valid():
            try:
                curso = form.save(commit=False)
                curso.centro = centro
                curso.save()
                form.save_m2m()  # Para salvar os instrutores (ManyToMany)
                
                messages.success(request, 'Curso criado com sucesso!')
                return redirect('listar_cursos')
            except Exception as e:
                messages.error(request, f'Erro ao criar curso: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CursoForm(centro=centro)
    
    context = {
        'form': form,
        'centro': centro,
        'categorias': Categoria.objects.all(),
        'instrutores': Instrutor.objects.filter(centro_de_formacao=centro, ativo=True)
    }
    return render(request, 'criar_curso.html', context)

def listar_cursos(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para ver seus cursos.")
        return redirect('login_gestor')
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
    cursos = Curso.objects.filter(centro=centro).order_by('-data_inicio')
    
    context = {
        'cursos': cursos,
        'centro': centro
    }
    return render(request, 'listar_cursos.html', context)

def editar_curso(request, curso_id):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para editar cursos.")
        return redirect('login_gestor')
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
    curso = get_object_or_404(Curso, id=curso_id, centro=centro)
    
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES, instance=curso, centro=centro)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Curso atualizado com sucesso!')
                return redirect('listar_cursos')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar curso: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CursoForm(instance=curso, centro=centro)
    
    context = {
        'form': form,
        'curso': curso,
        'centro': centro
    }
    return render(request, 'editar_curso.html', context)

def publicar_curso(request, curso_id):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        return JsonResponse({'success': False, 'error': 'Sessão expirada'})
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        curso = Curso.objects.get(id=curso_id, centro=centro)
        
        curso.publicado = True
        curso.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Curso publicado com sucesso!',
            'publicado': True
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def despublicar_curso(request, curso_id):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        return JsonResponse({'success': False, 'error': 'Sessão expirada'})
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        curso = Curso.objects.get(id=curso_id, centro=centro)
        
        curso.publicado = False
        curso.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Curso despublicado com sucesso!',
            'publicado': False
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def excluir_curso(request, curso_id):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        curso = Curso.objects.get(id=curso_id, centro=centro)
        curso.delete()
        
        messages.success(request, 'Curso excluído com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao excluir curso: {str(e)}')
    
    return redirect('listar_cursos')