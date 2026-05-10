from django import template

register = template.Library()

@register.filter(name='avaliacao_count')
def avaliacao_count(comentarios, rating):
    try:
        rating_int = int(rating)
        count = 0
        for comentario in comentarios:
            if comentario.avaliacao == rating_int:
                count += 1
        return count
    except (ValueError, TypeError):
        return 0

@register.filter(name='divide')
def divide(value, arg):
    """Divide o valor pelo argumento"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiplica o valor pelo argumento"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name='get_rating_count')
def get_rating_count(comentarios, rating):
    """Alias para avaliacao_count"""
    return avaliacao_count(comentarios, rating)

@register.filter(name='is_favorited_by')
def is_favorited_by(curso, user):
    from cursos_app.models import Favorito
    from cursovideoapp.models import FavoritoCursoVideo

    if not user.is_authenticated:
        return False
    
    # Check if user has an aluno profile
    if not hasattr(user, 'aluno_profile'):
        return False
        
    aluno = user.aluno_profile
    
    # Detect model type
    model_name = curso.__class__.__name__
    
    if model_name == 'Curso':
        return Favorito.objects.filter(aluno=aluno, curso=curso).exists()
    elif model_name == 'Curso_video':
        return FavoritoCursoVideo.objects.filter(aluno=aluno, curso=curso).exists()
        
    return False

@register.filter
def model_type(obj):
    return obj.__class__.__name__

@register.filter
def get_item(dictionary, key):
    if dictionary:
        return dictionary.get(key)
    return None

@register.filter(name='formata_kz')
def formata_kz(value):
    """Formata o valor para o padrão Angolano: 10.000 (3 casas após o ponto)"""
    try:
        val = float(value)
        # Formata com separador de milhar sendo vírgula, depois troca por ponto
        # Isso garante que 10000 vire 10.000
        return "{:,.0f}".format(val).replace(',', '.')
    except (ValueError, TypeError):
        return value