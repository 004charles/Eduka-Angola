from django.shortcuts import render
from cursos_app.models import Curso, Categoria
from django.conf import settings
from django.db.models import Count, Q

def index(request):
    # Obtém os cursos em destaque e publicados
    cursos_destaque = Curso.objects.filter(
        destaque=True, 
        publicado=True, 
        ativo=True
    ).select_related('centro').prefetch_related('instrutores')
    
    categoria = Categoria.objects.annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True)))
    
    context = {
        'categoria':categoria,
        'cursos_destaque': cursos_destaque,
        'DEBUG': settings.DEBUG, 
    }
    
    return render(request, 'core/index.html', context)


def erro_404_view(request, exception):
    return render(request, '404.html', status=404)


