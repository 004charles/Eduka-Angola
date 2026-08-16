from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from cursovideoapp.models import Curso_video, Aula, Certificado
from gestoreduka.models import CentroDeFormacao
from gestoreduka.views import get_gestor_context
from gestoreduka.forms import CursoVideoForm, AulaForm
from gestoreduka.plan_permissions import get_plano_ativo, limite

@login_required
def listar_cursos_video(request):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    cursos = Curso_video.objects.filter(centro=centro).order_by('-data_publicacao')
    
    paginator = Paginator(cursos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gestor/video/listar_cursos.html', {
        'centro': centro,
        'page_obj': page_obj
    })

@login_required
def criar_curso_video(request):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    plano = get_plano_ativo(centro)
    if not plano or not plano.permite_cursos_video:
        messages.error(request, 'O seu plano atual não permite publicar cursos em vídeo.')
        return redirect('gerenciar_assinatura')

    limite_video_cursos = limite(centro, 'limite_cursos_video', padrao=0)
    total_video_cursos = Curso_video.objects.filter(centro=centro).count()
    if total_video_cursos >= limite_video_cursos:
        messages.warning(request, f'Atingiu o limite de vídeo-cursos do seu plano ({limite_video_cursos}).')
        return redirect('gerenciar_assinatura')

    if request.method == 'POST':
        form = CursoVideoForm(request.POST, request.FILES)
        if form.is_valid():
            curso = form.save(commit=False)
            curso.centro = centro
            curso.save()
            messages.success(request, 'Curso em vídeo criado com sucesso!')
            return redirect('listar_cursos_video')
    else:
        form = CursoVideoForm()

    return render(request, 'gestor/video/form_curso.html', {
        'form': form,
        'centro': centro,
        'titulo_pagina': 'Criar Curso em Vídeo'
    })

@login_required
def editar_curso_video(request, curso_id):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    curso = get_object_or_404(Curso_video, id=curso_id, centro=centro)

    if request.method == 'POST':
        form = CursoVideoForm(request.POST, request.FILES, instance=curso)
        if form.is_valid():
            form.save()
            messages.success(request, 'Curso atualizado com sucesso!')
            return redirect('listar_cursos_video')
    else:
        form = CursoVideoForm(instance=curso)

    return render(request, 'gestor/video/form_curso.html', {
        'form': form,
        'centro': centro,
        'curso': curso,
        'titulo_pagina': 'Editar Curso em Vídeo'
    })

@login_required
def excluir_curso_video(request, curso_id):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    curso = get_object_or_404(Curso_video, id=curso_id, centro=centro)
    
    if request.method == 'POST':
        curso.delete()
        messages.success(request, 'Curso excluído com sucesso!')
        
    return redirect('listar_cursos_video')

@login_required
def gerenciar_aulas_video(request, curso_id):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    curso = get_object_or_404(Curso_video, id=curso_id, centro=centro)
    
    plano = get_plano_ativo(centro)
    pode_publicar_video = bool(plano and plano.permite_cursos_video)
    if not pode_publicar_video:
        messages.error(request, 'O seu plano atual não permite gerir aulas de vídeo.')
        return redirect('gerenciar_assinatura')

    # O plano limita o número de vídeo-cursos, não o número de aulas de cada curso.
    # As aulas ficam sem limite artificial até existir um campo comercial específico.
    limite_aulas = None
    total_aulas = curso.aulas.count()
    pode_adicionar = True

    if request.method == 'POST' and pode_adicionar:
        form = AulaForm(request.POST)
        if form.is_valid():
            aula = form.save(commit=False)
            aula.curso = curso
            aula.save()
            messages.success(request, 'Aula adicionada com sucesso!')
            return redirect('gerenciar_aulas_video', curso_id=curso.id)
    else:
        form = AulaForm()

    aulas = curso.aulas.all().order_by('ordem')

    return render(request, 'gestor/video/gerenciar_aulas.html', {
        'curso': curso,
        'aulas': aulas,
        'form': form,
        'centro': centro,
        'pode_adicionar': pode_adicionar,
        'limite_aulas': limite_aulas,
        'total_aulas': total_aulas
    })

@login_required
def excluir_aula_video(request, aula_id):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    aula = get_object_or_404(Aula, id=aula_id, curso__centro=centro)
    curso_id = aula.curso.id
    
    if request.method == 'POST':
        aula.delete()
        messages.success(request, 'Aula excluída com sucesso!')
        
    return redirect('gerenciar_aulas_video', curso_id=curso_id)

@login_required
def listar_certificados_video(request):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    certificados = Certificado.objects.filter(curso__centro=centro).order_by('-data_emissao')
    
    status_filter = request.GET.get('status')
    if status_filter:
        certificados = certificados.filter(status=status_filter)
        
    paginator = Paginator(certificados, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'gestor/video/listar_certificados.html', {
        'centro': centro,
        'page_obj': page_obj,
        'status_filter': status_filter
    })

@login_required
def alterar_status_certificado(request, certificado_id):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    certificado = get_object_or_404(Certificado, id=certificado_id, curso__centro=centro)
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in ['EMITIDO', 'REJEITADO', 'PENDENTE']:
            certificado.status = novo_status
            certificado.aprovado_por = request.user
            certificado.save()
            messages.success(request, f'Status do certificado alterado para {novo_status}!')
            
    return redirect('listar_certificados_video')
