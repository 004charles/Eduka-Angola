import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from decouple import config as dc

mock_val = dc('GATEWAY_MOCK', default='False')
api_key = dc('PRONTU_API_KEY', default='')
api_url = dc('PRONTU_API_URL', default='')

print('=== Configuracao Prontu ===')
print('GATEWAY_MOCK: ' + str(mock_val))
print('PRONTU_API_URL: ' + api_url)
print('API KEY (primeiros 30 chars): ' + api_key[:30] + '...')
print()

# Testar chamada real a API do Prontu
import requests
headers = {
    'Content-Type': 'application/json',
    'Authorization': api_key,
    'User-Agent': 'EdukAngola/1.0'
}

print('Testando conectividade com API Prontu...')
try:
    # Tentar endpoint de saude/status
    resp = requests.get(api_url + '/v1/hosts/transactions-receive', headers=headers, timeout=10)
    print('Status HTTP: ' + str(resp.status_code))
    print('Resposta: ' + resp.text[:300])
except requests.ConnectionError as e:
    print('Erro de conexao: ' + str(e))
except requests.Timeout:
    print('Timeout - API nao respondeu em 10s')
except Exception as e:
    print('Erro: ' + str(e))

print()
print('Testando criacao de transacao mock...')
try:
    from pagamentos.services import ProntuPaymentGateway
    from decimal import Decimal
    from django.conf import settings

    gateway = ProntuPaymentGateway(api_url, api_key)
    
    payload = {
        'currency': 'AOA',
        'phone': '244923456789',
        'email': 'teste@edukangola.ao',
        'reference_id': 'PAG-TEST-REAL-001',
        'first_name': 'Teste',
        'last_name': 'Eduka',
        'amount': 1000.00,
        'cancel_url': 'http://localhost:8000/cancelado/',
        'return_url': 'http://localhost:8000/sucesso/',
        'expiration_date': '2026-12-31T23:59:59Z',
        'source': 0,
    }
    
    resp2 = requests.post(api_url + '/v1/hosts/transactions-receive', json=payload, headers=headers, timeout=15)
    print('Status HTTP: ' + str(resp2.status_code))
    print('Resposta: ' + resp2.text[:500])
except Exception as e:
    import traceback
    print('Erro: ' + str(e))
    traceback.print_exc()
