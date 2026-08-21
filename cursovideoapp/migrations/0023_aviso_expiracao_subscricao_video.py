from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('cursovideoapp', '0022_subscricao_video_aluno'),
        ('usuarios', '0019_preferencianotificacaoaluno_receber_push_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvisoExpiracaoSubscricaoVideo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('antecedencia_horas', models.PositiveSmallIntegerField(verbose_name='Antecedência em horas')),
                ('email_processado_em', models.DateTimeField(blank=True, null=True, verbose_name='E-mail processado em')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('assinatura', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avisos_expiracao', to='cursovideoapp.assinaturavideoaluno')),
                ('notificacao', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aviso_subscricao_video', to='usuarios.notificacaoaluno')),
            ],
            options={'verbose_name': 'Aviso de expiração de subscrição de vídeo', 'verbose_name_plural': 'Avisos de expiração de subscrições de vídeo', 'ordering': ['-criado_em']},
        ),
        migrations.AddConstraint(
            model_name='avisoexpiracaosubscricaovideo',
            constraint=models.UniqueConstraint(fields=('assinatura', 'antecedencia_horas'), name='aviso_video_subscricao_unico_por_janela'),
        ),
    ]
