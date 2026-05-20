from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('cursos_app', '0015_certificadocurso'),
    ]

    operations = [
        migrations.AddField(
            model_name='inscricao',
            name='status',
            field=models.CharField(
                choices=[
                    ('P', 'Pendente'),
                    ('A', 'Aceita'),
                    ('N', 'Negada'),
                    ('C', 'Cancelada'),
                ],
                default='P',
                max_length=1,
                verbose_name='Status',
                db_index=True,
            ),
        ),
    ]
