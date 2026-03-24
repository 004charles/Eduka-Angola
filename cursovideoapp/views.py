from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import json
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from cursos_app.models import Categoria, Instrutor
from cursovideoapp.models import Curso_video, FavoritoCursoVideo, Aula, ProgressoAula, Certificado

@login_required
def emitir_certificado(request, curso_slug):
    """
    Gera ou exibe o certificado de conclusão do curso para o aluno logado.
    """
    curso = get_object_or_404(Curso_video, slug=curso_slug)
    try:
        aluno = request.user.aluno_profile
    except (ObjectDoesNotExist, AttributeError):
        return redirect('index')
    
    # Verificar se o aluno concluiu todas as aulas
    if not curso.verificar_conclusao(aluno):
        return redirect('cursovideoapp:detalhe_curso', slug=curso_slug)
    
    # Obter ou criar o certificado
    certificado, created = Certificado.objects.get_or_create(aluno=aluno, curso=curso)
    
    # Gerar link de verificação completo para o QR Code
    verificacao_url = request.build_absolute_uri(
        reverse('cursovideoapp:verificar_certificado', kwargs={'codigo': certificado.codigo_verificacao})
    )
    
    return render(request, 'cursovideo/certificado.html', {
        'certificado': certificado,
        'aluno': aluno,
        'curso': curso,
        'verificacao_url': verificacao_url
    })

def verificar_certificado(request, codigo):
    """
    Página pública para validar a autenticidade de um certificado.
    """
    certificado = get_object_or_404(Certificado, codigo_verificacao=codigo)
    return render(request, 'cursovideo/verificar_certificado.html', {
        'certificado': certificado
    })
from avaliacoes.models import Comentario
from cursos_app.forms import AvaliacaoForm

def home_videos(request):
    """
    Página inicial para cursos em vídeo com diversas seções.
    """
    agora = timezone.now()
    
    # 1. Newest Videos (Novos Lançamentos)
    videos_recentes = Curso_video.objects.order_by('-data_publicacao')[:4]
    
    # 2. Trending (Em Alta) - based on enrollment count for now
    videos_populares = Curso_video.objects.annotate(
        num_inscritos=Count('inscritos')
    ).order_by('-num_inscritos')[:4]
    
    # 3. Most Watched (Mais Assistidos) - based on total lesson views
    videos_assistidos = Curso_video.objects.annotate(
        total_views=Sum('aulas__visualizacoes')
    ).order_by('-total_views')[:4]
    
    # Categories for filter
    categorias = Categoria.objects.annotate(
        num_cursos=Count('cursos_video')
    ).filter(num_cursos__gt=0).order_by('nome')
    
    context = {
        'videos_recentes': videos_recentes,
        'videos_populares': videos_populares,
        'videos_assistidos': videos_assistidos,
        'categorias': categorias,
        'aluno_logado': False,
        'favoritos': [],
        'active_menu': 'cursos_video',
    }
    
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            favoritos = FavoritoCursoVideo.objects.filter(aluno=aluno).values_list('curso_id', flat=True)
            context.update({
                'aluno_logado': True,
                'favoritos': list(favoritos),
            })
        except (ObjectDoesNotExist, AttributeError):
            pass
            
    return render(request, 'cursovideo/home.html', context)


@require_POST
def toggle_favorito_video(request):
    """
    API para alternar o status de favorito de um curso em vídeo.
    """
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'status': 'error', 'message': 'Não autorizado'}, status=403)
    
    try:
        data = json.loads(request.body)
        curso_id = data.get('curso_id')
        curso = Curso_video.objects.get(id=curso_id)
        
        try:
            aluno = request.user.aluno_profile
        except (ObjectDoesNotExist, AttributeError):
            return JsonResponse({'status': 'error', 'message': 'Perfil de aluno não encontrado'}, status=403)
        
        favorito, created = FavoritoCursoVideo.objects.get_or_create(aluno=aluno, curso=curso)
        
        if not created:
            favorito.delete()
            return JsonResponse({'status': 'removed'})
        
        return JsonResponse({'status': 'added'})
        
    except Curso_video.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Curso não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def api_load_more_videos(request):
    """
    API para carregar mais cursos em vídeo.
    """
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 4))
        tipo_filtro = request.GET.get('tipo', 'recentes')
        categoria_slug = request.GET.get('categoria', None)
        
        qs = Curso_video.objects.all()
        
        if categoria_slug:
            qs = qs.filter(categoria__slug=categoria_slug)
            
        if tipo_filtro == 'populares':
            qs = qs.annotate(num=Count('inscritos')).order_by('-num')
        else:
            qs = qs.order_by('-data_publicacao')
            
        cursos = qs[offset:offset+limit]
        
        data = []
        favoritos = []
        if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
             try:
                 aluno = request.user.aluno_profile
                 favoritos = list(FavoritoCursoVideo.objects.filter(
                     aluno=aluno, 
                     curso__in=cursos
                 ).values_list('curso_id', flat=True))
             except (ObjectDoesNotExist, AttributeError):
                 favoritos = []

        for curso in cursos:
            # Fallback for image
            img_url = curso.capa.url if curso.capa else '/static/assets/images/course/default-course.jpg'
            
            data.append({
                'id': curso.id,
                'titulo': curso.titulo,
                'imagem_url': img_url,
                'instrutor': curso.instrutor.nome,
                'visualizacoes': 0, # Video model might not have views yet
                'is_favorito': curso.id in favoritos,
                # 'url_detalhe': reverse('curso_video_detalhe', args=[curso.id]) # Update with real URL name
            })
            
        return JsonResponse({'cursos': data, 'has_more': qs.count() > offset + limit})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- Restored Views ---

def lista_cursos(request):
    """
    Exibe a lista de todos os cursos em vídeo, incluindo destaques.
    """

def detalhe_curso(request, slug):
    """
    Exibe os detalhes de um curso em vídeo, incluindo aulas e avaliações.
    """
    curso = get_object_or_404(Curso_video, slug=slug)
    
    # 1. Verificar se o aluno está inscrito e logado
    aluno_logado = request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO'
    aluno_obj = None
    aluno_inscrito = False
    
    if aluno_logado:
        try:
            aluno_obj = request.user.aluno_profile
            aluno_inscrito = curso.inscritos.filter(id=aluno_obj.id).exists()
        except (ObjectDoesNotExist, AttributeError):
            aluno_logado = False

    # 2. Carregar comentários e avaliações
    comentarios = Comentario.objects.select_related('aluno').filter(
        curso_video=curso,
        aprovado=True
    ).order_by('-data_comentario')
    
    media_result = comentarios.aggregate(media=Avg('avaliacao'))
    media_avaliacoes = media_result['media'] or 0.0
    
    rating_counts = {
        '5': comentarios.filter(avaliacao=5).count(),
        '4': comentarios.filter(avaliacao=4).count(),
        '3': comentarios.filter(avaliacao=3).count(),
        '2': comentarios.filter(avaliacao=2).count(),
        '1': comentarios.filter(avaliacao=1).count(),
    }
    
    total_comentarios = comentarios.count()
    rating_percent = {}
    for key, count in rating_counts.items():
        rating_percent[key] = (count / total_comentarios) * 100 if total_comentarios > 0 else 0

    # 3. Verificar comentário existente e formulário
    comentario_existente = None
    if aluno_obj:
        comentario_existente = Comentario.objects.filter(
            aluno=aluno_obj, 
            curso_video=curso
        ).first()
    
    avaliacao_form = None
    if aluno_logado and aluno_inscrito:
        avaliacao_form = AvaliacaoForm(instance=comentario_existente)

    # 4. Outros dados (aulas, cursos recomendados)
    aulas = curso.aulas.all().order_by('ordem')
    total_visualizacoes = aulas.aggregate(total=Count('id'))['total'] # Placeholder simple logic
    
    cursos_recomendados = Curso_video.objects.exclude(id=curso.id)[:6]
            
    # 4. Calcular progresso do curso se aluno logado e inscrito
    progresso_total = 0
    if aluno_inscrito:
        total_aulas = curso.aulas.count()
        if total_aulas > 0:
            aulas_concluidas = ProgressoAula.objects.filter(
                aluno=aluno_obj, 
                aula__curso=curso, 
                concluida=True
            ).count()
            progresso_total = int((aulas_concluidas / total_aulas) * 100)
            
    return render(request, 'cursovideo/detalhe_curso.html', {
        'curso': curso,
        'aluno_logado': aluno_logado,
        'aluno_inscrito': aluno_inscrito,
        'aulas': aulas,
        'comentarios': comentarios,
        'media_avaliacoes': round(media_avaliacoes, 1),
        'rating_counts': rating_counts,
        'rating_percent': rating_percent,
        'total_comentarios': total_comentarios,
        'avaliacao_form': avaliacao_form,
        'comentario_existente': comentario_existente,
        'total_visualizacoes': curso.aulas.all().count(), # Simplificado para exemplo
        'cursos_recomendados': cursos_recomendados,
        'progresso_total': progresso_total,
    })

@login_required
def toggle_inscricao(request, slug):
    """
    Inscreve ou remove a inscrição de um aluno em um curso.
    """
    curso = get_object_or_404(Curso_video, slug=slug)
    
    if request.user.tipo_usuario != 'ALUNO':
        return redirect('cursovideoapp:detalhe_curso', slug=slug)
        
    try:
        aluno = request.user.aluno_profile
    except (ObjectDoesNotExist, AttributeError):
        # Se for um Aluno sem perfil (deveria ser raro, mas acontece)
        messages.error(request, "Perfil de aluno não encontrado. Por favor, complete o seu registo.")
        return redirect('index')

    if curso.inscritos.filter(id=aluno.id).exists():
        curso.inscritos.remove(aluno)
    else:
        curso.inscritos.add(aluno)
        
    return redirect('cursovideoapp:detalhe_curso', slug=slug)

@login_required
def ver_aula(request, curso_slug, pk):
    """
    Interface de visualização de uma aula específica do curso com lógica de desbloqueio sequencial.
    """
    curso = get_object_or_404(Curso_video, slug=curso_slug)
    aula_atual = get_object_or_404(Aula, pk=pk, curso=curso)
    
    # Verificar inscrição
    try:
        aluno = request.user.aluno_profile
    except (ObjectDoesNotExist, AttributeError):
        return redirect('index')
        
    if not curso.inscritos.filter(id=aluno.id).exists():
        return redirect('cursovideoapp:detalhe_curso', slug=curso_slug)
    
    aulas = curso.aulas.all().order_by('ordem')
    
    # Lógica de desbloqueio sequencial
    progressos = ProgressoAula.objects.filter(aluno=aluno, aula__curso=curso)
    concluidas_ids = set(progressos.filter(concluida=True).values_list('aula_id', flat=True))
    
    aulas_status = []
    # A primeira aula está sempre desbloqueada
    aula_anterior_concluida = True 
    
    for i, aula in enumerate(aulas):
        if i == 0 or not aula.requer_conclusao_anterior:
            is_unlocked = True
        else:
            # Desbloqueada se a anterior estiver concluída
            is_unlocked = aulas[i-1].id in concluidas_ids
            
        aulas_status.append({
            'id': aula.id,
            'titulo': aula.titulo,
            'pk': aula.pk,
            'duracao_formatada': aula.duracao_formatada(),
            'is_unlocked': is_unlocked,
            'is_completed': aula.id in concluidas_ids,
            'ordem': aula.ordem,
            'requer_conclusao_anterior': aula.requer_conclusao_anterior
        })
    
    # Verificação de segurança: impedir acesso via URL a aulas bloqueadas
    aula_atual_info = next((item for item in aulas_status if item['id'] == aula_atual.id), None)
    if not aula_atual_info or not aula_atual_info['is_unlocked']:
        # Encontrar a última aula desbloqueada para redirecionar
        ultima_desbloqueada = next((item for item in reversed(aulas_status) if item['is_unlocked']), None)
        if ultima_desbloqueada:
            return redirect('cursovideoapp:ver_aula', curso_slug=curso_slug, pk=ultima_desbloqueada['pk'])
        return redirect('cursovideoapp:detalhe_curso', slug=curso_slug)

    proxima_aula = aulas.filter(ordem__gt=aula_atual.ordem).first()
    aula_anterior = aulas.filter(ordem__lt=aula_atual.ordem).last()
    
    # Calcular progresso total
    total_aulas = len(aulas_status)
    aulas_concluidas = sum(1 for item in aulas_status if item['is_completed'])
    progresso_total = int((aulas_concluidas / total_aulas) * 100) if total_aulas > 0 else 0
    
    # Obter progresso atual para controle de avanço no player
    progresso_atual, created = ProgressoAula.objects.get_or_create(aluno=aluno, aula=aula_atual)
    
    return render(request, 'cursovideo/ver_aula.html', {
        'curso': curso,
        'aula_atual': aula_atual,
        'proxima_aula': proxima_aula,
        'aula_anterior': aula_anterior,
        'aulas_status': aulas_status,
        'aulas': aulas,
        'progresso_total': progresso_total,
        'progresso_atual': progresso_atual,
    })


@login_required
def salvar_comentario_video(request, slug):
    """
    Salva ou atualiza uma avaliação (comentário) do aluno para o curso.
    """
    curso = get_object_or_404(Curso_video, slug=slug)
    
    if request.user.tipo_usuario != 'ALUNO':
        return redirect('cursovideoapp:detalhe_curso', slug=slug)
        
    try:
        aluno = request.user.aluno_profile
    except (ObjectDoesNotExist, AttributeError):
        return redirect('index')
    
    # 2. Verificar se aluno está inscrito
    if not curso.inscritos.filter(id=aluno.id).exists():
        return redirect('detalhe_curso', slug=slug)
    
    # 3. Verificar se já avaliou
    comentario_existente = Comentario.objects.filter(aluno=aluno, curso_video=curso).first()
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=comentario_existente)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.aluno = aluno
            comentario.curso_video = curso
            comentario.save()
            
    return redirect('detalhe_curso', slug=slug)

@require_POST
@login_required
def atualizar_progresso(request, aula_id):
    """
    Atualiza o tempo assistido e o status de conclusão de uma aula.
    """
    aula = get_object_or_404(Aula, id=aula_id)
    
    # Verificar se o usuário tem um perfil de aluno (pode ser admin testando)
    if not hasattr(request.user, 'aluno_profile') or not request.user.aluno_profile:
        return JsonResponse({'status': 'error', 'message': 'Perfil de aluno necessário'}, status=403)
        
    aluno = request.user.aluno_profile
    
    # Criar ou obter registro de progresso
    progresso, created = ProgressoAula.objects.get_or_create(
        aluno=aluno,
        aula=aula
    )
    
    # Receber dados do POST
    try:
        tempo_raw = request.POST.get('tempo_assistido', 0)
        tempo_assistido = int(float(tempo_raw))
        
        concluida_raw = request.POST.get('concluida', '').lower()
        concluida = concluida_raw in ['true', '1', 'on', 'yes']
        
        # Redundância de segurança no backend
        if not concluida and aula.duracao_segundos > 0:
            if (aula.duracao_segundos - tempo_assistido) < 5:
                concluida = True
        
        # Atualizar tempo assistido (armazenado em segundos) apenas se for maior
        if tempo_assistido > progresso.tempo_assistido:
            progresso.tempo_assistido = tempo_assistido
        
        if concluida:
            progresso.concluida = True
            
        progresso.save()
        
        return JsonResponse({
            'success': True,
            'progresso_percentual': progresso.progresso_percentual(),
            'concluida': progresso.concluida
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
