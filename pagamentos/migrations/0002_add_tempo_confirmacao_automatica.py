# Migration para sincronizar todos os campos em falta na tabela
# pagamentos_configuracaopagamento em producao.
#
# Usa ADD COLUMN IF NOT EXISTS para ser 100% seguro e idempotente:
# nao falha se a coluna ja existir.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pagamentos', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE pagamentos_configuracaopagamento
                    ADD COLUMN IF NOT EXISTS tempo_confirmacao_automatica_minutos integer NOT NULL DEFAULT 5,
                    ADD COLUMN IF NOT EXISTS max_tentativas_pagamento integer NOT NULL DEFAULT 3,
                    ADD COLUMN IF NOT EXISTS max_tentativas_webhook integer NOT NULL DEFAULT 5,
                    ADD COLUMN IF NOT EXISTS desconto_inscricao_percentual numeric(5,2) NOT NULL DEFAULT 0,
                    ADD COLUMN IF NOT EXISTS notificar_admin_pagamento_recebido boolean NOT NULL DEFAULT true,
                    ADD COLUMN IF NOT EXISTS exigir_verificacao_email boolean NOT NULL DEFAULT true,
                    ADD COLUMN IF NOT EXISTS exigir_cpf_valido boolean NOT NULL DEFAULT false,
                    ADD COLUMN IF NOT EXISTS tempo_expiracao_link_minutos integer NOT NULL DEFAULT 30,
                    ADD COLUMN IF NOT EXISTS gateway_padrao varchar(50) NOT NULL DEFAULT 'PRONTU',
                    ADD COLUMN IF NOT EXISTS moeda_padrao varchar(3) NOT NULL DEFAULT 'AOA',
                    ADD COLUMN IF NOT EXISTS pagamentos_ativados boolean NOT NULL DEFAULT true;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
