"""
CHECKLIST DE INTEGRAÇÃO - SISTEMA DE PAGAMENTOS
================================================

Este arquivo documenta como validar e configurar o sistema de pagamentos.
Execute este script ou siga manualmente os passos abaixo.
"""

import os
import sys
from pathlib import Path

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(status, message):
    """Imprime mensagem de status colorida"""
    symbol = '✓' if status else '✗'
    color = GREEN if status else RED
    print(f"{color}{symbol}{RESET} {message}")

def check_env_variables():
    """Verifica variáveis de ambiente necessárias"""
    print(f"\n{BLUE}=== VERIFICANDO VARIÁVEIS DE AMBIENTE ==={RESET}")
    
    required_vars = {
        'PAGAMENTOS_ATIVADOS': 'True',
        'GATEWAY_PADRAO': 'PRONTU',
        'MOEDA_PADRAO': 'AOA',
        'PRONTU_API_URL': 'https://api.prontu.io',
        'PRONTU_API_KEY': 'deve-ser-substituido',
        'PRONTU_CALLBACK_URL': 'http://localhost:8000/api/v1/pagamentos/webhook/prontu/',
        'FRONTEND_RETURN_URL': 'http://localhost:3000/pagamento/sucesso',
        'FRONTEND_CANCEL_URL': 'http://localhost:3000/pagamento/cancelado',
        'TEMPO_EXPIRACAO_LINK_MINUTOS': '120',
        'MAX_TENTATIVAS_PAGAMENTO': '3',
        'DEFAULT_FROM_EMAIL': 'nao-responda@edukangola.ao',
        'SITE_DOMAIN': 'http://localhost:8000',
    }
    
    env_file = Path('.env')
    if not env_file.exists():
        print_status(False, ".env não encontrado!")
        return False
    
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    all_present = True
    for var, expected in required_vars.items():
        is_present = var in env_content
        print_status(is_present, f"{var}")
        if not is_present:
            all_present = False
    
    return all_present

def check_django_settings():
    """Verifica se settings.py está configurado"""
    print(f"\n{BLUE}=== VERIFICANDO DJANGO SETTINGS ==={RESET}")
    
    settings_file = Path('eduangolacore/settings.py')
    if not settings_file.exists():
        print_status(False, "settings.py não encontrado!")
        return False
    
    with open(settings_file, 'r') as f:
        settings_content = f.read()
    
    checks = {
        "'pagamentos' in INSTALLED_APPS": "'pagamentos'" in settings_content,
        "PRONTU_API_URL configurado": "PRONTU_API_URL = os.getenv" in settings_content,
        "PRONTU_API_KEY configurado": "PRONTU_API_KEY = os.getenv" in settings_content,
        "FRONTEND_RETURN_URL configurado": "FRONTEND_RETURN_URL = os.getenv" in settings_content,
        "FRONTEND_CANCEL_URL configurado": "FRONTEND_CANCEL_URL = os.getenv" in settings_content,
    }
    
    all_ok = True
    for check, result in checks.items():
        print_status(result, check)
        if not result:
            all_ok = False
    
    return all_ok

def check_urls_configured():
    """Verifica se URLs foram registradas"""
    print(f"\n{BLUE}=== VERIFICANDO URLS ==={RESET}")
    
    urls_file = Path('eduangolacore/urls.py')
    if not urls_file.exists():
        print_status(False, "urls.py não encontrado!")
        return False
    
    with open(urls_file, 'r') as f:
        urls_content = f.read()
    
    is_present = "path('api/v1/pagamentos/'" in urls_content
    print_status(is_present, "Rota /api/v1/pagamentos/ registrada")
    
    return is_present

def check_app_structure():
    """Verifica estrutura do app pagamentos"""
    print(f"\n{BLUE}=== VERIFICANDO ESTRUTURA DO APP ==={RESET}")
    
    required_files = [
        'pagamentos/__init__.py',
        'pagamentos/models.py',
        'pagamentos/admin.py',
        'pagamentos/services.py',
        'pagamentos/serializers.py',
        'pagamentos/views.py',
        'pagamentos/urls.py',
        'pagamentos/apps.py',
        'pagamentos/migrations/0001_initial.py',
    ]
    
    all_present = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_status(exists, file_path)
        if not exists:
            all_present = False
    
    return all_present

def check_database():
    """Verifica se migrações foram aplicadas"""
    print(f"\n{BLUE}=== VERIFICANDO BANCO DE DADOS ==={RESET}")
    
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
        django.setup()
        
        from django.core.management import call_command
        from django.db import connections
        from django.db.migrations.loader import MigrationLoader
        
        db = connections.databases['default']
        loader = MigrationLoader(None, ignore_no_migrations=True)
        
        # Verificar se pagamentos está registrado
        from django.apps import apps
        pagamentos_app = apps.get_app_config('pagamentos')
        print_status(True, f"App 'pagamentos' registrado: {pagamentos_app.name}")
        
        # Verificar migrações
        pagamentos_migrations = [m for m in loader.disk_migrations.keys() if m[0] == 'pagamentos']
        print_status(len(pagamentos_migrations) > 0, f"Migrações encontradas: {len(pagamentos_migrations)}")
        
        # Verificar modelos
        from pagamentos.models import Pagamento, HistoricoPagamento, ConfiguracaoPagamento
        print_status(True, "Modelos carregados com sucesso")
        
        return True
    except Exception as e:
        print_status(False, f"Erro ao verificar banco: {str(e)}")
        return False

def print_configuration_guide():
    """Imprime guia de configuração"""
    print(f"\n{BLUE}=== GUIA DE CONFIGURAÇÃO .ENV ==={RESET}\n")
    
    guide = """
VARIÁVEIS ESSENCIAIS:

1. Ativação do Sistema
   PAGAMENTOS_ATIVADOS=True         # Ativar/desativar pagamentos

2. Gateway Principal  
   GATEWAY_PADRAO=PRONTU            # PRONTU, STRIPE, PAYPAL
   MOEDA_PADRAO=AOA                 # Moeda padrão

3. Credenciais Prontu (OBRIGATÓRIO - alterar em produção!)
   PRONTU_API_URL=https://api.prontu.io
   PRONTU_API_KEY=sua_chave_api_aqui    # ⚠️ ALTERAR ESTE VALOR
   PRONTU_CALLBACK_URL=http://localhost:8000/api/v1/pagamentos/webhook/prontu/

4. URLs de Redirecionamento (Frontend)
   FRONTEND_RETURN_URL=http://localhost:3000/pagamento/sucesso
   FRONTEND_CANCEL_URL=http://localhost:3000/pagamento/cancelado

5. Configurações de Pagamento
   TEMPO_EXPIRACAO_LINK_MINUTOS=120    # Link expira após 2h
   MAX_TENTATIVAS_PAGAMENTO=3           # Máximo de tentativas
   DESCONTO_INSCRICAO_PERCENTUAL=0      # Desconto (0-100%)

6. Notificações
   NOTIFICAR_ADMIN_PAGAMENTO_RECEBIDO=True
   VALIDAR_WEBHOOK_SIGNATURE=True

7. Email
   DEFAULT_FROM_EMAIL=nao-responda@edukangola.ao
   SITE_DOMAIN=http://localhost:8000

INSTRUÇÕES PARA PRODUÇÃO:
1. Alterar PRONTU_API_KEY com credenciais reais
2. Alterar FRONTEND_RETURN_URL e FRONTEND_CANCEL_URL para domínio real
3. Alterar SITE_DOMAIN para domínio em produção
4. Alterar PRONTU_CALLBACK_URL para domínio em produção
5. Definir DEBUG=False
6. Usar HTTPS em todas as URLs
7. Configurar EMAIL_BACKEND real (SendGrid, etc.)
"""
    print(guide)

def main():
    """Executa todas as verificações"""
    print(f"\n{BLUE}{'='*60}")
    print("CHECKLIST DE INTEGRAÇÃO - SISTEMA DE PAGAMENTOS")
    print(f"{'='*60}{RESET}\n")
    
    results = {
        'Variáveis de Ambiente': check_env_variables(),
        'Django Settings': check_django_settings(),
        'URLs Configuradas': check_urls_configured(),
        'Estrutura App': check_app_structure(),
        'Banco de Dados': check_database(),
    }
    
    print(f"\n{BLUE}=== RESUMO ==={RESET}\n")
    for check, result in results.items():
        print_status(result, check)
    
    all_ok = all(results.values())
    
    if all_ok:
        print(f"\n{GREEN}✓ Tudo configurado corretamente!{RESET}")
    else:
        print(f"\n{RED}✗ Alguns itens precisam ser verificados{RESET}")
    
    print_configuration_guide()
    
    print(f"\n{BLUE}=== PRÓXIMOS PASSOS ==={RESET}\n")
    print(f"""
1. Atualizar .env com credenciais reais do Prontu:
   PRONTU_API_KEY=sua_chave_real
   
2. Aplicar migrações (se ainda não feito):
   python manage.py migrate pagamentos
   
3. Testar webhook (substitua a URL):
   curl -X POST http://localhost:8000/api/v1/pagamentos/webhook/prontu/ \\
     -H "Content-Type: application/json" \\
     -d '{{"result": {{"reference_id": "PAG-TEST-123", "status": "accepted"}}}}'
   
4. Testar criação de pagamento via API:
   - Autenticar com JWT token
   - POST /api/v1/pagamentos/criar/
   - Fornecer: tipo_pagamento, valor, moeda, curso_id (opcional)
   
5. Verificar logs:
   tail -f logs/pagamentos.log (se configurado)
   
6. Acessar admin:
   http://localhost:8000/admin/pagamentos/
    """)
    
    return 0 if all_ok else 1

if __name__ == '__main__':
    sys.exit(main())
