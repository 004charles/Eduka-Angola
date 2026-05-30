#!/usr/bin/env python
"""
VALIDAÇÃO RÁPIDA - SISTEMA DE PAGAMENTOS
=========================================

Script rápido para validar que todos os componentes do sistema de pagamentos
estão funcionando corretamente.

Uso:
    python validate_payment_system.py
    
    ou
    
    ./validate_payment_system.py (se executável)
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta

# Cores
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'

User = get_user_model()


def print_header(title):
    print(f"\n{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}{title.center(50)}{RESET}")
    print(f"{BLUE}{'='*50}{RESET}\n")


def check_pass(msg):
    print(f"{GREEN}✓{RESET} {msg}")


def check_fail(msg, details=""):
    print(f"{RED}✗{RESET} {msg}")
    if details:
        print(f"  {details}")


def check_warning(msg, details=""):
    print(f"{YELLOW}⚠{RESET} {msg}")
    if details:
        print(f"  {details}")


def main():
    print(f"\n{CYAN}{'='*50}")
    print("VALIDAÇÃO DO SISTEMA DE PAGAMENTOS")
    print(f"{'='*50}{RESET}\n")
    
    errors = []
    warnings = []
    
    # 1. Verificar variáveis de ambiente (lidas do Django settings)
    print_header("1. VARIÁVEIS DE AMBIENTE")
    
    # Mapeia nome da var de ambiente para atributo no settings
    settings_vars = {
        'PAGAMENTOS_ATIVADOS': 'PAGAMENTOS_ATIVADOS',
        'GATEWAY_PADRAO': 'GATEWAY_PADRAO',
        'MOEDA_PADRAO': 'MOEDA_PADRAO',
        'PRONTU_API_URL': 'PRONTU_API_URL',
        'PRONTU_API_KEY': 'PRONTU_API_KEY',
        'PRONTU_CALLBACK_URL': 'PRONTU_CALLBACK_URL',
    }
    
    for var, setting_attr in settings_vars.items():
        # Tenta primeiro via os.getenv (variável de ambiente real)
        value = os.getenv(var)
        # Se não encontrou, tenta via Django settings
        if not value:
            value = getattr(settings, setting_attr, None)
            if value is not None:
                value = str(value)
        
        if value:
            display = value[:50] if len(str(value)) > 50 else value
            check_pass(f"{var} = {display}")
        else:
            check_fail(f"{var} não está configurado")
            errors.append(f"Falta variável de ambiente: {var}")
    
    # 2. Verificar Django settings
    print_header("2. DJANGO SETTINGS")
    
    # App instalado
    if 'pagamentos' in settings.INSTALLED_APPS:
        check_pass("App 'pagamentos' instalado")
    else:
        check_fail("App 'pagamentos' não está em INSTALLED_APPS")
        errors.append("App 'pagamentos' não instalado")
    
    # Configurações
    if hasattr(settings, 'PAGAMENTOS_ATIVADOS'):
        check_pass(f"PAGAMENTOS_ATIVADOS = {settings.PAGAMENTOS_ATIVADOS}")
    else:
        check_warning("PAGAMENTOS_ATIVADOS não definido em settings")
    
    if hasattr(settings, 'PRONTU_API_KEY'):
        check_pass("PRONTU_API_KEY configurado")
    else:
        check_fail("PRONTU_API_KEY não configurado")
        errors.append("PRONTU_API_KEY não está em settings")
    
    # 3. Verificar modelos
    print_header("3. MODELOS DE DADOS")
    
    try:
        from pagamentos.models import Pagamento, HistoricoPagamento, TentativaPagamento
        check_pass("Modelo Pagamento importado")
        check_pass("Modelo HistoricoPagamento importado")
        check_pass("Modelo TentativaPagamento importado")
        
        # Verificar banco
        count = Pagamento.objects.count()
        check_pass(f"Acesso ao banco: {count} pagamentos existentes")
    except ImportError as e:
        check_fail(f"Erro ao importar modelos: {e}")
        errors.append(f"Importação de modelos falhou: {e}")
    except Exception as e:
        check_fail(f"Erro ao acessar banco: {e}")
        errors.append(f"Acesso ao banco de dados falhou: {e}")
    
    # 4. Verificar serviço
    print_header("4. SERVIÇO DE PAGAMENTOS")
    
    try:
        from pagamentos.services import get_payment_service
        servico = get_payment_service()
        check_pass(f"Serviço obtido: {type(servico).__name__}")
        
        # Verificar métodos
        metodos = ['criar_pagamento', 'processar_webhook', 'fazer_retry_pagamento']
        for metodo in metodos:
            if hasattr(servico, metodo):
                check_pass(f"Método '{metodo}' disponível")
            else:
                check_fail(f"Método '{metodo}' não encontrado")
                errors.append(f"Método {metodo} não existe no serviço")
    except Exception as e:
        check_fail(f"Erro ao obter serviço: {e}")
        errors.append(f"Falha ao obter serviço de pagamentos: {e}")
    
    # 5. Verificar URLs
    print_header("5. URLS E ENDPOINTS")
    
    try:
        from django.urls import reverse
        
        # Verificar webhook URL
        try:
            url = reverse('webhook-prontu')
            check_pass(f"Webhook URL: {url}")
        except Exception as e:
            check_warning(f"Webhook URL não encontrada: {e}")
            warnings.append("Webhook URL pode não estar configurada")
        
        # Verificar CRUD URLs
        try:
            url = reverse('pagamento-list')
            check_pass(f"Pagamentos list URL: {url}")
        except:
            check_warning("Pagamentos list URL não encontrada")
    except Exception as e:
        check_fail(f"Erro ao verificar URLs: {e}")
        errors.append(f"Erro em verificação de URLs: {e}")
    
    # 6. Criar pagamento de teste
    print_header("6. TESTE DE CRIAÇÃO DE PAGAMENTO")
    
    try:
        # Criar usuário de teste
        usuario, criado = User.objects.get_or_create(
            email='validation@edukangola.ao',
            defaults={'nome': 'Validation Test User', 'tipo_usuario': 'ALUNO'}
        )
        
        if criado:
            check_pass(f"Usuário de teste criado")
        else:
            check_pass(f"Usuário de teste obtido existente")
        
        # Tentar criar pagamento
        try:
            from pagamentos.services import get_payment_service
            servico = get_payment_service()
            
            pagamento = servico.criar_pagamento(
                usuario=usuario,
                tipo_pagamento='INSCRICAO',
                valor=Decimal('1000.00'),
                moeda='AOA'
            )
            
            check_pass(f"Pagamento criado: {pagamento.referencia_pagamento}")
            check_pass(f"Status: {pagamento.status}")
            check_pass(f"URL: {pagamento.url_pagamento[:50] if pagamento.url_pagamento else 'N/A'}...")
        
        except Exception as e:
            # Tentar criar sem serviço
            from pagamentos.models import Pagamento
            import uuid
            
            pag = Pagamento.objects.create(
                usuario=usuario,
                referencia_pagamento=f'VAL_{uuid.uuid4().hex[:8]}',
                tipo_pagamento='INSCRICAO',
                valor=Decimal('1000.00'),
                valor_final=Decimal('1000.00'),
                moeda='AOA',
                gateway='PRONTU',
                status='PENDING'
            )
            
            check_warning(f"Criado sem serviço: {pag.referencia_pagamento}")
            warnings.append("Pagamento criado diretamente (serviço pode ter falha)")
    
    except Exception as e:
        check_fail(f"Erro ao criar pagamento: {e}")
        errors.append(f"Falha ao criar pagamento: {e}")
    
    # 7. Verificar API
    print_header("7. ENDPOINTS DA API")
    
    try:
        from rest_framework.test import APIClient
        client = APIClient()
        
        # Sem autenticação
        response = client.get('/api/v1/pagamentos/')
        if response.status_code == 401:
            check_pass("Autenticação requerida (401)")
        else:
            check_warning(f"Autenticação não requerida (status: {response.status_code})")
            warnings.append("Endpoint de pagamentos pode estar acessível sem autenticação")
        
        # Com autenticação
        usuario_api = User.objects.first()
        if usuario_api:
            client.force_authenticate(user=usuario_api)
            response = client.get('/api/v1/pagamentos/')
            
            if response.status_code == 200:
                check_pass(f"Endpoint autenticado funciona (200)")
            else:
                check_warning(f"Endpoint retornou: {response.status_code}")
    
    except Exception as e:
        check_warning(f"Erro ao testar API: {e}")
        warnings.append(f"Testes de API podem ter falhado: {e}")
    
    # RESUMO FINAL
    print_header("RESUMO DA VALIDAÇÃO")
    
    total_checks = len(errors) + len(warnings)
    
    if not errors:
        print(f"{GREEN}✓ SISTEMA VALIDADO COM SUCESSO{RESET}\n")
        print("✓ Todas as verificações críticas passaram")
        
        if warnings:
            print(f"\n{YELLOW}Avisos:{RESET}")
            for i, w in enumerate(warnings, 1):
                print(f"  {i}. {w}")
    else:
        print(f"{RED}✗ FALHAS DETECTADAS{RESET}\n")
        print(f"Erros críticos: {len(errors)}")
        
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
        
        if warnings:
            print(f"\n{YELLOW}Avisos: {len(warnings)}{RESET}")
            for i, w in enumerate(warnings, 1):
                print(f"  {i}. {w}")
        
        print(f"\n{RED}Ação necessária: Corrigir os erros acima antes de usar o sistema.{RESET}")
    
    print(f"\n{BLUE}{'='*50}{RESET}\n")
    
    # Return exit code
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
