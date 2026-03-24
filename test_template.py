import os
import django
from django.test import Client
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

try:
    c = Client()
    response = c.get('/cursos/curso/3/')
    print("Success:", response.status_code)
except Exception as e:
    import traceback
    traceback.print_exc()
