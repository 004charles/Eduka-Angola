import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()
from django.test import Client
from django.urls import reverse
from usuarios.models import Usuario

email = 'aluno.demo@eduka-angola.test'
password = 'EdukaAluno#2026'
client = Client()
login_ok = client.login(email=email, password=password)
print('LOGIN=', login_ok)
url = reverse('aluno_dashboard')
response = client.get(url)
print(f'DASHBOARD={url}|status={response.status_code}|redirect={response.url if response.status_code in (301,302,303,307,308) else ""}')
user = Usuario.objects.get(email=email)
print(f'USUARIO={user.id}|tipo={user.tipo_usuario}|ativo={user.is_active}|nome={user.nome}')
