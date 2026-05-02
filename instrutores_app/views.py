from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import InstrutorSignupForm
from django.contrib.auth.forms import AuthenticationForm

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
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.tipo_usuario == 'INSTRUTOR':
                if user.is_active:
                    login(request, user)
                    return redirect('instrutores_app:dashboard')
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
from cursos_app.models import Instrutor
from django.db.models import Count, Sum

def get_instrutor(user):
    return getattr(user, 'instrutor_profile', None)

def instrutor_dashboard(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
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
    cursos = Curso_video.objects.filter(instrutor=instrutor).order_by('-id')
    return render(request, 'instrutores/cursos.html', {'cursos': cursos})

def criar_curso(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
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
    curso = get_object_or_404(Curso_video, id=curso_id, instrutor=instrutor)
    aulas = Aula.objects.filter(curso=curso).order_by('ordem')
    
    return render(request, 'instrutores/detalhe_curso.html', {'curso': curso, 'aulas': aulas})
from .forms import CursoVideoForm, AulaForm

def adicionar_aula(request, curso_id):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
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
    aula = get_object_or_404(Aula, id=aula_id, curso__instrutor=get_instrutor(request.user))
    
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
    aula = get_object_or_404(Aula, id=aula_id, curso__instrutor=get_instrutor(request.user))
    curso_id = aula.curso.id
    aula.delete()
    messages.success(request, "Aula removida com sucesso!")
    return redirect('instrutores_app:detalhe_curso', curso_id=curso_id)
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CursoVideoForm, AulaForm, InstrutorProfileForm, MaterialAulaForm, AvisoCursoForm
from cursovideoapp.models import MaterialAula, AvisoCurso, ProgressoAula

def listar_alunos(request):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'INSTRUTOR':
        return redirect('instrutores_app:login')
    
    instrutor = get_instrutor(request.user)
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
