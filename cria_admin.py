import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from usuarios.models import Usuario

email = 'admin@edukangola.com'
nome = 'Administrador'
password = 'admin' # Altere conforme necessário

try:
    if not Usuario.objects.filter(email=email).exists():
        Usuario.objects.create_superuser(email=email, nome=nome, password=password)
        print(f"Sucesso! Utilizador {email} criado com a senha: {password}")
    else:
        print(f"O utilizador {email} já existe.")
except Exception as e:
    print(f"Erro ao criar superutilizador: {e}")
