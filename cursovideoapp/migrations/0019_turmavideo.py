from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cursovideoapp', '0018_curso_video_is_original_edukangola'),
    ]

    operations = [
        migrations.CreateModel(
            name='TurmaVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, verbose_name='Nome da Turma')),
                ('codigo', models.CharField(max_length=30, unique=True, verbose_name='Código da Turma')),
                ('data_inicio', models.DateField(verbose_name='Data de Início')),
                ('data_fim', models.DateField(blank=True, null=True, verbose_name='Data de Término')),
                ('turno', models.CharField(choices=[('MANHA', 'Manhã'), ('TARDE', 'Tarde'), ('NOITE', 'Noite'), ('INTEGRAL', 'Integral'), ('SABADO', 'Sábado')], default='NOITE', max_length=10, verbose_name='Turno')),
                ('horario_inicio', models.TimeField(blank=True, null=True, verbose_name='Horário de Início')),
                ('horario_fim', models.TimeField(blank=True, null=True, verbose_name='Horário de Fim')),
                ('dias_semana', models.CharField(blank=True, max_length=100, verbose_name='Dias da Semana')),
                ('vagas_totais', models.PositiveIntegerField(default=0, verbose_name='Vagas Totais')),
                ('vagas_ocupadas', models.PositiveIntegerField(default=0, verbose_name='Vagas Ocupadas')),
                ('vagas_disponiveis', models.PositiveIntegerField(default=0, verbose_name='Vagas Disponíveis')),
                ('status', models.CharField(choices=[('ABERTA', 'Aberta'), ('EM_ANDAMENTO', 'Em andamento'), ('CONCLUIDA', 'Concluída'), ('CANCELADA', 'Cancelada')], db_index=True, default='ABERTA', max_length=20, verbose_name='Status')),
                ('observacoes', models.TextField(blank=True, verbose_name='Observações')),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('data_atualizacao', models.DateTimeField(auto_now=True)),
                ('curso', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='turmas', to='cursovideoapp.curso_video')),
            ],
            options={
                'verbose_name': 'Turma de Vídeo-Curso',
                'verbose_name_plural': 'Turmas de Vídeo-Curso',
                'ordering': ['data_inicio', 'turno'],
                'unique_together': {('curso', 'codigo')},
            },
        ),
    ]
