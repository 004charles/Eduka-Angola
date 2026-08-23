from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_adminauditlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clienteapikey',
            name='nome_cliente',
            field=models.CharField(help_text='Ex: Site parceiro ou integração institucional.', max_length=150, unique=True, verbose_name='Nome do Cliente / Site'),
        ),
    ]
