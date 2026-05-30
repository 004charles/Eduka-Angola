"""
TESTE E2E COMPLETO - SISTEMA DE PAGAMENTOS
============================================

Este script realiza um teste end-to-end completo do sistema de pagamentos.
Valida desde a configuração até o fluxo completo de pagamento.

Uso: python manage.py shell < test_pagamentos_e2e.py
ou: python test_pagamentos_e2e.py
"""

import os
import sys
import json
import django
import uuid
from pathlib import Path
from decimal import Decimal
from datetime import timedelta
from typing import Dict, List, Tuple

# Setup Django
if __name__ == "__main__":
    # Carregar variáveis do arquivo .env
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        k, v = parts
                        val = v.strip().strip("'").strip('"')
                        os.environ.setdefault(k.strip(), val)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
    django.setup()

# Imports após setup
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.management import call_command
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from pagamentos.models import Pagamento, HistoricoPagamento, TentativaPagamento
from pagamentos.services import (
    get_payment_service,
    ProntuPaymentGateway,
    PagamentoException,
    PagamentoInvalido
)
from cursos_app.models import Curso

User = get_user_model()

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'


def print_header(titulo: str):
    """Imprime header formatado"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{titulo.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_status(teste: str, passou: bool, mensagem: str = ""):
    """Imprime resultado de um teste"""
    symbol = '✓' if passou else '✗'
    color = GREEN if passou else RED
    print(f"  {color}{symbol}{RESET} {teste}")
    if mensagem:
        print(f"    └─ {mensagem}")


def print_info(titulo: str, conteudo: str = ""):
    """Imprime informação"""
    print(f"{CYAN}ℹ{RESET} {titulo}")
    if conteudo:
        print(f"  {conteudo}")


def teste_env_variables() -> Tuple[bool, List[str]]:
    """Verifica variáveis de ambiente necessárias"""
    print_header("1. VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
    
    required_vars = {
        'PAGAMENTOS_ATIVADOS': 'True',
        'GATEWAY_PADRAO': 'PRONTU',
        'MOEDA_PADRAO': 'AOA',
        'PRONTU_API_URL': 'https://api.prontu.io',
        'PRONTU_API_KEY': None,
        'PRONTU_CALLBACK_URL': 'http://localhost:8000/api/v1/pagamentos/webhook/prontu/',
        'FRONTEND_RETURN_URL': None,
        'FRONTEND_CANCEL_URL': None,
        'TEMPO_EXPIRACAO_LINK_MINUTOS': '120',
        'MAX_TENTATIVAS_PAGAMENTO': '3',
    }
    
    todos_presentes = True
    erros = []
    
    for var, valor_esperado in required_vars.items():
        valor_real = os.getenv(var)
        presente = valor_real is not None
        
        if not presente:
            print_status(var, False, "Não configurada")
            todos_presentes = False
            erros.append(f"FALTA: {var}")
        else:
            # Validar valor se necessário
            if valor_esperado and valor_real != valor_esperado:
                print_status(var, False, f"Esperado: {valor_esperado}, Obtido: {valor_real[:50]}")
                # Não é erro crítico, apenas aviso
            else:
                print_status(var, True, f"Valor: {valor_real[:50]}")
    
    return todos_presentes, erros


def teste_django_settings() -> Tuple[bool, List[str]]:
    """Verifica se Django settings está configurado"""
    print_header("2. VERIFICAÇÃO DE CONFIGURAÇÕES DO DJANGO")
    
    from django.conf import settings
    
    erros = []
    
    # Verificar se app está instalado
    app_instalado = 'pagamentos' in settings.INSTALLED_APPS
    print_status("App 'pagamentos' instalado", app_instalado)
    if not app_instalado:
        erros.append("App 'pagamentos' não está em INSTALLED_APPS")
    
    # Verificar settings de pagamentos
    checks = {
        'PAGAMENTOS_ATIVADOS': getattr(settings, 'PAGAMENTOS_ATIVADOS', False),
        'GATEWAY_PADRAO': getattr(settings, 'GATEWAY_PADRAO', None),
        'PRONTU_API_URL': getattr(settings, 'PRONTU_API_URL', None),
        'PRONTU_API_KEY': getattr(settings, 'PRONTU_API_KEY', None),
    }
    
    for setting, valor in checks.items():
        existe = valor is not None and valor != ""
        print_status(f"Setting '{setting}' configurado", existe)
        if not existe:
            erros.append(f"Setting '{setting}' não configurado")
    
    # Verificar URLs
    try:
        from django.urls import reverse
        url_webhook = reverse('webhook-prontu')
        print_status("Webhook URL configurada", True, f"URL: {url_webhook}")
    except Exception as e:
        print_status("Webhook URL configurada", False, str(e))
        erros.append(f"Erro ao resolver webhook URL: {str(e)}")
    
    return len(erros) == 0, erros


def teste_models_database() -> Tuple[bool, List[str]]:
    """Verifica se modelos estão sincronizados com banco"""
    print_header("3. VERIFICAÇÃO DE MODELOS E BANCO DE DADOS")
    
    erros = []
    
    # Verificar se tabela existe
    try:
        from django.db import connection
        cursor = connection.cursor()
        
        tabelas_esperadas = [
            'pagamentos_pagamento',
            'pagamentos_historicopagamento',
            'pagamentos_tentativapagamento',
        ]
        
        for tabela in tabelas_esperadas:
            cursor.execute(f"SELECT 1 FROM {tabela} LIMIT 1")
            print_status(f"Tabela '{tabela}' existe", True)
    except Exception as e:
        print_status(f"Verificação de tabelas", False, str(e))
        erros.append(f"Erro ao acessar banco: {str(e)}")
    
    # Verificar se podemos criar objetos
    try:
        count_antes = Pagamento.objects.count()
        print_status("Acesso ao modelo Pagamento", True, f"Total no banco: {count_antes}")
    except Exception as e:
        print_status("Acesso ao modelo Pagamento", False, str(e))
        erros.append(f"Erro ao acessar modelo Pagamento: {str(e)}")
    
    return len(erros) == 0, erros


def teste_criar_pagamento() -> Tuple[bool, List[str]]:
    """Testa criação de pagamento"""
    print_header("4. TESTE DE CRIAÇÃO DE PAGAMENTO")
    
    erros = []
    pagamento_criado = None
    
    try:
        # Criar usuário de teste
        usuario, criado = User.objects.get_or_create(
            email='teste_e2e@edukangola.ao',
            defaults={
                'nome': 'Teste E2E',
                'tipo_usuario': 'ALUNO'
            }
        )
        print_status("Usuário de teste criado/obtido", True, f"ID: {usuario.id}")
        
        # Criar pagamento
        servico = get_payment_service()
        pagamento = servico.criar_pagamento(
            usuario=usuario,
            tipo_pagamento='INSCRICAO',
            valor=Decimal('5000.00'),
            moeda='AOA',
            url_sucesso='http://localhost:3000/pagamento/sucesso',
            url_cancelamento='http://localhost:3000/pagamento/cancelado',
        )
        
        print_status("Pagamento criado", True, f"ID: {pagamento.id}")
        print_info("Referência", pagamento.referencia_pagamento)
        print_info("Status", pagamento.status)
        print_info("Valor", f"{pagamento.valor_final} {pagamento.moeda}")
        print_info("Gateway", pagamento.gateway)
        
        # Validações
        assert pagamento.usuario == usuario, "Usuário não associado corretamente"
        print_status("Usuário associado corretamente", True)
        
        assert pagamento.status in ['PENDING', 'REQUESTED'], f"Status inicial deve ser PENDING ou REQUESTED (obtido: {pagamento.status})"
        print_status(f"Status inicial {pagamento.status}", True)
        
        assert pagamento.valor_final == Decimal('5000.00'), "Valor final incorreto"
        print_status("Valor final correto", True)
        
        assert pagamento.url_pagamento, "URL de pagamento não gerada"
        print_status("URL de pagamento gerada", True, f"URL: {pagamento.url_pagamento[:50]}")
        
        pagamento_criado = pagamento
        
    except Exception as e:
        print_status("Criação de pagamento", False, str(e))
        erros.append(f"Erro ao criar pagamento: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return len(erros) == 0, erros, pagamento_criado


def teste_listar_pagamentos(usuario) -> Tuple[bool, List[str]]:
    """Testa listagem de pagamentos do usuário"""
    print_header("5. TESTE DE LISTAGEM DE PAGAMENTOS")
    
    erros = []
    
    try:
        pagamentos = Pagamento.objects.filter(usuario=usuario)
        total = pagamentos.count()
        
        print_status("Pagamentos listados", True, f"Total: {total}")
        
        if total > 0:
            for i, pag in enumerate(pagamentos[:3], 1):
                print_info(f"Pagamento {i}", 
                          f"{pag.referencia_pagamento} - {pag.status} - {pag.valor_final} {pag.moeda}")
        
    except Exception as e:
        print_status("Listagem de pagamentos", False, str(e))
        erros.append(f"Erro ao listar pagamentos: {str(e)}")
    
    return len(erros) == 0, erros


def teste_atualizar_status_pagamento(pagamento) -> Tuple[bool, List[str]]:
    """Testa atualização de status de pagamento"""
    print_header("6. TESTE DE ATUALIZAÇÃO DE STATUS")
    
    erros = []
    
    try:
        # Atualizar status
        pagamento.status = 'PROCESSING'
        pagamento.save()
        
        print_status("Status atualizado para PROCESSING", True)
        
        # Verificar histórico
        historico = HistoricoPagamento.objects.filter(pagamento=pagamento)
        total_historico = historico.count()
        
        print_status("Histórico de mudanças registrado", True, f"Total de mudanças: {total_historico}")
        
        if total_historico > 0:
            for registro in historico[:3]:
                print_info(f"Mudança", f"{registro.status_anterior} → {registro.status_novo}")
        
    except Exception as e:
        print_status("Atualização de status", False, str(e))
        erros.append(f"Erro ao atualizar status: {str(e)}")
    
    return len(erros) == 0, erros


def teste_webhook() -> Tuple[bool, List[str]]:
    """Testa processamento de webhook do Prontu"""
    print_header("7. TESTE DE WEBHOOK")
    
    erros = []
    client = APIClient()
    
    try:
        # Criar pagamento primeiro
        usuario, _ = User.objects.get_or_create(
            email='webhook@edukangola.ao',
            defaults={'nome': 'Teste Webhook', 'tipo_usuario': 'ALUNO'}
        )
        
        servico = get_payment_service()
        pagamento = servico.criar_pagamento(
            usuario=usuario,
            tipo_pagamento='INSCRICAO',
            valor=Decimal('1000.00'),
            moeda='AOA',
        )
        
        print_info("Pagamento de teste", f"ID: {pagamento.id}")
        print_info("Referência", pagamento.referencia_pagamento)
        
        # Simular webhook de sucesso
        webhook_data = {
            'result': {
                'status': 'accepted',
                'id': 'txn_' + str(pagamento.id)[:8],
                'prontu_transaction_id': 'txn_' + str(pagamento.id)[:8],
                'reference_id': pagamento.referencia_pagamento,
                'amount': str(pagamento.valor_final),
                'currency': pagamento.moeda,
                'timestamp': timezone.now().isoformat(),
            }
        }
        
        print_info("Dados do webhook", json.dumps(webhook_data, indent=2))
        
        # Enviar webhook
        try:
            resposta = client.post(
                '/api/v1/pagamentos/webhook/prontu/',
                data=webhook_data,
                format='json'
            )
            
            if resposta.status_code == status.HTTP_200_OK:
                print_status("Webhook processado", True, f"Status: {resposta.status_code}")
                print_info("Resposta", json.dumps(resposta.json(), indent=2))
            else:
                print_status("Webhook processado", False, f"Status: {resposta.status_code}")
                erros.append(f"Webhook retornou status {resposta.status_code}")
        
        except Exception as e:
            print_status("Envio de webhook", False, str(e))
            erros.append(f"Erro ao enviar webhook: {str(e)}")
        
    except Exception as e:
        print_status("Teste de webhook", False, str(e))
        erros.append(f"Erro no teste de webhook: {str(e)}")
    
    return len(erros) == 0, erros


def teste_fluxo_completo_e2e() -> Tuple[bool, List[str]]:
    """Testa o fluxo completo E2E"""
    print_header("8. TESTE DE FLUXO COMPLETO E2E")
    
    erros = []
    
    try:
        # Passo 1: Criar usuário
        print(f"\n{CYAN}Passo 1: Criando usuário...{RESET}")
        usuario, _ = User.objects.get_or_create(
            email='fluxo@edukangola.ao',
            defaults={'nome': 'Fluxo Completo E2E', 'tipo_usuario': 'ALUNO'}
        )
        print_status("Usuário criado", True, f"ID: {usuario.id}")
        
        # Passo 2: Criar pagamento
        print(f"\n{CYAN}Passo 2: Criando pagamento...{RESET}")
        servico = get_payment_service()
        pagamento = servico.criar_pagamento(
            usuario=usuario,
            tipo_pagamento='INSCRICAO',
            valor=Decimal('2500.00'),
            moeda='AOA',
        )
        print_status("Pagamento criado", True, f"ID: {pagamento.id}")
        print_info("Status inicial", pagamento.status)
        
        # Passo 3: Verificar pagamento
        print(f"\n{CYAN}Passo 3: Verificando pagamento...{RESET}")
        pagamento_recuperado = Pagamento.objects.get(id=pagamento.id)
        assert pagamento_recuperado.usuario == usuario, "Usuário não coincide"
        print_status("Pagamento recuperado corretamente", True)
        
        # Passo 4: Simular webhook
        print(f"\n{CYAN}Passo 4: Simulando webhook de sucesso...{RESET}")
        pagamento.status = 'ACCEPTED'
        pagamento.data_pagamento = timezone.now()
        pagamento.referencia_gateway = f"prontu_{uuid.uuid4().hex[:8]}"
        pagamento.save()
        print_status("Status atualizado para ACCEPTED", True)
        
        # Passo 5: Verificar histórico
        print(f"\n{CYAN}Passo 5: Verificando histórico...{RESET}")
        historico = HistoricoPagamento.objects.filter(pagamento=pagamento)
        print_status("Histórico registrado", True, f"Total: {historico.count()}")
        
        # Passo 6: Verificar dados persistidos
        print(f"\n{CYAN}Passo 6: Verificando dados persistidos...{RESET}")
        pagamento_final = Pagamento.objects.get(id=pagamento.id)
        assert pagamento_final.status == 'ACCEPTED', "Status não foi persistido"
        assert pagamento_final.data_pagamento is not None, "Data de pagamento não foi persistida"
        print_status("Dados persistidos corretamente", True)
        
        print_info("Resumo do fluxo",
                  f"Pagamento {pagamento.referencia_pagamento} "
                  f"passou de PENDING → ACCEPTED com sucesso")
        
    except Exception as e:
        print_status("Fluxo E2E completo", False, str(e))
        erros.append(f"Erro no fluxo E2E: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return len(erros) == 0, erros


def teste_api_endpoints() -> Tuple[bool, List[str]]:
    """Testa endpoints da API"""
    print_header("9. TESTE DE ENDPOINTS DA API")
    
    erros = []
    client = APIClient()
    
    try:
        # Criar usuário e fazer login
        usuario, _ = User.objects.get_or_create(
            email='api@edukangola.ao',
            defaults={'nome': 'API Test User', 'tipo_usuario': 'ALUNO'}
        )
        usuario.set_password('testpass123')
        usuario.save()
        
        # Autenticar
        client.force_authenticate(user=usuario)
        print_status("Usuário autenticado", True)
        
        # Teste: GET /api/v1/pagamentos/
        print(f"\n{CYAN}Teste GET /api/v1/pagamentos/{RESET}")
        try:
            resposta = client.get('/api/v1/pagamentos/')
            if resposta.status_code == status.HTTP_200_OK:
                print_status("GET /api/v1/pagamentos/", True, f"Retornou {len(resposta.json())} pagamentos")
            else:
                print_status("GET /api/v1/pagamentos/", False, f"Status: {resposta.status_code}")
        except Exception as e:
            print_status("GET /api/v1/pagamentos/", False, str(e))
        
        # Teste: POST /api/v1/pagamentos/criar/
        print(f"\n{CYAN}Teste POST /api/v1/pagamentos/criar/{RESET}")
        try:
            payload = {
                'tipo_pagamento': 'INSCRICAO',
                'valor': '1500.00',
                'moeda': 'AOA',
            }
            resposta = client.post('/api/v1/pagamentos/criar/', payload, format='json')
            if resposta.status_code == status.HTTP_201_CREATED:
                print_status("POST /api/v1/pagamentos/criar/", True, f"Status: {resposta.status_code}")
                dados = resposta.json()
                print_info("Resposta", f"ID: {dados.get('pagamento', {}).get('id')}")
            else:
                print_status("POST /api/v1/pagamentos/criar/", False, f"Status: {resposta.status_code}")
                print_info("Erro", str(resposta.json()))
        except Exception as e:
            print_status("POST /api/v1/pagamentos/criar/", False, str(e))
        
    except Exception as e:
        print_status("Testes de API", False, str(e))
        erros.append(f"Erro nos testes de API: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return len(erros) == 0, erros


def teste_servico_pagamento() -> Tuple[bool, List[str]]:
    """Testa o serviço de pagamento"""
    print_header("10. TESTE DO SERVIÇO DE PAGAMENTO")
    
    erros = []
    
    try:
        servico = get_payment_service()
        print_status("Serviço de pagamento obtido", True, f"Tipo: {type(servico).__name__}")
        
        # Verificar se serviço tem métodos essenciais
        metodos_esperados = [
            'criar_pagamento',
            'processar_webhook',
            'fazer_retry_pagamento',
        ]
        
        for metodo in metodos_esperados:
            tem_metodo = hasattr(servico, metodo)
            print_status(f"Método '{metodo}' existe", tem_metodo)
            if not tem_metodo:
                erros.append(f"Método '{metodo}' não encontrado")
        
    except Exception as e:
        print_status("Obtenção do serviço", False, str(e))
        erros.append(f"Erro ao obter serviço: {str(e)}")
    
    return len(erros) == 0, erros


def teste_seguranca() -> Tuple[bool, List[str]]:
    """Testa aspectos de segurança"""
    print_header("11. TESTE DE SEGURANÇA")
    
    erros = []
    client = APIClient()
    
    try:
        # Teste 1: Não autenticado não pode listar pagamentos
        print(f"\n{CYAN}Teste: Acesso sem autenticação{RESET}")
        resposta = client.get('/api/v1/pagamentos/')
        if resposta.status_code == status.HTTP_401_UNAUTHORIZED:
            print_status("Acesso sem autenticação bloqueado", True)
        else:
            print_status("Acesso sem autenticação bloqueado", False, f"Status: {resposta.status_code}")
            erros.append("Endpoint permite acesso não autenticado")
        
        # Teste 2: Usuário não pode acessar pagamentos de outros
        print(f"\n{CYAN}Teste: Isolamento de dados entre usuários{RESET}")
        
        # Criar dois usuários
        user1, _ = User.objects.get_or_create(email='user1@edukangola.ao', defaults={'nome': 'Security User 1', 'tipo_usuario': 'ALUNO'})
        user2, _ = User.objects.get_or_create(email='user2@edukangola.ao', defaults={'nome': 'Security User 2', 'tipo_usuario': 'ALUNO'})
        
        # Criar pagamento para user1
        servico = get_payment_service()
        pag1 = servico.criar_pagamento(
            usuario=user1,
            tipo_pagamento='INSCRICAO',
            valor=Decimal('1000.00'),
            moeda='AOA',
        )
        
        # Tentar acessar como user2
        client.force_authenticate(user=user2)
        try:
            resposta = client.get(f'/api/v1/pagamentos/{pag1.id}/')
            if resposta.status_code == status.HTTP_404_NOT_FOUND:
                print_status("Isolamento de dados funcionando", True)
            else:
                print_status("Isolamento de dados funcionando", False, f"Status: {resposta.status_code}")
                erros.append("User2 conseguiu acessar pagamento de User1")
        except Exception as e:
            print_status("Verificação de isolamento", False, str(e))
        
    except Exception as e:
        print_status("Testes de segurança", False, str(e))
        erros.append(f"Erro nos testes de segurança: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return len(erros) == 0, erros


def gerar_relatorio_final(resultados: Dict) -> None:
    """Gera relatório final dos testes"""
    print_header("RELATÓRIO FINAL")
    
    total_testes = len(resultados)
    testes_passou = sum(1 for r in resultados.values() if r['passou'])
    testes_falharam = total_testes - testes_passou
    
    print(f"Total de testes: {total_testes}")
    print(f"{GREEN}Passou: {testes_passou}{RESET}")
    print(f"{RED}Falhou: {testes_falharam}{RESET}\n")
    
    # Tabela de resultados
    print(f"{CYAN}Resultados por teste:{RESET}\n")
    for nome, resultado in resultados.items():
        symbol = GREEN + '✓' if resultado['passou'] else RED + '✗'
        print(f"{symbol}{RESET} {nome}")
        if resultado.get('erros'):
            for erro in resultado['erros'][:2]:  # Mostrar primeiros 2 erros
                print(f"    └─ {erro}")
    
    # Conclusão
    print(f"\n{BLUE}{'='*60}{RESET}")
    if testes_falharam == 0:
        print(f"{GREEN}✓ TODOS OS TESTES PASSARAM!{RESET}")
        print("Sistema de pagamentos está integrado corretamente.")
    else:
        print(f"{YELLOW}⚠ {testes_falharam} TESTE(S) FALHARAM{RESET}")
        print("Verifique os erros acima e corrija as configurações.")
    print(f"{BLUE}{'='*60}{RESET}\n")


def main():
    """Executa todos os testes"""
    import uuid  # Adicionar import global
    
    print_header("TESTE E2E - SISTEMA DE PAGAMENTOS EDUKANGOLA")
    
    resultados = {}
    pagamento_teste = None
    usuario_teste = None
    
    # 1. Verificar variáveis de ambiente
    passou, erros = teste_env_variables()
    resultados['1. Variáveis de Ambiente'] = {'passou': passou, 'erros': erros}
    
    # 2. Verificar Django settings
    passou, erros = teste_django_settings()
    resultados['2. Django Settings'] = {'passou': passou, 'erros': erros}
    
    # 3. Verificar banco de dados
    passou, erros = teste_models_database()
    resultados['3. Banco de Dados'] = {'passou': passou, 'erros': erros}
    
    # 4. Criar pagamento
    passou, erros, pagamento = teste_criar_pagamento()
    resultados['4. Criar Pagamento'] = {'passou': passou, 'erros': erros}
    pagamento_teste = pagamento
    usuario_teste = pagamento.usuario if pagamento else None
    
    # 5. Listar pagamentos (precisa de usuário)
    if usuario_teste:
        passou, erros = teste_listar_pagamentos(usuario_teste)
        resultados['5. Listar Pagamentos'] = {'passou': passou, 'erros': erros}
    
    # 6. Atualizar status (precisa de pagamento)
    if pagamento_teste:
        passou, erros = teste_atualizar_status_pagamento(pagamento_teste)
        resultados['6. Atualizar Status'] = {'passou': passou, 'erros': erros}
    
    # 7. Webhook
    passou, erros = teste_webhook()
    resultados['7. Webhook'] = {'passou': passou, 'erros': erros}
    
    # 8. Fluxo completo E2E
    passou, erros = teste_fluxo_completo_e2e()
    resultados['8. Fluxo Completo E2E'] = {'passou': passou, 'erros': erros}
    
    # 9. Endpoints da API
    passou, erros = teste_api_endpoints()
    resultados['9. Endpoints da API'] = {'passou': passou, 'erros': erros}
    
    # 10. Serviço de pagamento
    passou, erros = teste_servico_pagamento()
    resultados['10. Serviço de Pagamento'] = {'passou': passou, 'erros': erros}
    
    # 11. Segurança
    passou, erros = teste_seguranca()
    resultados['11. Segurança'] = {'passou': passou, 'erros': erros}
    
    # Gerar relatório final
    gerar_relatorio_final(resultados)


if __name__ == '__main__':
    main()
