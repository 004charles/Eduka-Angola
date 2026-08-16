from django.db import migrations, models


def converter_modalidades_para_presencial(apps, schema_editor):
    Curso = apps.get_model('cursos_app', 'Curso')
    Curso.objects.filter(modalidade__in=['ONLINE', 'HIBRIDO']).update(modalidade='PRESENCIAL')


class Migration(migrations.Migration):

    dependencies = [
        ('cursos_app', '0030_alter_curso_tipo_cobranca_inscricao'),
    ]

    operations = [
        migrations.RunPython(converter_modalidades_para_presencial, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='curso',
            name='modalidade',
            field=models.CharField(choices=[('PRESENCIAL', 'Presencial')], default='PRESENCIAL', max_length=20),
        ),
    ]
