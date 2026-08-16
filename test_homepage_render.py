import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

client = Client()
response = client.get('/')
assert response.status_code == 200, response.status_code
html = response.content.decode('utf-8')
assert '1 248' not in html
assert 'Ver os 312 cursos' not in html
assert 'Ver os 164 cursos' not in html
assert 'Ver os 214 cursos internacionais' not in html
assert '142 instituições certificadas' not in html
assert 'Pague o seu curso em 6 prestações sem juros' not in html
assert 'British Language Centre · Luanda' not in html
assert 'Bem-vindo, Gestor Demo Eduka-Angola' not in html

User = get_user_model()
try:
    gestor = User.objects.get(email='gestor.demo@eduka-angola.test')
except User.DoesNotExist:
    gestor = None
if gestor is not None:
    client.force_login(gestor)
    authenticated_html = client.get('/').content.decode('utf-8')
    assert 'Bem-vindo, Gestor Demo Eduka-Angola' not in authenticated_html

print('PASS: homepage renderiza para visitante anónimo')
print('PASS: números fixos e promessas não verificadas removidos')
print('PASS: saudação da conta demo não aparece para visitante')
