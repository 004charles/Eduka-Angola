# Migration to add tempo_confirmacao_automatica_minutos column
# that was missing from the production database schema.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracaopagamento',
            name='tempo_confirmacao_automatica_minutos',
            field=models.PositiveIntegerField(
                default=5,
                help_text='Aguarda este tempo para confirmar pagamento antes de expirar',
                verbose_name='Tempo para Confirmação Automática (minutos)'
            ),
        ),
    ]
