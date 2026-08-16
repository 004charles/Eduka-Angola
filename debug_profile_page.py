import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()
from django.test import Client
html = Client().get('/cursos/centro/1/cursos/').content.decode('utf-8')
for line_no, line in enumerate(html.splitlines(), 1):
    if '120' in line:
        print(f'{line_no}: {line.strip()[:300]}')
