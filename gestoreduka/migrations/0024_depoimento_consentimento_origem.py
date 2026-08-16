from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gestoreduka', '0023_candidaturacentro_link_criado_em_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='depoimento',
            name='consentimento_publico',
            field=models.BooleanField(default=False, verbose_name='Consentimento para publicação'),
        ),
        migrations.AddField(
            model_name='depoimento',
            name='origem',
            field=models.CharField(choices=[('GESTOR', 'Adicionado por gestor'), ('ALUNO', 'Submetido por aluno')], default='GESTOR', max_length=12, verbose_name='Origem'),
        ),
        migrations.AddField(
            model_name='depoimento',
            name='publicar_nome',
            field=models.BooleanField(default=False, verbose_name='Mostrar nome completo publicamente'),
        ),
    ]
