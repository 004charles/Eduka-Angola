from django.conf import settings
from cursos_app.models import Curso

def languages(request):
    return {
        'LANGUAGES': settings.LANGUAGES,
        'CURRENT_LANGUAGE': request.LANGUAGE_CODE,
    }

def destaques(request):
    """
    Disponibiliza os cursos em destaque em todos os templates.
    Útil para componentes globais como o modal de pesquisa do cabeçalho.
    """
    return {
        'destaques_global': Curso.objects.filter(
            destaque=True, 
            publicado=True, 
            ativo=True
        ).select_related('centro')[:5]
    }

def google_maps_key(request):
    """
    Disponibiliza a chave da API do Google Maps para os templates.
    """
    return {
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    }