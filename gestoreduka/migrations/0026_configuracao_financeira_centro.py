from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gestoreduka', '0025_remove_feed_reels'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracaoFinanceiraCentro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('moeda_apresentacao', models.CharField(choices=[('AOA', 'Kwanza (AOA)'), ('EUR', 'Euro (EUR)'), ('USD', 'Dólar norte-americano (USD)'), ('MZN', 'Metical moçambicano (MZN)'), ('XOF', 'Franco CFA da África Ocidental (XOF)'), ('CVE', 'Escudo cabo-verdiano (CVE)'), ('BRL', 'Real brasileiro (BRL)'), ('STN', 'Dobra são-tomense (STN)')], max_length=3, verbose_name='Moeda apresentada ao aluno')),
                ('moeda_cobranca', models.CharField(choices=[('AOA', 'Kwanza (AOA)'), ('EUR', 'Euro (EUR)'), ('USD', 'Dólar norte-americano (USD)'), ('MZN', 'Metical moçambicano (MZN)'), ('XOF', 'Franco CFA da África Ocidental (XOF)'), ('CVE', 'Escudo cabo-verdiano (CVE)'), ('BRL', 'Real brasileiro (BRL)'), ('STN', 'Dobra são-tomense (STN)')], max_length=3, verbose_name='Moeda efectiva de cobrança')),
                ('gateway', models.CharField(choices=[('PRONTU', 'Prontu'), ('PENDENTE', 'A definir pela Edukangola')], default='PENDENTE', max_length=20, verbose_name='Gateway de cobrança')),
                ('estado', models.CharField(choices=[('PENDENTE_VALIDACAO', 'A aguardar validação da Edukangola'), ('ACTIVA', 'Activa para cobrança'), ('SUSPENSA', 'Suspensa')], db_index=True, default='PENDENTE_VALIDACAO', max_length=24, verbose_name='Estado de activação')),
                ('validado_em', models.DateTimeField(blank=True, null=True)),
                ('observacao_validacao', models.CharField(blank=True, max_length=300, verbose_name='Observação da Edukangola')),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('centro', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='configuracao_financeira', to='gestoreduka.centrodeformacao')),
                ('validado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='configuracoes_financeiras_validadas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Configuração financeira do centro',
                'verbose_name_plural': 'Configurações financeiras dos centros',
            },
        ),
    ]
