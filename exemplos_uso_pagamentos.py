"""
EXEMPLOS PRÁTICOS - USO DO SISTEMA DE PAGAMENTOS
=================================================

Exemplos práticos de como usar o sistema de pagamentos após testes validarem
a integração.

Todos os exemplos assumem que os testes E2E passaram com sucesso.
"""

# ============================================================
# EXEMPLO 1: CRIAR PAGAMENTO VIA API
# ============================================================

def exemplo_criar_pagamento_api():
    """Exemplo: Criar pagamento via API REST"""
    
    import requests
    import json
    
    # URL do endpoint
    url = "http://localhost:8000/api/v1/pagamentos/criar/"
    
    # Headers com token de autenticação
    headers = {
        "Authorization": "Bearer seu_token_jwt_aqui",
        "Content-Type": "application/json"
    }
    
    # Dados do pagamento
    payload = {
        "tipo_pagamento": "INSCRICAO",
        "valor": "5000.00",
        "moeda": "AOA",
        "curso_id": 1,
        "url_sucesso": "https://edukangola.com/pagamento/sucesso",
        "url_cancelamento": "https://edukangola.com/pagamento/cancelado"
    }
    
    # Fazer request
    response = requests.post(url, headers=headers, json=payload)
    
    # Processar resposta
    if response.status_code == 201:
        dados = response.json()
        print(f"✓ Pagamento criado com sucesso!")
        print(f"  ID: {dados['pagamento']['id']}")
        print(f"  Referência: {dados['pagamento']['referencia_pagamento']}")
        print(f"  URL: {dados['pagamento']['url_pagamento']}")
        
        # Redirecionar usuário para URL de pagamento
        return dados['pagamento']['url_pagamento']
    else:
        print(f"✗ Erro ao criar pagamento: {response.status_code}")
        print(response.json())
        return None


# ============================================================
# EXEMPLO 2: CRIAR PAGAMENTO VIA SERVIÇO (Backend)
# ============================================================

def exemplo_criar_pagamento_backend():
    """Exemplo: Criar pagamento usando o serviço backend"""
    
    from django.contrib.auth import get_user_model
    from pagamentos.services import get_payment_service
    from decimal import Decimal
    
    User = get_user_model()
    
    # Obter usuário
    usuario = User.objects.get(username='joao_silva')
    
    # Obter serviço de pagamentos
    servico = get_payment_service()
    
    # Criar pagamento
    pagamento = servico.criar_pagamento(
        usuario=usuario,
        tipo_pagamento='INSCRICAO',
        valor=Decimal('5000.00'),
        moeda='AOA',
        curso_id=1,
        numero_parcela=None,
        url_sucesso='https://edukangola.com/sucesso',
        url_cancelamento='https://edukangola.com/cancelado'
    )
    
    # Retornar URL para redirecionar usuário
    return pagamento.url_pagamento


# ============================================================
# EXEMPLO 3: LISTAR PAGAMENTOS DO USUÁRIO
# ============================================================

def exemplo_listar_pagamentos():
    """Exemplo: Listar todos os pagamentos de um usuário"""
    
    from pagamentos.models import Pagamento
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    usuario = User.objects.get(username='joao_silva')
    
    # Listar todos os pagamentos
    pagamentos = Pagamento.objects.filter(usuario=usuario).order_by('-data_criacao')
    
    print(f"Pagamentos de {usuario.first_name}:")
    
    for pagamento in pagamentos:
        status_emoji = "✓" if pagamento.eh_pago() else "⏳"
        print(f"\n{status_emoji} Pagamento #{pagamento.referencia_pagamento}")
        print(f"  Data: {pagamento.data_criacao.strftime('%d/%m/%Y %H:%M')}")
        print(f"  Valor: {pagamento.valor_final} {pagamento.moeda}")
        print(f"  Status: {pagamento.status}")
        print(f"  Tipo: {pagamento.tipo_pagamento}")
        
        if pagamento.eh_pago():
            print(f"  Data Pagamento: {pagamento.data_pagamento}")
            print(f"  Gateway ID: {pagamento.referencia_gateway}")
    
    return pagamentos


# ============================================================
# EXEMPLO 4: VERIFICAR STATUS DE PAGAMENTO
# ============================================================

def exemplo_verificar_status():
    """Exemplo: Verificar o status de um pagamento específico"""
    
    from pagamentos.models import Pagamento
    
    # Buscar pagamento por referência
    pagamento = Pagamento.objects.get(referencia_pagamento='REF_abc123xyz')
    
    print(f"Pagamento: {pagamento.referencia_pagamento}")
    print(f"Status: {pagamento.status}")
    print(f"Valor: {pagamento.valor_final} {pagamento.moeda}")
    
    # Verificar se foi pago
    if pagamento.eh_pago():
        print(f"✓ Pago em {pagamento.data_pagamento}")
        
        # Processar confirmação (ativar acesso, etc)
        processar_confirmacao_pagamento(pagamento)
    else:
        print(f"⏳ Aguardando pagamento")
        
        # Verificar se pode fazer retry
        if pagamento.pode_fazer_retry():
            print(f"  Você pode tentar pagar novamente")
        else:
            print(f"  Status não permite retry")
    
    return pagamento


# ============================================================
# EXEMPLO 5: FAZER RETRY DE PAGAMENTO
# ============================================================

def exemplo_retry_pagamento():
    """Exemplo: Fazer retry de um pagamento expirado/rejeitado"""
    
    from pagamentos.models import Pagamento
    from pagamentos.services import get_payment_service, PagamentoException
    
    # Buscar pagamento
    pagamento = Pagamento.objects.get(referencia_pagamento='REF_abc123xyz')
    
    # Verificar se pode fazer retry
    if not pagamento.pode_fazer_retry():
        print(f"✗ Pagamento {pagamento.status} não pode fazer retry")
        return None
    
    # Obter serviço
    servico = get_payment_service()
    
    try:
        # Fazer retry
        pagamento_atualizado = servico.fazer_retry_pagamento(pagamento)
        
        print(f"✓ Novo link de pagamento gerado!")
        print(f"  URL: {pagamento_atualizado.url_pagamento}")
        
        return pagamento_atualizado.url_pagamento
    
    except PagamentoException as e:
        print(f"✗ Erro ao fazer retry: {e}")
        return None


# ============================================================
# EXEMPLO 6: PROCESSAR WEBHOOK DO PRONTU
# ============================================================

def exemplo_processar_webhook():
    """Exemplo: Processar webhook do Prontu (implementação no Django)"""
    
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.views.decorators.http import require_http_methods
    from pagamentos.services import get_payment_service
    import json
    
    @csrf_exempt
    @require_http_methods(["POST"])
    def webhook_prontu(request):
        """Endpoint para receber webhooks do Prontu"""
        
        try:
            # Parsear dados
            dados = json.loads(request.body)
            
            # Obter serviço
            servico = get_payment_service()
            
            # Processar webhook
            resultado = servico.processar_webhook(dados)
            
            # Retornar sucesso
            return JsonResponse({
                'sucesso': True,
                'mensagem': 'Webhook processado com sucesso',
                'resultado': resultado
            })
        
        except Exception as e:
            # Log do erro
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao processar webhook: {e}")
            
            # Retornar erro
            return JsonResponse({
                'sucesso': False,
                'erro': str(e)
            }, status=400)
    
    return webhook_prontu


# ============================================================
# EXEMPLO 7: HISTÓRICO DE PAGAMENTO
# ============================================================

def exemplo_historico_pagamento():
    """Exemplo: Ver histórico completo de um pagamento"""
    
    from pagamentos.models import Pagamento, HistoricoPagamento
    
    # Buscar pagamento
    pagamento = Pagamento.objects.get(referencia_pagamento='REF_abc123xyz')
    
    print(f"Histórico do Pagamento {pagamento.referencia_pagamento}:")
    print("="*50)
    
    # Obter histórico
    historico = HistoricoPagamento.objects.filter(
        pagamento=pagamento
    ).order_by('data_criacao')
    
    for i, evento in enumerate(historico, 1):
        print(f"\n{i}. {evento.data_criacao.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"   {evento.status_anterior} → {evento.status_novo}")
        print(f"   Motivo: {evento.motivo}")
        print(f"   Usuário: {evento.usuario if evento.usuario else 'Sistema'}")
    
    return historico


# ============================================================
# EXEMPLO 8: GERAR RELATÓRIO DE PAGAMENTOS
# ============================================================

def exemplo_relatorio_pagamentos():
    """Exemplo: Gerar relatório de pagamentos por período"""
    
    from pagamentos.models import Pagamento
    from django.utils import timezone
    from datetime import timedelta
    from decimal import Decimal
    
    # Definir período (últimos 30 dias)
    data_inicio = timezone.now() - timedelta(days=30)
    data_fim = timezone.now()
    
    # Filtrar pagamentos
    pagamentos = Pagamento.objects.filter(
        data_criacao__gte=data_inicio,
        data_criacao__lte=data_fim
    )
    
    # Calcular métricas
    total_pagamentos = pagamentos.count()
    pagamentos_confirmados = pagamentos.filter(status='ACCEPTED').count()
    pagamentos_pendentes = pagamentos.filter(status='PENDING').count()
    pagamentos_rejeitados = pagamentos.filter(status='REJECTED').count()
    
    valor_total = sum(p.valor_final for p in pagamentos) or Decimal(0)
    valor_confirmado = sum(p.valor_final for p in pagamentos.filter(status='ACCEPTED')) or Decimal(0)
    
    # Gerar relatório
    relatorio = {
        'periodo': f'{data_inicio.date()} até {data_fim.date()}',
        'total_pagamentos': total_pagamentos,
        'pagamentos_confirmados': pagamentos_confirmados,
        'pagamentos_pendentes': pagamentos_pendentes,
        'pagamentos_rejeitados': pagamentos_rejeitados,
        'taxa_sucesso': (pagamentos_confirmados / total_pagamentos * 100) if total_pagamentos > 0 else 0,
        'valor_total': valor_total,
        'valor_confirmado': valor_confirmado,
    }
    
    # Exibir
    print(f"RELATÓRIO DE PAGAMENTOS")
    print(f"Período: {relatorio['periodo']}")
    print("="*50)
    print(f"Total: {relatorio['total_pagamentos']} pagamentos")
    print(f"Confirmados: {relatorio['pagamentos_confirmados']}")
    print(f"Pendentes: {relatorio['pagamentos_pendentes']}")
    print(f"Rejeitados: {relatorio['pagamentos_rejeitados']}")
    print(f"Taxa de Sucesso: {relatorio['taxa_sucesso']:.1f}%")
    print("="*50)
    print(f"Valor Total: {relatorio['valor_total']} AOA")
    print(f"Valor Confirmado: {relatorio['valor_confirmado']} AOA")
    
    return relatorio


# ============================================================
# EXEMPLO 9: PROCESSAMENTO AUTOMÁTICO DE PAGAMENTOS
# ============================================================

def exemplo_processamento_automatico():
    """Exemplo: Task celery para processar pagamentos pendentes"""
    
    # Nota: Requer Celery configurado
    # from celery import shared_task
    
    # @shared_task
    def processar_pagamentos_pendentes():
        """Task celery para verificar status de pagamentos pendentes"""
        
        from pagamentos.models import Pagamento
        from pagamentos.services import get_payment_service
        from django.utils import timezone
        from datetime import timedelta
        
        # Buscar pagamentos pendentes há mais de 1 hora
        hora_atras = timezone.now() - timedelta(hours=1)
        pagamentos_antigos = Pagamento.objects.filter(
            status='PENDING',
            data_criacao__lt=hora_atras
        )
        
        servico = get_payment_service()
        processados = 0
        
        for pagamento in pagamentos_antigos:
            try:
                # Verificar status no gateway
                status_gateway = servico.verificar_status(pagamento.referencia_gateway)
                
                # Atualizar se mudou
                if status_gateway['status'] != pagamento.status:
                    pagamento.status = status_gateway['status']
                    pagamento.save()
                    processados += 1
            
            except Exception as e:
                print(f"Erro ao verificar pagamento {pagamento.id}: {e}")
        
        return f"{processados} pagamentos atualizados"
    
    return processar_pagamentos_pendentes()


# ============================================================
# EXEMPLO 10: INTEGRAÇÃO COM INSCRIÇÃO EM CURSO
# ============================================================

def exemplo_inscrever_com_pagamento():
    """Exemplo: Inscrever usuário em curso após pagamento confirmado"""
    
    from django.contrib.auth import get_user_model
    from pagamentos.models import Pagamento
    from cursos_app.models import Curso, Inscricao
    from django.utils import timezone
    
    User = get_user_model()
    
    def inscrever_usuario_em_curso(pagamento_id):
        """Inscrever usuário após pagamento confirmado"""
        
        # Buscar pagamento
        pagamento = Pagamento.objects.get(id=pagamento_id)
        
        # Verificar se foi pago
        if not pagamento.eh_pago():
            raise ValueError(f"Pagamento {pagamento.id} ainda não foi confirmado")
        
        # Obter curso
        curso = pagamento.curso
        if not curso:
            raise ValueError(f"Pagamento {pagamento.id} não tem curso associado")
        
        # Criar inscrição
        inscricao, criada = Inscricao.objects.get_or_create(
            usuario=pagamento.usuario,
            curso=curso,
            defaults={
                'data_inscricao': timezone.now(),
                'pagamento': pagamento,
                'status': 'ATIVA'
            }
        )
        
        if criada:
            print(f"✓ Usuário inscrito em {curso.titulo}")
            
            # Enviar email de confirmação
            enviar_email_inscricao_confirmada(pagamento.usuario, curso)
            
            # Ativar acesso ao conteúdo
            ativar_acesso_curso(pagamento.usuario, curso)
        else:
            print(f"⚠ Usuário já estava inscrito em {curso.titulo}")
        
        return inscricao
    
    return inscrever_usuario_em_curso


# ============================================================
# EXEMPLO 11: TRATAMENTO DE ERROS
# ============================================================

def exemplo_tratamento_erros():
    """Exemplo: Como tratar erros do sistema de pagamentos"""
    
    from pagamentos.services import (
        get_payment_service,
        PagamentoException,
        PagamentoInvalido,
        GatewayIndisponivel
    )
    from decimal import Decimal
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    usuario = User.objects.get(username='joao_silva')
    
    try:
        servico = get_payment_service()
        
        pagamento = servico.criar_pagamento(
            usuario=usuario,
            tipo_pagamento='INSCRICAO',
            valor=Decimal('5000.00'),
            moeda='AOA'
        )
        
        print(f"✓ Pagamento criado: {pagamento.referencia_pagamento}")
    
    except PagamentoInvalido as e:
        # Dados inválidos
        print(f"✗ Dados inválidos: {e}")
        # Retornar erro ao usuário
        return {'erro': 'Dados do pagamento inválidos', 'detalhes': str(e)}
    
    except GatewayIndisponivel as e:
        # Gateway fora do ar
        print(f"✗ Gateway indisponível: {e}")
        # Tentar novamente em alguns minutos
        return {'erro': 'Serviço temporariamente indisponível', 'retry': True}
    
    except PagamentoException as e:
        # Erro geral
        print(f"✗ Erro no pagamento: {e}")
        # Log para investigação
        return {'erro': 'Erro ao processar pagamento', 'detalhes': str(e)}
    
    except Exception as e:
        # Erro inesperado
        print(f"✗ Erro inesperado: {e}")
        # Log crítico
        import logging
        logger = logging.getLogger(__name__)
        logger.critical(f"Erro crítico em pagamento: {e}", exc_info=True)
        
        return {'erro': 'Erro inesperado', 'detalhes': str(e)}


# ============================================================
# COMO USAR ESTES EXEMPLOS
# ============================================================

if __name__ == '__main__':
    """
    Para usar estes exemplos em um shell Django:
    
    python manage.py shell
    
    Depois:
    
    from exemplos_pagamentos import *
    
    # Exemplo 1: Criar pagamento
    url = exemplo_criar_pagamento_backend()
    print(url)
    
    # Exemplo 3: Listar pagamentos
    pagamentos = exemplo_listar_pagamentos()
    
    # Exemplo 7: Ver histórico
    historico = exemplo_historico_pagamento()
    
    # Exemplo 8: Gerar relatório
    relatorio = exemplo_relatorio_pagamentos()
    """
    
    print(__doc__)
