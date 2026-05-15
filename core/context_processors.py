from django.conf import settings
from cursos_app.models import Curso

def languages(request):
    return {
        'LANGUAGES': settings.LANGUAGES,
        'CURRENT_LANGUAGE': request.LANGUAGE_CODE,
    }

from django.core.cache import cache

def destaques(request):
    """
    Disponibiliza os cursos em destaque em todos os templates.
    Útil para componentes globais como o modal de pesquisa do cabeçalho.
    """
    cache_key = 'destaques_global'
    destaques_data = cache.get(cache_key)
    
    if destaques_data is None:
        destaques_data = list(Curso.objects.filter(
            destaque=True, 
            publicado=True, 
            ativo=True
        ).select_related('centro')[:5])
        cache.set(cache_key, destaques_data, 900)  # 15 minutos
        
    return {
        'destaques_global': destaques_data
    }

def google_maps_key(request):
    """
    Disponibiliza a chave da API do Google Maps para os templates.
    """
    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }