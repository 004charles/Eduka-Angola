from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_http_methods
import json

from cursovideoapp.models import Curso_video, Aula, Certificado
from gestoreduka.models import CentroDeFormacao, AuditoriaCentro
from gestoreduka.views import get_gestor_context
from gestoreduka.forms import CursoVideoForm, AulaForm
from gestoreduka.plan_permissions import get_plano_ativo, limite


def _react_video_course_payload(curso, include_lessons=False):
    try:
        capa = curso.capa.url if curso.capa else ''
    except ValueError:
        capa = ''
    capas_demonstracao = {
        'Excel para Decisões Rápidas': '/manus-storage/demo-video-excel-decisoes_b6137029.jpg',
        'Empreendedorismo na Prática': '/manus-storage/demo-video-empreendedorismo_62e4b9d3.jpg',
    }
    capa = capa or capas_demonstracao.get(curso.titulo, '')
    result = {'id': curso.id, 'titulo': curso.titulo, 'descricao': curso.descricao, 'categoria_id': curso.categoria_id, 'categoria': curso.categoria.nome, 'is_pago': curso.is_pago, 'preco': str(curso.preco), 'destaque': curso.destaque, 'capa_url': capa, 'total_aulas': curso.aulas.count(), 'total_inscritos': curso.inscritos.count(), 'data_publicacao': curso.data_publicacao.isoformat()}
    if include_lessons:
        result['aulas'] = [{'id': aula.id, 'titulo': aula.titulo, 'video_url': aula.video_url, 'descricao': aula.descricao or '', 'ordem': aula.ordem} for aula in curso.aulas.order_by('ordem', 'id')]
    return result


def _react_video_data(request):
    if request.content_type and request.content_type.startswith('application/json'):
        try:
            return json.loads(request.body or '{}'), None
        except (TypeError, ValueError):
            return None, JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    return request.POST, None


def _react_video_access(request):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return None, None, JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    plano = get_plano_ativo(centro)
    if not plano or not plano.permite_cursos_video:
        return None, None, JsonResponse({'detail': 'O plano actual não permite gerir cursos em vídeo.'}, status=403)
    return centro, filial, None


@login_required
@require_http_methods(['GET', 'POST'])
def react_gestor_video_courses(request):
    """Lista ou cria cursos em vídeo no centro autenticado, respeitando os limites do plano."""
    centro, filial, response = _react_video_access(request)
    if response:
        return response
    if request.method == 'GET':
        form = CursoVideoForm()
        return JsonResponse({'cursos': [_react_video_course_payload(curso) for curso in Curso_video.objects.filter(centro=centro).select_related('categoria').order_by('-data_publicacao')], 'categorias': [{'id': categoria.id, 'nome': categoria.nome} for categoria in form.fields['categoria'].queryset.order_by('nome')], 'limite': limite(centro, 'limite_cursos_video', padrao=0)})
    if Curso_video.objects.filter(centro=centro).count() >= limite(centro, 'limite_cursos_video', padrao=0):
        return JsonResponse({'detail': 'O limite de cursos em vídeo do plano foi atingido.'}, status=403)
    payload, response = _react_video_data(request)
    if response:
        return response
    form = CursoVideoForm(payload, request.FILES)
    if not form.is_valid():
        return JsonResponse({'detail': 'Verifique os dados do curso em vídeo.', 'errors': form.errors.get_json_data()}, status=400)
    curso = form.save(commit=False)
    curso.centro = centro
    curso.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CURSO_VIDEO_CRIADO', entidade='Curso_video', objeto_id=str(curso.pk), dados={'titulo': curso.titulo})
    return JsonResponse({'ok': True, 'curso': _react_video_course_payload(curso)}, status=201)


@login_required
@require_http_methods(['GET', 'PATCH', 'DELETE'])
def react_gestor_video_course_detail(request, curso_id):
    """Consulta, actualiza ou remove um curso em vídeo pertencente ao centro autenticado."""
    centro, filial, response = _react_video_access(request)
    if response:
        return response
    curso = get_object_or_404(Curso_video.objects.select_related('categoria'), id=curso_id, centro=centro)
    if request.method == 'GET':
        return JsonResponse({'curso': _react_video_course_payload(curso, include_lessons=True)})
    if request.method == 'DELETE':
        titulo = curso.titulo
        curso.delete()
        AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CURSO_VIDEO_REMOVIDO', entidade='Curso_video', objeto_id=str(curso_id), dados={'titulo': titulo})
        return JsonResponse({'ok': True, 'curso_id': curso_id})
    payload, response = _react_video_data(request)
    if response:
        return response
    form = CursoVideoForm(payload, request.FILES, instance=curso)
    if not form.is_valid():
        return JsonResponse({'detail': 'Verifique os dados do curso em vídeo.', 'errors': form.errors.get_json_data()}, status=400)
    curso = form.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CURSO_VIDEO_ACTUALIZADO', entidade='Curso_video', objeto_id=str(curso.pk), dados={'titulo': curso.titulo})
    return JsonResponse({'ok': True, 'curso': _react_video_course_payload(curso, include_lessons=True)})


@login_required
@require_http_methods(['POST'])
def react_gestor_video_lessons(request, curso_id):
    """Acrescenta uma aula validada a um curso em vídeo do centro autenticado."""
    centro, filial, response = _react_video_access(request)
    if response:
        return response
    curso = get_object_or_404(Curso_video, id=curso_id, centro=centro)
    payload, response = _react_video_data(request)
    if response:
        return response
    form = AulaForm(payload)
    if not form.is_valid():
        return JsonResponse({'detail': 'Verifique os dados da aula.', 'errors': form.errors.get_json_data()}, status=400)
    aula = form.save(commit=False)
    aula.curso = curso
    aula.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='AULA_VIDEO_CRIADA', entidade='Aula', objeto_id=str(aula.pk), dados={'curso_id': curso.pk, 'titulo': aula.titulo})
    return JsonResponse({'ok': True, 'aula': {'id': aula.id, 'titulo': aula.titulo, 'video_url': aula.video_url, 'descricao': aula.descricao or '', 'ordem': aula.ordem}}, status=201)


@login_required
@require_http_methods(['DELETE'])
def react_gestor_video_lesson_detail(request, aula_id):
    """Remove uma aula de um curso em vídeo pertencente ao centro autenticado."""
    centro, filial, response = _react_video_access(request)
    if response:
        return response
    aula = get_object_or_404(Aula, id=aula_id, curso__centro=centro)
    curso_id, titulo = aula.curso_id, aula.titulo
    aula.delete()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='AULA_VIDEO_REMOVIDA', entidade='Aula', objeto_id=str(aula_id), dados={'curso_id': curso_id, 'titulo': titulo})
    return JsonResponse({'ok': True, 'aula_id': aula_id})


def _react_video_certificate_payload(certificado):
    return {'id': str(certificado.id), 'aluno': certificado.aluno.nome, 'curso': certificado.curso.titulo, 'data_emissao': certificado.data_emissao.isoformat(), 'codigo_verificacao': certificado.codigo_verificacao, 'status': certificado.status, 'nota_final': str(certificado.nota_final), 'exercicios_concluidos': certificado.total_exercicios_concluidos}


@login_required
@require_http_methods(['GET'])
def react_gestor_video_certificates(request):
    """Lista certificados de cursos em vídeo pertencentes ao centro autenticado."""
    centro, filial, response = _react_video_access(request)
    if response:
        return response
    certificados = Certificado.objects.filter(curso__centro=centro).select_related('aluno', 'curso').order_by('-data_emissao')
    status = request.GET.get('status')
    if status in {'PENDENTE', 'EMITIDO', 'REJEITADO'}:
        certificados = certificados.filter(status=status)
    return JsonResponse({'certificados': [_react_video_certificate_payload(certificado) for certificado in certificados[:100]], 'status_opcoes': ['PENDENTE', 'EMITIDO', 'REJEITADO']})


@login_required
@require_http_methods(['PATCH'])
def react_gestor_video_certificate_detail(request, certificado_id):
    """Actualiza o estado de um certificado em vídeo que pertence ao centro autenticado."""
    centro, filial, response = _react_video_access(request)
    if response:
        return response
    certificado = get_object_or_404(Certificado.objects.select_related('aluno', 'curso'), id=certificado_id, curso__centro=centro)
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    status = payload.get('status')
    if status not in {'PENDENTE', 'EMITIDO', 'REJEITADO'}:
        return JsonResponse({'detail': 'O estado do certificado é inválido.'}, status=400)
    certificado.status, certificado.aprovado_por = status, request.user
    certificado.save(update_fields=['status', 'aprovado_por'])
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CERTIFICADO_VIDEO_ACTUALIZADO', entidade='Certificado', objeto_id=str(certificado.pk), dados={'status': status})
    return JsonResponse({'ok': True, 'certificado': _react_video_certificate_payload(certificado)})

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
