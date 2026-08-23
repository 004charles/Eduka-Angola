from django.db import migrations, models


def criar_modulos(apps, schema_editor):
    ModuloPublico = apps.get_model('gestoreduka', 'ModuloPublico')
    for chave, ordem in [('ESCOLAS', 110), ('ESTAGIOS', 120)]:
        ModuloPublico.objects.get_or_create(chave=chave, defaults={'ativo': False, 'ordem': ordem})


class Migration(migrations.Migration):
    dependencies = [('gestoreduka', '0027_modulo_publico')]
    operations = [
        migrations.AlterField(
            model_name='modulopublico',
            name='chave',
            field=models.CharField(choices=[('BOLSAS', 'Bolsas de estudo'), ('ESCOLAS', 'Escolas'), ('ESTAGIOS', 'Estágios')], max_length=40, unique=True, verbose_name='Módulo'),
        ),
        migrations.RunPython(criar_modulos, migrations.RunPython.noop),
    ]
