from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos_app', '0032_restaurar_modalidades_internas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curso',
            name='modalidade',
            field=models.CharField(
                choices=[
                    ('PRESENCIAL', 'Presencial'),
                    ('ONLINE', 'Online'),
                    ('HIBRIDO', 'Híbrido'),
                ],
                db_index=True,
                default='PRESENCIAL',
                max_length=10,
                verbose_name='Modalidade',
            ),
        ),
    ]
