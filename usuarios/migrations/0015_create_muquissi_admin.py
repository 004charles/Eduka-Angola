from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    Usuario = apps.get_model('usuarios', 'Usuario')
    email = 'muquissicarlos@gmail.com'
    nome = 'Muquissi Carlos'
    
    # Verifica se já existe um usuário com este e-mail para evitar erros em futuros deploys
    if not Usuario.objects.filter(email=email).exists():
        Usuario.objects.create(
            email=email,
            nome=nome,
            password=make_password('edukaadmin123'),  # Senha temporária 
            is_superuser=True,
            is_staff=True,
            is_active=True,
            tipo_usuario='ADMIN'
        )

class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0014_perfilaluno_foto_de_capa'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
