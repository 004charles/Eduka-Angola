import os
from decimal import Decimal
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from django.db import transaction
from django.utils import timezone
from gestoreduka.models import CentroDeFormacao
from planos.models import Plano, AssinaturaMembro
from pagamentos.models import Pagamento
from pagamentos.services import PaymentService


class RollbackTest(Exception):
    pass


try:
    with transaction.atomic():
        centro = CentroDeFormacao.objects.get(pk=1)
        plano = Plano.objects.create(
            nome='__TESTE_PLANO__',
            descricao='Plano temporário de teste',
            preco=Decimal('1000.00'),
            limite_cursos=5,
            ativo=True,
        )
        assinatura = AssinaturaMembro.objects.create(
            centro=centro,
            plano=None,
            status='PENDENTE',
        )
        pagamento = Pagamento.objects.create(
            referencia_pagamento='TEST-ASSINATURA-IDEMPOTENTE',
            usuario=centro.usuario,
            tipo_pagamento='ASSINATURA_PLANO',
            plano=plano,
            moeda='AOA',
            valor=Decimal('1000.00'),
            valor_final=Decimal('1000.00'),
            gateway='PRONTU',
            status='ACCEPTED',
        )

        service = PaymentService()
        service._enviar_email_confirmacao = lambda _pagamento: None
        service._notificar_admin = lambda _pagamento: None
        service.config.notificar_admin_pagamento_recebido = False

        service._processar_pagamento_aceito(pagamento)
        assinatura.refresh_from_db()
        pagamento.refresh_from_db()
        primeira_data_fim = assinatura.data_fim

        assert assinatura.status == 'ATIVO', assinatura.status
        assert assinatura.plano_id == plano.id
        assert assinatura.esta_ativa is True
        assert primeira_data_fim is not None
        assert pagamento.metadados.get('assinatura_ativada_em')

        service._processar_pagamento_aceito(pagamento)
        assinatura.refresh_from_db()
        assert assinatura.data_fim == primeira_data_fim

        print('PASS: assinatura ativada com estado ATIVO')
        print('PASS: relação centro.usuario utilizada')
        print('PASS: data de validade criada como DateTime')
        print('PASS: repetição do pós-processamento não prolonga a assinatura duas vezes')
        raise RollbackTest()
except RollbackTest:
    pass
