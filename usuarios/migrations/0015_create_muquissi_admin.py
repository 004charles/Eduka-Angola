from django.db import migrations

def create_superuser(apps, schema_editor):
    """Não criar administradores automaticamente em migrations.

    Contas administrativas devem ser criadas no ambiente de destino por um
    operador autorizado, com credencial única e rotação obrigatória.
    """
    return

class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0014_perfilaluno_foto_de_capa'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
