import django
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from pagamentos.services import get_payment_service
from decimal import Decimal

print('Testando servico de pagamentos...')
try:
    servico = get_payment_service()
    print('Gateway: ' + servico.config.gateway_padrao)
    print('Pagamentos ativados: ' + str(servico.config.pagamentos_ativados))
    
    # Verificar se mock mode esta ativo
    from decouple import config as dc
    mock_val = dc('GATEWAY_MOCK', default='False')
    print('GATEWAY_MOCK no .env: ' + str(mock_val))
    
    result = servico.gateway_atual.criar_transacao(
        referencia_pagamento='PAG-TEST-001',
        usuario_nome='Teste Usuario',
        usuario_email='teste@teste.com',
        usuario_telefone='244923456789',
        valor=Decimal('1000.00'),
        moeda='AOA',
        descricao='Teste Pagamento',
        url_callback='http://localhost:8000/webhook/',
        url_retorno='http://localhost:8000/sucesso/',
        url_cancelamento='http://localhost:8000/cancelado/',
    )
    print('SUCESSO! Resultado:')
    print('  referencia_gateway: ' + str(result.get('referencia_gateway')))
    print('  url_pagamento: ' + str(result.get('url_pagamento')))
    print('  status: ' + str(result.get('status')))
except Exception as e:
    import traceback
    print('ERRO: ' + type(e).__name__ + ': ' + str(e))
    traceback.print_exc()
