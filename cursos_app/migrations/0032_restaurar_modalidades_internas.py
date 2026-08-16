from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cursos_app', '0031_simplificar_modalidade_presencial'),
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
                default='PRESENCIAL',
                max_length=10,
            ),
        ),
    ]
