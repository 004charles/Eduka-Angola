import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()
from django.urls import resolve

match = resolve('/cursos/ficha_inscricao/1/')
view = match.func
print('VIEW_MODULE=', getattr(view, '__module__', None))
print('VIEW_NAME=', getattr(view, '__name__', None))
print('VIEW_REPR=', repr(view))
print('VIEW_DICT=', getattr(view, '__dict__', {}))
print('URL_NAME=', match.url_name)
print('URL_ROUTE=', getattr(match, 'route', None))
