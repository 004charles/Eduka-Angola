from django.db import migrations, models


def criar_modulo_bolsas(apps, schema_editor):
    ModuloPublico = apps.get_model('gestoreduka', 'ModuloPublico')
    ModuloPublico.objects.get_or_create(chave='BOLSAS', defaults={'ativo': False, 'ordem': 100})


class Migration(migrations.Migration):

    dependencies = [
        ('gestoreduka', '0026_configuracao_financeira_centro'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuloPublico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chave', models.CharField(choices=[('BOLSAS', 'Bolsas de estudo')], max_length=40, unique=True, verbose_name='Módulo')),
                ('ativo', models.BooleanField(db_index=True, default=False, verbose_name='Visível e disponível no site')),
                ('ordem', models.PositiveSmallIntegerField(default=100, verbose_name='Ordem no menu')),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Módulo público',
                'verbose_name_plural': 'Módulos públicos',
                'ordering': ('ordem', 'chave'),
            },
        ),
        migrations.RunPython(criar_modulo_bolsas, migrations.RunPython.noop),
    ]
