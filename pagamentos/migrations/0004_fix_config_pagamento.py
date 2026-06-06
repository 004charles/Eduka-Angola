import django.core.validators
from django.db import migrations, models
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError

def add_columns_safely(apps, schema_editor):
    ConfiguracaoPagamento = apps.get_model('pagamentos', 'ConfiguracaoPagamento')
    
    fields_to_add = [
        ('max_tentativas_webhook', models.PositiveIntegerField(default=5, verbose_name='Máximo de Tentativas de Webhook')),
        ('max_tentativas_pagamento', models.PositiveIntegerField(default=3, verbose_name='Máximo de Tentativas')),
        ('tempo_confirmacao_automatica_minutos', models.PositiveIntegerField(default=5, help_text='Aguarda este tempo para confirmar pagamento antes de expirar', verbose_name='Tempo para Confirmação Automática (minutos)')),
        ('desconto_inscricao_percentual', models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Desconto na Inscrição (%)')),
        ('notificar_admin_pagamento_recebido', models.BooleanField(default=True, verbose_name='Notificar Admin ao Receber Pagamento')),
        ('exigir_verificacao_email', models.BooleanField(default=True, verbose_name='Exigir Verificação de Email')),
        ('exigir_cpf_valido', models.BooleanField(default=False, verbose_name='Exigir CPF/NIF Válido')),
        ('tempo_expiracao_link_minutos', models.PositiveIntegerField(default=30, help_text='Quanto tempo o link de pagamento fica válido', verbose_name='Tempo de Expiração do Link (minutos)')),
        ('gateway_padrao', models.CharField(choices=[('PRONTU', 'Prontu'), ('STRIPE', 'Stripe'), ('PAYPAL', 'PayPal')], default='PRONTU', max_length=50, verbose_name='Gateway Padrão')),
        ('moeda_padrao', models.CharField(choices=[('AOA', 'Kwanza (AOA)'), ('EUR', 'Euro (EUR)'), ('USD', 'Dólar (USD)')], default='AOA', max_length=3, verbose_name='Moeda Padrão')),
        ('pagamentos_ativados', models.BooleanField(default=True, verbose_name='Pagamentos Ativados')),
    ]
    
    for field_name, field_instance in fields_to_add:
        try:
            with transaction.atomic():
                field_instance.set_attributes_from_name(field_name)
                schema_editor.add_field(ConfiguracaoPagamento, field_instance)
        except (OperationalError, ProgrammingError):
            # O campo já existe (ignorar erro silenciosamente para ser idempotente)
            pass

class Migration(migrations.Migration):
    # Definido como não atómico porque algumas bases de dados (como PostgreSQL) não permitem
    # modificações no schema dentro de blocos atómicos quando a intenção é capturar excepções.
    atomic = False

    dependencies = [
        ('pagamentos', '0003_alter_pagamento_tipo_pagamento'),
    ]

    operations = [
        migrations.RunPython(add_columns_safely),
    ]
