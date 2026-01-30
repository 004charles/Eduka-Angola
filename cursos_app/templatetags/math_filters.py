# cursos_app/templatetags/math_filters.py
from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    """
    Divide o valor pelo argumento.
    """
    try:
        if arg == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0

@register.filter
def multiply(value, arg):
    """
    Multiplica o valor pelo argumento.
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, arg):
    """
    Subtrai o argumento do valor.
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """
    Adiciona o argumento ao valor.
    """
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return 0