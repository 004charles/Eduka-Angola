from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
import json
from django.urls import reverse

from cursos_app.models import Categoria, Instrutor
from cursovideoapp.models import Curso_video, FavoritoCursoVideo, Aula, ProgressoAula
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
    
    # Categories for filter
    categorias = Categoria.objects.annotate(
        num_cursos=Count('cursos_video')
    ).filter(num_cursos__gt=0).order_by('nome')
    
    context = {
        'videos_recentes': videos_recentes,
        'videos_populares': videos_populares,
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
        except AttributeError:
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
        aluno = request.user.aluno_profile
        
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
             favoritos = list(FavoritoCursoVideo.objects.filter(
                 aluno=request.user.aluno_profile, 
                 curso__in=cursos
             ).values_list('curso_id', flat=True))

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
        except AttributeError:
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
    })

@login_required
def toggle_inscricao(request, slug):
    """
    Inscreve ou remove a inscrição de um aluno em um curso.
    """
    curso = get_object_or_404(Curso_video, slug=slug)
    if request.user.tipo_usuario != 'ALUNO':
        # Handle non-student logic
        return redirect('detalhe_curso', slug=slug)
        
    aluno = request.user.aluno_profile
    if curso.inscritos.filter(id=aluno.id).exists():
        curso.inscritos.remove(aluno)
    else:
        curso.inscritos.add(aluno)
    return redirect('detalhe_curso', slug=slug)

@login_required
def ver_aula(request, curso_slug, pk):
    """
    Interface de visualização de uma aula específica do curso.
    """
    curso = get_object_or_404(Curso_video, slug=curso_slug)
    aula_atual = get_object_or_404(Aula, pk=pk, curso=curso)
    
    # Check enrollment
    if not curso.inscritos.filter(id=request.user.aluno_profile.id).exists():
        return redirect('detalhe_curso', slug=curso_slug)
    
    aulas = curso.aulas.all().order_by('ordem')
    
    # Get previous/next
    proxima_aula = aulas.filter(ordem__gt=aula_atual.ordem).first()
    aula_anterior = aulas.filter(ordem__lt=aula_atual.ordem).last()
    
    return render(request, 'cursovideo/ver_aula.html', {
        'curso': curso,
        'aula_atual': aula_atual,
        'proxima_aula': proxima_aula,
        'aula_anterior': aula_anterior,
        'aulas': aulas
    })

@login_required
def salvar_comentario_video(request, slug):
    """
    Salva ou atualiza uma avaliação (comentário) do aluno para o curso.
    """
    curso = get_object_or_404(Curso_video, slug=slug)
    
    # 1. Obter aluno
    if request.user.tipo_usuario != 'ALUNO':
        return redirect('detalhe_curso', slug=slug)
        
    aluno = request.user.aluno_profile
    
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
    
    if request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'status': 'error', 'message': 'Não autorizado'}, status=403)
        
    aluno = request.user.aluno_profile
    
    # Criar ou obter registro de progresso
    progresso, created = ProgressoAula.objects.get_or_create(
        aluno=aluno,
        aula=aula
    )
    
    # Receber dados do POST
    try:
        tempo_assistido = float(request.POST.get('tempo_assistido', 0))
        concluida = request.POST.get('concluida') == 'true'
        
        # Atualizar tempo assistido (armazenado em segundos)
        progresso.tempo_assistido = int(tempo_assistido)
        
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
