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