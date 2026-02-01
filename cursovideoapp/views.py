from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
import json
from django.urls import reverse

from cursovideoapp.models import Curso_video, Categoria, FavoritoCursoVideo, Aula, ProgressoAula

def home_videos(request):
    """
    Home page for Video Courses with rich sections.
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
        num_cursos=Count('cursos')
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
    """API to toggle favorite status for a video course"""
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
    API to load more video courses.
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
                'instrutor': curso.instrutor,
                'visualizacoes': 0, # Video model might not have views yet
                'is_favorito': curso.id in favoritos,
                # 'url_detalhe': reverse('curso_video_detalhe', args=[curso.id]) # Update with real URL name
            })
            
        return JsonResponse({'cursos': data, 'has_more': qs.count() > offset + limit})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# --- Restored Views ---

def lista_cursos(request):
    cursos = Curso_video.objects.filter(destaque=False)
    destaques = Curso_video.objects.filter(destaque=True)
    categorias = Categoria.objects.all()
    return render(request, 'cursovideo/lista_cursos.html', {
        'cursos': cursos, 
        'destaques': destaques,
        'categorias': categorias
    })

def detalhe_curso(request, slug):
    curso = get_object_or_404(Curso_video, slug=slug)
    inscrito = False
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        if curso.inscritos.filter(id=request.user.aluno_profile.id).exists():
            inscrito = True
            
    return render(request, 'cursovideo/detalhe_curso.html', {
        'curso': curso,
        'inscrito': inscrito
    })

@login_required
def toggle_inscricao(request, slug):
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

@require_POST
@login_required
def atualizar_progresso(request, aula_id):
    # Minimal implementation
    return JsonResponse({'status': 'ok'})
