from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ConviteCentro
from django.http import JsonResponse 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from cursos_app.models import Curso, Categoria, Instrutor
from .forms import CursoForm
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from .models import CentroDeFormacao, ConviteCentro
import re
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import CentroDeFormacao, ConviteCentro
import re
from .models import CentroDeFormacao, Conversa, Mensagem
from usuarios.models import Aluno
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
import os
from datetime import datetime
from .models import (
    CentroDeFormacao, PerfilCentroDeFormacao, Certificacao, 
    Diferencial, AreaFormacao, Equipe, Recurso, Depoimento,
    Estatistica, Parceria, Evento, GaleriaImagem, ReelCentro,
    Filial
)

def centro_dashboard(request):
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
            'active_tab': active_tab,
            'latitude': centro.latitude,
            'longitude': centro.longitude,
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
            centro.cidade = request.POST.get('cidade', centro.cidade)
            centro.provincia = request.POST.get('provincia', centro.provincia)
            
            # Processar localização geográfica
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if latitude and longitude:
                try:
                    lat_float = float(latitude)
                    lng_float = float(longitude)
                    
                    # Validar coordenadas (Angola está aproximadamente entre -18 e -4 de latitude e 11 e 24 de longitude)
                    if -18 <= lat_float <= -4 and 11 <= lng_float <= 24:
                        centro.set_localizacao(lat_float, lng_float)
                    else:
                        messages.warning(request, "Coordenadas fora do território de Angola. Verifique os valores.")
                        
                except (ValueError, TypeError):
                    messages.warning(request, "Coordenadas inválidas. Use números decimais.")
            else:
                # Se ambos os campos estiverem vazios, limpa a localização
                centro.localizacao = None
            
            centro.save()
            
            # Dados do perfil
            perfil.dono = request.POST.get('dono', perfil.dono)
            perfil.descricao = request.POST.get('descricao', perfil.descricao)
            perfil.tipo = request.POST.get('tipo', perfil.tipo)
            perfil.modalidade = request.POST.get('modalidade', perfil.modalidade)
            
            if 'video_apresentacao' in request.FILES:
                if perfil.video_apresentacao:
                    if os.path.isfile(perfil.video_apresentacao.path):
                        os.remove(perfil.video_apresentacao.path)
                perfil.video_apresentacao = request.FILES['video_apresentacao']
            
            perfil.save()
            
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
            
            if not senha_atual or not nova_senha or not confirmar_senha:
                messages.error(request, "Todos os campos são obrigatórios.")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            if not centro.verificar_senha(senha_atual):
                messages.error(request, "Senha atual incorreta!")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            if nova_senha != confirmar_senha:
                messages.error(request, "As novas senhas não coincidem!")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            if len(nova_senha) < 8:
                messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
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



def diferenciais_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        diferenciais = centro.diferenciais.all()
        
        context = {
            'centro': centro,
            'diferenciais': diferenciais,
            'active_tab': 'diferentials'
        }
        return render(request, 'gestor/diferenciais.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_diferencial(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            Diferencial.objects.create(
                centro=centro,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao'),
                icone=request.POST.get('icone', 'feather-check')
            )
            
            messages.success(request, 'Diferencial adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar diferencial: {str(e)}')
    
    return redirect('diferenciais_gestor')

def editar_diferencial(request, diferencial_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            diferencial = Diferencial.objects.get(
                id=diferencial_id, 
                centro_id=centro_id
            )
            
            diferencial.titulo = request.POST.get('titulo', diferencial.titulo)
            diferencial.descricao = request.POST.get('descricao', diferencial.descricao)
            diferencial.icone = request.POST.get('icone', diferencial.icone)
            diferencial.save()
            
            messages.success(request, 'Diferencial atualizado com sucesso!')
            
        except Diferencial.DoesNotExist:
            messages.error(request, "Diferencial não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar diferencial: {str(e)}')
    
    return redirect('diferenciais_gestor')

def excluir_diferencial(request, diferencial_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            diferencial = Diferencial.objects.get(
                id=diferencial_id, 
                centro_id=centro_id
            )
            diferencial.delete()
            messages.success(request, 'Diferencial excluído com sucesso!')
            
        except Diferencial.DoesNotExist:
            messages.error(request, "Diferencial não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir diferencial: {str(e)}')
    
    return redirect('diferenciais_gestor')


def equipe_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        equipe = centro.equipe.all()
        
        context = {
            'centro': centro,
            'equipe': equipe,
            'active_tab': 'team'
        }
        return render(request, 'gestor/equipe.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_membro_equipe(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            membro = Equipe(
                centro=centro,
                nome=request.POST.get('nome'),
                cargo=request.POST.get('cargo'),
                biografia=request.POST.get('biografia', ''),
                formacao=request.POST.get('formacao', ''),
                experiencia=request.POST.get('experiencia', ''),
                linkedin=request.POST.get('linkedin', ''),
                email=request.POST.get('email', ''),
                ordem=request.POST.get('ordem', 0)
            )
            
            if 'foto' in request.FILES:
                membro.foto = request.FILES['foto']
            
            membro.save()
            messages.success(request, 'Membro da equipe adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar membro: {str(e)}')
    
    return redirect('equipe_gestor')

def editar_membro_equipe(request, membro_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            membro = Equipe.objects.get(
                id=membro_id, 
                centro_id=centro_id
            )
            
            membro.nome = request.POST.get('nome', membro.nome)
            membro.cargo = request.POST.get('cargo', membro.cargo)
            membro.biografia = request.POST.get('biografia', membro.biografia)
            membro.formacao = request.POST.get('formacao', membro.formacao)
            membro.experiencia = request.POST.get('experiencia', membro.experiencia)
            membro.linkedin = request.POST.get('linkedin', membro.linkedin)
            membro.email = request.POST.get('email', membro.email)
            membro.ordem = request.POST.get('ordem', membro.ordem)
            
            if 'foto' in request.FILES:
                if membro.foto:
                    if os.path.isfile(membro.foto.path):
                        os.remove(membro.foto.path)
                membro.foto = request.FILES['foto']
            
            membro.save()
            messages.success(request, 'Membro da equipe atualizado com sucesso!')
            
        except Equipe.DoesNotExist:
            messages.error(request, "Membro não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar membro: {str(e)}')
    
    return redirect('equipe_gestor')

def excluir_membro_equipe(request, membro_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            membro = Equipe.objects.get(
                id=membro_id, 
                centro_id=centro_id
            )
            
            if membro.foto and os.path.isfile(membro.foto.path):
                os.remove(membro.foto.path)
            
            membro.delete()
            messages.success(request, 'Membro da equipe excluído com sucesso!')
            
        except Equipe.DoesNotExist:
            messages.error(request, "Membro não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir membro: {str(e)}')
    
    return redirect('equipe_gestor')



def depoimentos_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        depoimentos = centro.depoimentos.all()
        
        context = {
            'centro': centro,
            'depoimentos': depoimentos,
            'active_tab': 'testimonials'
        }
        return render(request, 'gestor/depoimentos.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_depoimento(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            depoimento = Depoimento(
                centro=centro,
                nome=request.POST.get('nome'),
                cargo=request.POST.get('cargo', ''),
                texto=request.POST.get('texto'),
                nota=int(request.POST.get('nota', 5)),
                aprovado=True  # Aprova automaticamente quando adicionado pelo gestor
            )
            
            if 'foto' in request.FILES:
                depoimento.foto = request.FILES['foto']
            
            depoimento.save()
            messages.success(request, 'Depoimento adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar depoimento: {str(e)}')
    
    return redirect('depoimentos_gestor')

def toggle_aprovacao_depoimento(request, depoimento_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            depoimento = Depoimento.objects.get(
                id=depoimento_id, 
                centro_id=centro_id
            )
            depoimento.aprovado = not depoimento.aprovado
            depoimento.save()
            
            status = "aprovado" if depoimento.aprovado else "reprovado"
            messages.success(request, f'Depoimento {status} com sucesso!')
            
        except Depoimento.DoesNotExist:
            messages.error(request, "Depoimento não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar status: {str(e)}')
    
    return redirect('depoimentos_gestor')

def excluir_depoimento(request, depoimento_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            depoimento = Depoimento.objects.get(
                id=depoimento_id, 
                centro_id=centro_id
            )
            
            if depoimento.foto and os.path.isfile(depoimento.foto.path):
                os.remove(depoimento.foto.path)
            
            depoimento.delete()
            messages.success(request, 'Depoimento excluído com sucesso!')
            
        except Depoimento.DoesNotExist:
            messages.error(request, "Depoimento não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir depoimento: {str(e)}')
    
    return redirect('depoimentos_gestor')



def estatisticas_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        estatisticas = centro.estatisticas.all()
        
        context = {
            'centro': centro,
            'estatisticas': estatisticas,
            'active_tab': 'statistics'
        }
        return render(request, 'gestor/estatisticas.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_estatistica(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            Estatistica.objects.create(
                centro=centro,
                titulo=request.POST.get('titulo'),
                valor=request.POST.get('valor'),
                icone=request.POST.get('icone', 'feather-users'),
                ordem=request.POST.get('ordem', 0)
            )
            
            messages.success(request, 'Estatística adicionada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar estatística: {str(e)}')
    
    return redirect('estatisticas_gestor')

def editar_estatistica(request, estatistica_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            estatistica = Estatistica.objects.get(
                id=estatistica_id, 
                centro_id=centro_id
            )
            
            estatistica.titulo = request.POST.get('titulo', estatistica.titulo)
            estatistica.valor = request.POST.get('valor', estatistica.valor)
            estatistica.icone = request.POST.get('icone', estatistica.icone)
            estatistica.ordem = request.POST.get('ordem', estatistica.ordem)
            estatistica.save()
            
            messages.success(request, 'Estatística atualizada com sucesso!')
            
        except Estatistica.DoesNotExist:
            messages.error(request, "Estatística não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar estatística: {str(e)}')
    
    return redirect('estatisticas_gestor')

def excluir_estatistica(request, estatistica_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            estatistica = Estatistica.objects.get(
                id=estatistica_id, 
                centro_id=centro_id
            )
            estatistica.delete()
            messages.success(request, 'Estatística excluída com sucesso!')
            
        except Estatistica.DoesNotExist:
            messages.error(request, "Estatística não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir estatística: {str(e)}')
    
    return redirect('estatisticas_gestor')



def parcerias_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        parcerias = centro.parcerias.all()
        
        context = {
            'centro': centro,
            'parcerias': parcerias,
            'active_tab': 'partnerships'
        }
        return render(request, 'gestor/parcerias.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_parceria(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            parceria = Parceria(
                centro=centro,
                nome_empresa=request.POST.get('nome_empresa'),
                tipo_parceria=request.POST.get('tipo_parceria'),
                website=request.POST.get('website', '')
            )
            
            if 'logo' in request.FILES:
                parceria.logo = request.FILES['logo']
            
            parceria.save()
            messages.success(request, 'Parceria adicionada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar parceria: {str(e)}')
    
    return redirect('parcerias_gestor')

def toggle_parceria(request, parceria_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            parceria = Parceria.objects.get(
                id=parceria_id, 
                centro_id=centro_id
            )
            parceria.ativa = not parceria.ativa
            parceria.save()
            
            status = "ativada" if parceria.ativa else "desativada"
            messages.success(request, f'Parceria {status} com sucesso!')
            
        except Parceria.DoesNotExist:
            messages.error(request, "Parceria não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar status: {str(e)}')
    
    return redirect('parcerias_gestor')

def excluir_parceria(request, parceria_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            parceria = Parceria.objects.get(
                id=parceria_id, 
                centro_id=centro_id
            )
            
            if parceria.logo and os.path.isfile(parceria.logo.path):
                os.remove(parceria.logo.path)
            
            parceria.delete()
            messages.success(request, 'Parceria excluída com sucesso!')
            
        except Parceria.DoesNotExist:
            messages.error(request, "Parceria não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir parceria: {str(e)}')
    
    return redirect('parcerias_gestor')



def eventos_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        eventos = centro.eventos.all()
        
        context = {
            'centro': centro,
            'eventos': eventos,
            'active_tab': 'events'
        }
        return render(request, 'gestor/eventos.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_evento(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            data_inicio_str = request.POST.get('data_inicio')
            data_fim_str = request.POST.get('data_fim')
            
            evento = Evento(
                centro=centro,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao'),
                local=request.POST.get('local'),
                tipo=request.POST.get('tipo'),
                link_inscricao=request.POST.get('link_inscricao', '')
            )
            
            if data_inicio_str:
                evento.data_inicio = timezone.make_aware(
                    datetime.strptime(data_inicio_str, '%Y-%m-%dT%H:%M')
                )
            
            if data_fim_str:
                evento.data_fim = timezone.make_aware(
                    datetime.strptime(data_fim_str, '%Y-%m-%dT%H:%M')
                )
            
            if 'imagem' in request.FILES:
                evento.imagem = request.FILES['imagem']
            
            evento.save()
            messages.success(request, 'Evento adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar evento: {str(e)}')
    
    return redirect('eventos_gestor')

def toggle_destaque_evento(request, evento_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            evento = Evento.objects.get(
                id=evento_id, 
                centro_id=centro_id
            )
            evento.destaque = not evento.destaque
            evento.save()
            
            status = "em destaque" if evento.destaque else "removido do destaque"
            messages.success(request, f'Evento {status} com sucesso!')
            
        except Evento.DoesNotExist:
            messages.error(request, "Evento não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar destaque: {str(e)}')
    
    return redirect('eventos_gestor')

def excluir_evento(request, evento_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            evento = Evento.objects.get(
                id=evento_id, 
                centro_id=centro_id
            )
            
            if evento.imagem and os.path.isfile(evento.imagem.path):
                os.remove(evento.imagem.path)
            
            evento.delete()
            messages.success(request, 'Evento excluído com sucesso!')
            
        except Evento.DoesNotExist:
            messages.error(request, "Evento não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir evento: {str(e)}')
    
    return redirect('eventos_gestor')




def reels_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        reels = centro.reels.all()
        
        context = {
            'centro': centro,
            'reels': reels,
            'active_tab': 'reels'
        }
        return render(request, 'gestor/reels.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_reel(request):
    if request.method == 'POST' and request.FILES.get('video'):
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            reel = ReelCentro(
                centro=centro,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao', ''),
                video=request.FILES['video']
            )
            
            if 'thumbnail' in request.FILES:
                reel.thumbnail = request.FILES['thumbnail']
            
            reel.save()
            messages.success(request, 'Reel adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar reel: {str(e)}')
    
    return redirect('reels_gestor')

def toggle_publico_reel(request, reel_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            reel = ReelCentro.objects.get(
                id=reel_id, 
                centro_id=centro_id
            )
            reel.publico = not reel.publico
            reel.save()
            
            status = "público" if reel.publico else "privado"
            messages.success(request, f'Reel definido como {status} com sucesso!')
            
        except ReelCentro.DoesNotExist:
            messages.error(request, "Reel não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar visibilidade: {str(e)}')
    
    return redirect('reels_gestor')

def toggle_destaque_reel(request, reel_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            reel = ReelCentro.objects.get(
                id=reel_id, 
                centro_id=centro_id
            )
            reel.destaque = not reel.destaque
            reel.save()
            
            status = "em destaque" if reel.destaque else "removido do destaque"
            messages.success(request, f'Reel {status} com sucesso!')
            
        except ReelCentro.DoesNotExist:
            messages.error(request, "Reel não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar destaque: {str(e)}')
    
    return redirect('reels_gestor')

def excluir_reel(request, reel_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            reel = ReelCentro.objects.get(
                id=reel_id, 
                centro_id=centro_id
            )
            
            # Remover arquivos de mídia
            if reel.video and os.path.isfile(reel.video.path):
                os.remove(reel.video.path)
            if reel.thumbnail and os.path.isfile(reel.thumbnail.path):
                os.remove(reel.thumbnail.path)
            
            reel.delete()
            messages.success(request, 'Reel excluído com sucesso!')
            
        except ReelCentro.DoesNotExist:
            messages.error(request, "Reel não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir reel: {str(e)}')
    
    return redirect('reels_gestor')




def recursos_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        recursos = centro.recursos.all()
        
        context = {
            'centro': centro,
            'recursos': recursos,
            'active_tab': 'resources'
        }
        return render(request, 'gestor/recursos.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_recurso(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            Recurso.objects.create(
                centro=centro,
                nome=request.POST.get('nome'),
                descricao=request.POST.get('descricao'),
                icone=request.POST.get('icone', '')
            )
            
            messages.success(request, 'Recurso adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar recurso: {str(e)}')
    
    return redirect('recursos_gestor')

def editar_recurso(request, recurso_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            recurso = Recurso.objects.get(
                id=recurso_id, 
                centro_id=centro_id
            )
            
            recurso.nome = request.POST.get('nome', recurso.nome)
            recurso.descricao = request.POST.get('descricao', recurso.descricao)
            recurso.icone = request.POST.get('icone', recurso.icone)
            recurso.save()
            
            messages.success(request, 'Recurso atualizado com sucesso!')
            
        except Recurso.DoesNotExist:
            messages.error(request, "Recurso não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar recurso: {str(e)}')
    
    return redirect('recursos_gestor')

def excluir_recurso(request, recurso_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            recurso = Recurso.objects.get(
                id=recurso_id, 
                centro_id=centro_id
            )
            recurso.delete()
            messages.success(request, 'Recurso excluído com sucesso!')
            
        except Recurso.DoesNotExist:
            messages.error(request, "Recurso não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir recurso: {str(e)}')
    
    return redirect('recursos_gestor')




def areas_formacao_gestor(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        areas = centro.areas_formacao.all()
        
        context = {
            'centro': centro,
            'areas': areas,
            'active_tab': 'areas'
        }
        return render(request, 'gestor/areas_formacao.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_area_formacao(request):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            AreaFormacao.objects.create(
                centro=centro,
                nome=request.POST.get('nome'),
                descricao=request.POST.get('descricao', ''),
                icone=request.POST.get('icone', ''),
                ordem=request.POST.get('ordem', 0)
            )
            
            messages.success(request, 'Área de formação adicionada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar área: {str(e)}')
    
    return redirect('areas_formacao_gestor')

def editar_area_formacao(request, area_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            area = AreaFormacao.objects.get(
                id=area_id, 
                centro_id=centro_id
            )
            
            area.nome = request.POST.get('nome', area.nome)
            area.descricao = request.POST.get('descricao', area.descricao)
            area.icone = request.POST.get('icone', area.icone)
            area.ordem = request.POST.get('ordem', area.ordem)
            area.save()
            
            messages.success(request, 'Área de formação atualizada com sucesso!')
            
        except AreaFormacao.DoesNotExist:
            messages.error(request, "Área não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar área: {str(e)}')
    
    return redirect('areas_formacao_gestor')

def excluir_area_formacao(request, area_id):
    if request.method == 'POST':
        centro_id = request.session.get('centro_id')
        if not centro_id:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            area = AreaFormacao.objects.get(
                id=area_id, 
                centro_id=centro_id
            )
            area.delete()
            messages.success(request, 'Área de formação excluída com sucesso!')
            
        except AreaFormacao.DoesNotExist:
            messages.error(request, "Área não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir área: {str(e)}')
    
    return redirect('areas_formacao_gestor')






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
                
                # Se for salvar como rascunho
                if request.POST.get('rascunho'):
                    curso.rascunho = True
                    curso.publicado = False
                    curso.save()
                    form.save_m2m()
                    messages.success(request, 'Curso salvo como rascunho com sucesso!')
                    return redirect('listar_cursos')
                else:
                    # Salva e redireciona para overview
                    curso.rascunho = True
                    curso.publicado = False
                    curso.save()
                    form.save_m2m()
                    return redirect('curso_overview', curso_id=curso.id)
                    
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

def curso_overview(request, curso_id):
    """Página de revisão do curso antes da publicação"""
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para ver o curso.")
        return redirect('login_gestor')
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
    curso = get_object_or_404(Curso, id=curso_id, centro=centro)
    
    context = {
        'curso': curso,
        'centro': centro
    }
    return render(request, 'curso_overview.html', context)

def publicar_curso_final(request, curso_id):
    """Publicação final do curso após revisão"""
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        curso = Curso.objects.get(id=curso_id, centro=centro)
        
        # Validações finais antes de publicar
        if not curso.titulo:
            messages.error(request, "O curso precisa ter um título.")
            return redirect('curso_overview', curso_id=curso_id)
        
        if not curso.descricao:
            messages.error(request, "O curso precisa ter uma descrição.")
            return redirect('curso_overview', curso_id=curso_id)
        
        if not curso.instrutores.exists():
            messages.error(request, "O curso precisa ter pelo menos um instrutor.")
            return redirect('curso_overview', curso_id=curso_id)
        
        # Publica o curso
        curso.rascunho = False
        curso.publicado = True
        curso.data_publicacao = timezone.now()
        curso.save()
        
        messages.success(request, 'Curso publicado com sucesso!')
        return redirect('listar_cursos')
        
    except Exception as e:
        messages.error(request, f'Erro ao publicar curso: {str(e)}')
        return redirect('curso_overview', curso_id=curso_id)




# gestoreduka/views.py
def listar_cursos(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Faça login para ver seus cursos.")
        return redirect('login_gestor')
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
    
    # CORREÇÃO: Use data_criacao ou data_inicio_inscricoes
    cursos = Curso.objects.filter(centro=centro).order_by('-data_criacao')  # ← CORRIGIDO
    
    # Filtros para as abas
    cursos_publicados = cursos.filter(publicado=True)
    cursos_rascunhos = cursos.filter(publicado=False)
    cursos_destaque = cursos.filter(destaque=True)
    
    context = {
        'cursos': cursos,
        'cursos_publicados': cursos_publicados,
        'cursos_rascunhos': cursos_rascunhos,
        'cursos_destaque': cursos_destaque,
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




# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@login_required
def chat_centro(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        return redirect('login_gestor')
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
    
    # Buscar conversas do centro
    conversas = Conversa.objects.filter(centro=centro, ativa=True).select_related('aluno')
    
    # Se houver uma conversa específica selecionada
    conversa_id = request.GET.get('conversa_id')
    conversa_atual = None
    mensagens = []
    
    if conversa_id:
        conversa_atual = get_object_or_404(Conversa, id=conversa_id, centro=centro)
        mensagens = Mensagem.objects.filter(conversa=conversa_atual).select_related('remetente_aluno', 'remetente_centro')
    
    context = {
        'centro': centro,
        'conversas': conversas,
        'conversa_atual': conversa_atual,
        'mensagens': mensagens,
    }
    return render(request, 'chat_centro.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def enviar_mensagem_centro(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        conversa_id = data.get('conversa_id')
        mensagem_texto = data.get('mensagem')
        
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        conversa = get_object_or_404(Conversa, id=conversa_id, centro=centro)
        
        mensagem = Mensagem.objects.create(
            conversa=conversa,
            remetente_centro=centro,
            mensagem=mensagem_texto,
            tipo='TEXTO'
        )
        
        # Atualizar última mensagem da conversa
        conversa.ultima_mensagem = timezone.now()
        conversa.save()
        
        return JsonResponse({
            'success': True,
            'mensagem_id': mensagem.id,
            'data_envio': mensagem.data_envio.strftime('%d/%m/%Y %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def atualizar_status_digitando(request):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        conversa_id = data.get('conversa_id')
        digitando = data.get('digitando', False)
        
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        conversa = get_object_or_404(Conversa, id=conversa_id, centro=centro)
        
        # Buscar a mensagem de digitando existente
        mensagem_digitando = Mensagem.objects.filter(
            conversa=conversa, 
            remetente_centro=centro, 
            digitando=True
        ).first()
        
        if digitando:
            # Se não existe uma mensagem de digitando, criar uma
            if not mensagem_digitando:
                Mensagem.objects.create(
                    conversa=conversa,
                    remetente_centro=centro,
                    mensagem='...',
                    tipo='TEXTO',
                    digitando=True
                )
        else:
            # Se existe uma mensagem de digitando, deletá-la
            if mensagem_digitando:
                mensagem_digitando.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def buscar_mensagens(request, conversa_id):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
    conversa = get_object_or_404(Conversa, id=conversa_id, centro=centro)
    
    # Buscar mensagens normais + apenas a última mensagem de digitando do centro
    mensagens_normais = Mensagem.objects.filter(
        conversa=conversa, 
        digitando=False
    ).select_related('remetente_aluno', 'remetente_centro')
    
    ultima_digitando = Mensagem.objects.filter(
        conversa=conversa,
        remetente_centro=centro,
        digitando=True
    ).order_by('-data_envio').first()
    
    mensagens_data = []
    
    for msg in mensagens_normais:
        foto_perfil = None
        inicial = None
        
        if msg.remetente_aluno and hasattr(msg.remetente_aluno, 'perfil'):
            if msg.remetente_aluno.perfil:
                foto_perfil = msg.remetente_aluno.perfil.get_foto_perfil_url()
                inicial = msg.remetente_aluno.perfil.get_inicial_nome()
        
        mensagens_data.append({
            'id': msg.id,
            'mensagem': msg.mensagem,
            'tipo': msg.tipo,
            'is_centro': msg.is_centro(),
            'remetente_nome': msg.remetente.nome if msg.remetente_aluno else msg.remetente_centro.nome,
            'foto_perfil': foto_perfil,
            'inicial': inicial,
            'data_envio': msg.data_envio.strftime('%H:%M'),
            'digitando': msg.digitando
        })
    
    if ultima_digitando:
        mensagens_data.append({
            'id': ultima_digitando.id,
            'mensagem': ultima_digitando.mensagem,
            'tipo': ultima_digitando.tipo,
            'is_centro': ultima_digitando.is_centro(),
            'remetente_nome': ultima_digitando.remetente_centro.nome,
            'foto_perfil': None,
            'inicial': None,
            'data_envio': ultima_digitando.data_envio.strftime('%H:%M'),
            'digitando': True
        })
    
    return JsonResponse({'mensagens': mensagens_data})



@login_required
def iniciar_conversa_centro(request, centro_id):
    """Iniciar uma nova conversa com um centro"""
    try:
        aluno_id = request.session.get('aluno')
        if not aluno_id:
            messages.error(request, 'Você precisa estar logado como aluno para iniciar uma conversa.')
            return redirect('login_aluno')
        
        aluno = Aluno.objects.get(id=aluno_id, ativo=True)
        centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
        
        # Verificar se já existe uma conversa
        conversa, created = Conversa.objects.get_or_create(
            centro=centro,
            aluno=aluno,
            defaults={
                'data_criacao': timezone.now(),
                'ultima_mensagem': timezone.now()
            }
        )
        
        # Redirecionar para a página de chat do aluno com a conversa selecionada
        return redirect(f'{reverse("aluno_chat")}?conversa_id={conversa.id}')
        
    except Aluno.DoesNotExist:
        messages.error(request, 'Aluno não encontrado. Faça login novamente.')
        return redirect('login_aluno')
    except Exception as e:
        messages.error(request, f'Erro ao iniciar conversa: {str(e)}')
        return redirect('listar_cursos')



@login_required
def centro_chat_modal(request, centro_id):
    """View para carregar o modal de chat no perfil do centro"""
    try:
        centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
        aluno_id = request.session.get('aluno')
        
        if not aluno_id:
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        aluno = get_object_or_404(Aluno, id=aluno_id, ativo=True)
        
        # Buscar ou criar conversa
        conversa, created = Conversa.objects.get_or_create(
            centro=centro,
            aluno=aluno,
            defaults={
                'data_criacao': timezone.now(),
                'ultima_mensagem': timezone.now()
            }
        )
        
        # Buscar mensagens
        mensagens = Mensagem.objects.filter(conversa=conversa).select_related(
            'remetente_aluno', 'remetente_centro'
        ).order_by('data_envio')
        
        mensagens_data = []
        for msg in mensagens:
            mensagens_data.append({
                'id': msg.id,
                'mensagem': msg.mensagem,
                'is_centro': msg.is_centro(),
                'remetente_nome': msg.remetente_centro.nome if msg.is_centro() else aluno.nome,
                'data_envio': msg.data_envio.strftime('%H:%M'),
                'digitando': msg.digitando
            })
        
        return JsonResponse({
            'success': True,
            'conversa_id': conversa.id,
            'mensagens': mensagens_data,
            'centro_nome': centro.nome,
            'aluno_nome': aluno.nome
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def enviar_mensagem_centro_modal(request):
    """Enviar mensagem via modal do perfil do centro"""
    aluno_id = request.session.get('aluno')
    if not aluno_id:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        conversa_id = data.get('conversa_id')
        mensagem_texto = data.get('mensagem')
        
        aluno = Aluno.objects.get(id=aluno_id, ativo=True)
        conversa = get_object_or_404(Conversa, id=conversa_id, aluno=aluno)
        
        mensagem = Mensagem.objects.create(
            conversa=conversa,
            remetente_aluno=aluno,
            mensagem=mensagem_texto,
            tipo='TEXTO'
        )
        
        # Atualizar última mensagem da conversa
        conversa.ultima_mensagem = timezone.now()
        conversa.save()
        
        return JsonResponse({
            'success': True,
            'mensagem_id': mensagem.id,
            'data_envio': mensagem.data_envio.strftime('%H:%M'),
            'is_centro': False
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def atualizar_digitando_modal(request):
    """Atualizar status de digitando no modal"""
    aluno_id = request.session.get('aluno')
    if not aluno_id:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        conversa_id = data.get('conversa_id')
        digitando = data.get('digitando', False)
        
        aluno = Aluno.objects.get(id=aluno_id, ativo=True)
        conversa = get_object_or_404(Conversa, id=conversa_id, aluno=aluno)
        
        # Buscar mensagem de digitando existente
        mensagem_digitando = Mensagem.objects.filter(
            conversa=conversa, 
            remetente_aluno=aluno, 
            digitando=True
        ).first()
        
        if digitando:
            if not mensagem_digitando:
                Mensagem.objects.create(
                    conversa=conversa,
                    remetente_aluno=aluno,
                    mensagem='...',
                    tipo='TEXTO',
                    digitando=True
                )
        else:
            if mensagem_digitando:
                mensagem_digitando.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def buscar_mensagens_modal(request, conversa_id):
    """Buscar mensagens para o modal"""
    aluno_id = request.session.get('aluno')
    if not aluno_id:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    aluno = get_object_or_404(Aluno, id=aluno_id, ativo=True)
    conversa = get_object_or_404(Conversa, id=conversa_id, aluno=aluno)
    
    # Buscar mensagens normais + digitando
    mensagens_normais = Mensagem.objects.filter(
        conversa=conversa, 
        digitando=False
    ).select_related('remetente_aluno', 'remetente_centro')
    
    ultima_digitando = Mensagem.objects.filter(
        conversa=conversa,
        remetente_aluno=aluno,
        digitando=True
    ).order_by('-data_envio').first()
    
    mensagens_data = []
    
    for msg in mensagens_normais:
        mensagens_data.append({
            'id': msg.id,
            'mensagem': msg.mensagem,
            'is_centro': msg.is_centro(),
            'remetente_nome': msg.remetente_centro.nome if msg.is_centro() else aluno.nome,
            'data_envio': msg.data_envio.strftime('%H:%M'),
            'digitando': False
        })
    
    if ultima_digitando:
        mensagens_data.append({
            'id': ultima_digitando.id,
            'mensagem': ultima_digitando.mensagem,
            'is_centro': False,
            'remetente_nome': aluno.nome,
            'data_envio': ultima_digitando.data_envio.strftime('%H:%M'),
            'digitando': True
        })
    
    return JsonResponse({'mensagens': mensagens_data})