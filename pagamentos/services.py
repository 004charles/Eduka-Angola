"""
Serviço de pagamentos - Camada de abstração para múltiplos gateways.
Implementa padrões de design: Strategy, Factory, Observer.
"""
import base64
import logging
import hashlib
import json
import os
import sys
import uuid
from decimal import Decimal
from datetime import timedelta
from typing import Optional, Dict, Any, Tuple
from abc import ABC, abstractmethod

import requests
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.db import models, transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import (
    Pagamento,
    HistoricoPagamento,
    TentativaPagamento,
    ConfiguracaoPagamento
)

logger = logging.getLogger(__name__)


class PagamentoException(Exception):
    """Exceção base para erros de pagamento"""
    pass


class GatewayIndisponivel(PagamentoException):
    """Gateway de pagamento indisponível"""
    pass


class PagamentoInvalido(PagamentoException):
    """Pagamento inválido"""
    pass


class PaymentGateway(ABC):
    """Interface abstrata para gateways de pagamento"""
    
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = 30
        self.session = requests.Session()
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'EdukAngola/1.0'
        }
        if api_key:
            headers['Authorization'] = api_key

        self.session.headers.update(headers)
    
    @abstractmethod
    def criar_transacao(
        self,
        referencia_pagamento: str,
        usuario_nome: str,
        usuario_email: str,
        usuario_telefone: str,
        valor: Decimal,
        moeda: str,
        descricao: str,
        url_callback: str,
        url_retorno: str,
        url_cancelamento: str,
        metadados: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Cria uma transação no gateway"""
        pass
    
    @abstractmethod
    def validar_callback(self, dados_callback: Dict[str, Any]) -> bool:
        """Valida a assinatura do callback"""
        pass
    
    @abstractmethod
    def processar_callback(self, dados_callback: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o callback do gateway"""
        pass
    
    @abstractmethod
    def verificar_status(self, referencia_gateway: str) -> Dict[str, Any]:
        """Verifica o status de uma transação"""
        pass
    
    def fazer_requisicao(
        self,
        metodo: str,
        endpoint: str,
        dados: Dict[str, Any] = None,
        timeout: int = None
    ) -> Dict[str, Any]:
        """Faz requisição segura ao gateway com retry"""
        url = f"{self.api_url}/{endpoint}"
        timeout = timeout or self.timeout
        
        try:
            if metodo == 'POST':
                resposta = self.session.post(url, json=dados, timeout=timeout)
            elif metodo == 'GET':
                resposta = self.session.get(url, params=dados, timeout=timeout)
            else:
                raise ValueError(f"Método HTTP inválido: {metodo}")
            
            resposta.raise_for_status()
            return resposta.json()
        
        except requests.Timeout:
            logger.error(f"Timeout ao conectar ao gateway: {url}")
            raise GatewayIndisponivel("Gateway de pagamento indisponível (timeout)")
        except requests.ConnectionError:
            logger.error(f"Erro de conexão ao gateway: {url}")
            raise GatewayIndisponivel("Gateway de pagamento indisponível")
        except requests.HTTPError as e:
            body = e.response.text
            logger.error(f"Erro HTTP do gateway: {e.response.status_code} - {body}")
            raise PagamentoException(f"Erro do gateway: {e.response.status_code} - {body}")
        except json.JSONDecodeError:
            logger.error(f"Resposta inválida do gateway (não é JSON)")
            raise PagamentoException("Resposta inválida do gateway")


class ProntuPaymentGateway(PaymentGateway):
    """Implementação específica para Prontu"""
    
    STATUS_MAP = {
        'accepted': 'ACCEPTED',
        'success': 'ACCEPTED',
        'rejected': 'REJECTED',
        'pending': 'PENDING',
        'requested': 'REQUESTED',
        'processing': 'PROCESSING',
        'expired': 'EXPIRED',
        'cancelled': 'CANCELLED',
    }

    def __init__(self, api_url: str, api_key: str):
        """Inicializa o gateway Prontu.
        
        Se PRONTU_EMAIL e PRONTU_PASSWORD estiverem configurados, autentica
        automaticamente via /v1/merchants/get_token para obter um token válido.
        O token do portal pode ser passado como fallback via api_key.
        """
        super().__init__(api_url, api_key)
        # O runner de testes nunca deve autenticar num fornecedor externo.
        # Testes que precisam de payload real fazem patch explícito da sessão.
        if not self._is_test_runtime():
            self._autenticar_via_credenciais()

    @staticmethod
    def _is_test_runtime():
        return "test" in sys.argv or bool(os.getenv("PYTEST_CURRENT_TEST"))

    @classmethod
    def _mock_mode_enabled(cls):
        """Retorna mock explícito ou activa-o por defeito no runner de testes."""
        explicit_mock = os.getenv("GATEWAY_MOCK")
        if explicit_mock is not None:
            return explicit_mock.lower() in ["true", "1", "yes"]
        if cls._is_test_runtime():
            return True
        try:
            from decouple import config as decouple_config
            return decouple_config("GATEWAY_MOCK", default="False", cast=str).lower() in ["true", "1", "yes"]
        except Exception:
            return False

    def _autenticar_via_credenciais(self):
        """Tenta autenticar via email+password para obter token real da API."""
        try:
            from decouple import config as dc
            email = dc('PRONTU_EMAIL', default='')
            password = dc('PRONTU_PASSWORD', default='')
            env = dc('PRONTU_ENV', default='0', cast=int)
        except Exception:
            import os
            email = os.getenv('PRONTU_EMAIL', '')
            password = os.getenv('PRONTU_PASSWORD', '')
            env = int(os.getenv('PRONTU_ENV', '0'))

        if not email or not password:
            logger.debug("PRONTU_EMAIL/PASSWORD não configurados — usando PRONTU_API_KEY do portal.")
            return

        try:
            resp = self.session.post(
                f"{self.api_url}/v1/merchants/get_token",
                json={'email': email, 'password': password, 'env': env},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                token = data.get('token')
                if token:
                    # Actualizar o token na sessão
                    self.api_key = token
                    self.session.headers['Authorization'] = token
                    account = data.get('account', {})
                    logger.info(
                        f"Prontu autenticado com sucesso. Conta: {account.get('name', 'N/A')} "
                        f"({account.get('email', 'N/A')})"
                    )
                    return
            logger.warning(
                f"Falha ao autenticar no Prontu via credenciais: {resp.status_code} — {resp.text[:200]}"
            )
        except Exception as e:
            logger.warning(f"Erro ao autenticar no Prontu via credenciais: {e}")

    def _validar_formato_prontu_api_key(self):
        """Valida se o token Prontu está em formato JWT e contém exp no payload ou no campo data."""
        if not self.api_key:
            return

        partes = self.api_key.split('.')
        if len(partes) != 3:
            raise PagamentoException(
                'PRONTU_API_KEY inválida ou mal formatada: token JWT deve conter 3 partes separadas por pontos.'
            )

        payload_b64 = partes[1]
        padding = '=' * ((4 - len(payload_b64) % 4) % 4)
        try:
            payload_bytes = base64.urlsafe_b64decode(payload_b64 + padding)
            payload = json.loads(payload_bytes)
        except Exception as exc:
            raise PagamentoException(
                f'PRONTU_API_KEY inválida ou mal formatada: {exc}'
            )

        # O Prontu pode ter 'exp' no payload raiz OU dentro de um campo 'data'
        exp_value = payload.get('exp') or (payload.get('data') or {}).get('exp')

        if exp_value is None:
            raise PagamentoException(
                "PRONTU_API_KEY inválida ou mal formatada: claim 'exp' não encontrada no JWT."
            )

        # exp pode ser número UNIX ou string de data — ambos são válidos
        logger.debug(f"Prontu JWT exp: {exp_value}")

    def criar_transacao(
        self,
        referencia_pagamento: str,
        usuario_nome: str,
        usuario_email: str,
        usuario_telefone: str,
        valor: Decimal,
        moeda: str,
        descricao: str,
        url_callback: str,
        url_retorno: str,
        url_cancelamento: str,
        metadados: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Cria transação no Prontu"""
        
        nome_partes = usuario_nome.split() if usuario_nome else []
        payload = {
            'currency': moeda,
            'phone': self._limpar_telefone(usuario_telefone),
            'email': usuario_email,
            'reference_id': referencia_pagamento,
            'first_name': nome_partes[0] if nome_partes else '',
            'last_name': ' '.join(nome_partes[1:]) if len(nome_partes) > 1 else '',
            'amount': float(valor),
            'cancel_url': url_cancelamento,
            'return_url': url_retorno,
            'expiration_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'source': 0,
        }
        
        logger.info(f"Criando transação Prontu: {referencia_pagamento}")
        
        import uuid
        api_key_lower = (self.api_key or '').lower()
        mock_mode = self._mock_mode_enabled()
        placeholder_keys = [
            'sua_chave',
            'seu_api_key',
            'substituir',
            'deve-ser-substituido',
            'pk_test_sua_chave_aqui',
            'seu_api_key_aqui_substituir_em_producao'
        ]

        if mock_mode:
            logger.info(f"Usando MOCK para transação Prontu: {referencia_pagamento}")
            mock_id = f"mock_prontu_{uuid.uuid4().hex[:8].upper()}"
            mock_url = f"{settings.SITE_DOMAIN}/api/v1/pagamentos/webhook/prontu/?ref={referencia_pagamento}"

            return {
                'referencia_gateway': mock_id,
                'url_pagamento': mock_url,
                'resposta_completa': {
                    'status': 'success',
                    'data': {
                        'data': {
                            'id': mock_id,
                            'url': mock_url,
                            'callbackUrl': mock_url
                        }
                    }
                },
                'status': 'REQUESTED'
            }

        if not self.api_key or any(key in api_key_lower for key in placeholder_keys):
            raise PagamentoException(
                'PRONTU_API_KEY inválida ou ausente. Defina uma chave real em .env para gerar links de pagamento reais.'
            )

        self._validar_formato_prontu_api_key()

        try:
            try:
                resposta = self.fazer_requisicao('POST', 'v1/hosts/transactions-receive', payload)
            except PagamentoException as e:
                if '404' in str(e):
                    logger.info('Endpoint v1/hosts/transactions-receive não encontrado, tentando transactions-receive')
                    resposta = self.fazer_requisicao('POST', 'transactions-receive', payload)
                else:
                    raise
            
            dados_transacao = resposta.get('data')
            if isinstance(dados_transacao, dict) and 'data' in dados_transacao:
                dados_transacao = dados_transacao['data']
            
            if not isinstance(dados_transacao, dict) or 'url' not in dados_transacao:
                logger.error(f"Resposta inesperada do Prontu: {resposta}")
                raise PagamentoException("Resposta inesperada do Prontu")
            
            return {
                'referencia_gateway': dados_transacao.get('id'),
                'url_pagamento': dados_transacao.get('url'),
                'resposta_completa': resposta,
                'status': 'REQUESTED'
            }
        
        except PagamentoException:
            raise
        except Exception as e:
            logger.error(f"Erro ao criar transação Prontu: {str(e)}")
            raise PagamentoException(f"Erro ao criar transação: {str(e)}")
    
    def validar_callback(self, dados_callback: Dict[str, Any]) -> bool:
        """Valida callback do Prontu"""
        # O Prontu não usa assinatura específica neste exemplo,
        # mas em produção seria recomendado validar a origem
        
        if 'result' not in dados_callback:
            logger.warning("Callback Prontu sem campo 'result'")
            return False
        
        resultado = dados_callback['result']
        campos_obrigatorios = ['reference_id', 'status']
        
        if not all(campo in resultado for campo in campos_obrigatorios):
            logger.warning(f"Callback Prontu incompleto: {resultado}")
            return False
        
        return True
    
    def processar_callback(self, dados_callback: Dict[str, Any]) -> Dict[str, Any]:
        """Processa callback do Prontu"""
        
        if not self.validar_callback(dados_callback):
            raise PagamentoInvalido("Callback inválido")
        
        resultado = dados_callback['result']
        status_prontu = resultado.get('status', '').lower()
        status_novo = self.STATUS_MAP.get(status_prontu, 'PENDING')
        
        return {
            'referencia_pagamento': resultado.get('reference_id'),
            'referencia_gateway': resultado.get('prontu_transaction_id') or resultado.get('id'),
            'status': status_novo,
            'resposta_completa': resultado,
            'motivo': f"Callback Prontu - Status: {status_prontu}"
        }
    
    def verificar_status(self, referencia_gateway: str) -> Dict[str, Any]:
        """Verifica status de transação no Prontu"""
        
        try:
            # Assumindo endpoint de verificação
            resposta = self.fazer_requisicao(
                'GET',
                f'transactions/{referencia_gateway}'
            )
            
            status_prontu = resposta.get('status', '').lower()
            status_novo = self.STATUS_MAP.get(status_prontu, 'PENDING')
            
            return {
                'status': status_novo,
                'resposta_completa': resposta
            }
        except Exception as e:
            logger.error(f"Erro ao verificar status no Prontu: {str(e)}")
            raise GatewayIndisponivel("Não foi possível verificar o status")
    
    def _limpar_telefone(self, telefone: str) -> str:
        """Remove caracteres especiais do telefone"""
        return ''.join(c for c in telefone if c.isdigit())


def _obter_nome_usuario(usuario) -> str:
    """Obtém o nome do usuário de forma segura"""
    if not usuario:
        return 'Usuário'
    if hasattr(usuario, 'nome') and usuario.nome:
        return usuario.nome
    if hasattr(usuario, 'get_full_name') and usuario.get_full_name():
        return usuario.get_full_name()
    return getattr(usuario, 'email', 'Usuário')


def _obter_telefone_usuario(usuario) -> str:
    """Obtém o telefone do usuário com fallback de segurança"""
    if not usuario:
        return '244923456789'
    try:
        if hasattr(usuario, 'aluno_profile') and usuario.aluno_profile:
            aluno = usuario.aluno_profile
            if hasattr(aluno, 'perfil') and aluno.perfil and aluno.perfil.telefone:
                return aluno.perfil.telefone
    except Exception:
        pass
    
    # Tentar também outros atributos comuns
    for attr in ['phone', 'telefone', 'mobile']:
        if hasattr(usuario, attr):
            val = getattr(usuario, attr)
            if val:
                return val
                
    return '244923456789'


class PaymentService:
    """Serviço principal de pagamentos - Orquestração"""
    
    GATEWAYS = {
        'PRONTU': ProntuPaymentGateway,
    }
    
    def __init__(self):
        self.config = ConfiguracaoPagamento.get_config()
        self.gateway_atual = self._inicializar_gateway(self.config.gateway_padrao)
    
    def _inicializar_gateway(self, nome_gateway: str) -> PaymentGateway:
        """Inicializa o gateway apropriado"""
        
        if nome_gateway not in self.GATEWAYS:
            raise ValueError(f"Gateway não suportado: {nome_gateway}")
        
        if nome_gateway == 'PRONTU':
            api_url = settings.PRONTU_API_URL
            api_key = settings.PRONTU_API_KEY
        else:
            raise ValueError(f"Configuração não encontrada para {nome_gateway}")
        
        gateway_class = self.GATEWAYS[nome_gateway]
        return gateway_class(api_url, api_key)
    
    @transaction.atomic
    def criar_pagamento(
        self,
        usuario,
        tipo_pagamento: str,
        valor: Decimal,
        moeda: str = 'AOA',
        curso=None,
        plano=None,
        numero_parcela: int = None,
        url_sucesso: str = None,
        url_cancelamento: str = None,
        metadados: Dict[str, Any] = None,
        desconto_extra: Decimal = None,
    ) -> Pagamento:
        """
        Cria um novo pagamento no sistema e no gateway.
        Implementa padrão de transação segura.
        """
        
        if not self.config.pagamentos_ativados:
            raise PagamentoException("Pagamentos estão desativados no sistema")
        
        # Validar usuario
        if not usuario or not usuario.is_authenticated:
            raise PagamentoInvalido("Usuário não autenticado")
        
        # Validar valor
        if valor <= 0:
            raise PagamentoInvalido("Valor deve ser maior que zero")
        
        # Gerar referência única
        referencia_pagamento = self._gerar_referencia_pagamento()
        
        # Calcular valor com desconto
        valor_desconto = Decimal('0')
        if tipo_pagamento == 'INSCRICAO' and self.config.desconto_inscricao_percentual > 0:
            valor_desconto = valor * (self.config.desconto_inscricao_percentual / 100)
        valor_desconto = min(valor, valor_desconto + (desconto_extra or Decimal('0')))
        valor_final = max(Decimal('0.01'), valor - valor_desconto)
        
        # Criar URL de callback
        url_callback = self._construir_url_callback(referencia_pagamento)
        
        # Preparar dados do pagamento
        nome_usuario = _obter_nome_usuario(usuario)
        telefone_usuario = _obter_telefone_usuario(usuario)
        
        descricao = self._gerar_descricao_pagamento(tipo_pagamento, curso, numero_parcela)
        
        logger.info(f"Iniciando criação de pagamento: {referencia_pagamento}")
        
        try:
            # Chamar gateway para criar transação
            dados_gateway = self.gateway_atual.criar_transacao(
                referencia_pagamento=referencia_pagamento,
                usuario_nome=nome_usuario,
                usuario_email=usuario.email,
                usuario_telefone=telefone_usuario,
                valor=valor_final,
                moeda=moeda,
                descricao=descricao,
                url_callback=url_callback,
                url_retorno=url_sucesso or settings.FRONTEND_RETURN_URL,
                url_cancelamento=url_cancelamento or settings.FRONTEND_CANCEL_URL,
                metadados=metadados or {}
            )
            
            # Criar registro no banco de dados
            pagamento = Pagamento.objects.create(
                referencia_pagamento=referencia_pagamento,
                usuario=usuario,
                tipo_pagamento=tipo_pagamento,
                curso=curso,
                plano=plano,
                numero_parcela=numero_parcela,
                moeda=moeda,
                valor=valor,
                valor_desconto=valor_desconto,
                valor_final=valor_final,
                gateway=self.config.gateway_padrao,
                referencia_gateway=dados_gateway.get('referencia_gateway'),
                url_pagamento=dados_gateway.get('url_pagamento'),
                status=dados_gateway.get('status', 'PENDING'),
                url_sucesso=url_sucesso,
                url_cancelamento=url_cancelamento,
                metadados=metadados or {},
                resposta_gateway=dados_gateway.get('resposta_completa', {}),
                data_vencimento=timezone.now() + timedelta(
                    minutes=self.config.tempo_expiracao_link_minutos
                ),
                tentativas_pagamento=0
            )
            
            logger.info(f"Pagamento criado com sucesso: {referencia_pagamento}")
            
            return pagamento
        
        except PagamentoException as e:
            logger.error(f"Erro ao criar pagamento: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado ao criar pagamento: {str(e)}")
            raise PagamentoException(f"Erro ao criar pagamento: {str(e)}")
    
    def processar_webhook(
        self,
        dados_callback: Dict[str, Any],
        ip_address: str = None,
        user_agent: str = None
    ) -> Tuple[Pagamento, bool]:
        """
        Processa callback do gateway.
        Retorna (Pagamento, sucesso_processamento)
        """
        
        logger.info(f"Processando webhook: {json.dumps(dados_callback)}")
        
        try:
            # Processar callback do gateway
            dados_processados = self.gateway_atual.processar_callback(dados_callback)
            
            referencia_pagamento = dados_processados['referencia_pagamento']
            novo_status = dados_processados['status']
            
            # Buscar pagamento
            try:
                pagamento = Pagamento.objects.get(referencia_pagamento=referencia_pagamento)
            except Pagamento.DoesNotExist:
                logger.error(f"Pagamento não encontrado: {referencia_pagamento}")
                raise PagamentoInvalido(f"Pagamento não encontrado: {referencia_pagamento}")
            
            # Atualizar status
            self._atualizar_status_pagamento(
                pagamento,
                novo_status,
                dados_processados['resposta_completa'],
                dados_processados['motivo'],
                ip_address,
                user_agent,
                criado_por='WEBHOOK'
            )
            
            # Se pagamento aceito, executar ações
            if pagamento.eh_pago():
                self._processar_pagamento_aceito(pagamento)
            
            logger.info(f"Webhook processado com sucesso: {referencia_pagamento}")
            return pagamento, True
        
        except PagamentoException as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return None, False
        except Exception as e:
            logger.error(f"Erro inesperado ao processar webhook: {str(e)}")
            return None, False
    
    def fazer_retry_pagamento(self, pagamento: Pagamento) -> Pagamento:
        """Cria novo link de pagamento para transação expirada/rejeitada"""
        
        if not pagamento.pode_fazer_retry():
            raise PagamentoException(
                f"Pagamento não pode fazer retry no status {pagamento.get_status_display()}"
            )
        
        if pagamento.tentativas_pagamento >= self.config.max_tentativas_pagamento:
            raise PagamentoException("Número máximo de tentativas atingido")
        
        logger.info(f"Fazendo retry de pagamento: {pagamento.referencia_pagamento}")
        
        try:
            # Recriar transação no gateway
            dados_gateway = self.gateway_atual.criar_transacao(
                referencia_pagamento=pagamento.referencia_pagamento,
                usuario_nome=_obter_nome_usuario(pagamento.usuario),
                usuario_email=pagamento.usuario.email,
                usuario_telefone=_obter_telefone_usuario(pagamento.usuario),
                valor=pagamento.valor_final,
                moeda=pagamento.moeda,
                descricao=self._gerar_descricao_pagamento(
                    pagamento.tipo_pagamento,
                    pagamento.curso,
                    pagamento.numero_parcela
                ),
                url_callback=self._construir_url_callback(pagamento.referencia_pagamento),
                url_retorno=pagamento.url_sucesso or settings.FRONTEND_RETURN_URL,
                url_cancelamento=pagamento.url_cancelamento or settings.FRONTEND_CANCEL_URL,
            )
            
            # Atualizar pagamento
            pagamento.referencia_gateway = dados_gateway.get('referencia_gateway')
            pagamento.url_pagamento = dados_gateway.get('url_pagamento')
            pagamento.status = 'PENDING'
            pagamento.resposta_gateway = dados_gateway.get('resposta_completa', {})
            pagamento.data_vencimento = timezone.now() + timedelta(
                minutes=self.config.tempo_expiracao_link_minutos
            )
            pagamento.tentativas_pagamento += 1
            pagamento.save()
            
            # Registrar no histórico
            self._atualizar_status_pagamento(
                pagamento,
                'PENDING',
                dados_gateway.get('resposta_completa', {}),
                f'Retry #{pagamento.tentativas_pagamento}',
                criado_por='MANUAL'
            )
            
            logger.info(f"Retry realizado com sucesso: {pagamento.referencia_pagamento}")
            return pagamento
        
        except Exception as e:
            logger.error(f"Erro ao fazer retry: {str(e)}")
            raise PagamentoException(f"Erro ao fazer retry: {str(e)}")
    
    def verificar_status_atualizado(self, pagamento: Pagamento) -> Pagamento:
        """Verifica status atual no gateway e atualiza localmente"""
        
        if not pagamento.referencia_gateway:
            raise PagamentoException("Pagamento não tem referência no gateway")
        
        try:
            dados_status = self.gateway_atual.verificar_status(pagamento.referencia_gateway)
            novo_status = dados_status['status']
            
            if novo_status != pagamento.status:
                self._atualizar_status_pagamento(
                    pagamento,
                    novo_status,
                    dados_status.get('resposta_completa', {}),
                    'Verificação de status',
                    criado_por='SISTEMA'
                )
                
                if pagamento.eh_pago():
                    self._processar_pagamento_aceito(pagamento)
            
            return pagamento
        
        except Exception as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            raise
    
    def _atualizar_status_pagamento(
        self,
        pagamento: Pagamento,
        novo_status: str,
        resposta_gateway: Dict[str, Any] = None,
        motivo: str = '',
        ip_address: str = None,
        user_agent: str = None,
        criado_por: str = 'SISTEMA'
    ):
        """Atualiza status do pagamento com registro de auditoria"""
        
        if novo_status == pagamento.status:
            return  # Sem mudanças
        
        status_anterior = pagamento.status
        pagamento.atualizar_status(novo_status, resposta_gateway)
        
        # Registrar no histórico
        HistoricoPagamento.objects.create(
            pagamento=pagamento,
            status_anterior=status_anterior,
            status_novo=novo_status,
            motivo=motivo,
            referencia_gateway=pagamento.referencia_gateway,
            resposta_gateway=resposta_gateway or {},
            criado_por=criado_por,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        logger.info(
            f"Status atualizado: {pagamento.referencia_pagamento} "
            f"{status_anterior} → {novo_status}"
        )
    
    def _processar_pagamento_aceito(self, pagamento: Pagamento):
        """Ações a executar quando pagamento é aceito"""
        
        try:
            # Enviar email de confirmação
            self._enviar_email_confirmacao(pagamento)
            
            # Notificar admin se configurado
            if self.config.notificar_admin_pagamento_recebido:
                self._notificar_admin(pagamento)
            
            # Ativar a inscrição associada se o pagamento for de inscrição
            if pagamento.tipo_pagamento == 'INSCRICAO' and pagamento.curso:
                from cursos_app.models import Inscricao
                from cursos_app.utils import atribuir_turma_automatica
                
                inscricao_id = None
                if pagamento.metadados:
                    if isinstance(pagamento.metadados, str):
                        try:
                            meta_dict = json.loads(pagamento.metadados)
                        except Exception:
                            meta_dict = {}
                    else:
                        meta_dict = pagamento.metadados
                    
                    inscricao_id = meta_dict.get('inscricao_id')
                
                inscricao = None
                if inscricao_id:
                    try:
                        inscricao = Inscricao.objects.get(id=inscricao_id)
                    except (Inscricao.DoesNotExist, ValueError):
                        logger.warning(f"Inscrição com ID {inscricao_id} não encontrada.")
                
                # Fallback: buscar inscrição pendente para este aluno e curso
                if not inscricao:
                    inscricao = Inscricao.objects.filter(
                        aluno__usuario=pagamento.usuario,
                        curso=pagamento.curso,
                        status='P'
                    ).order_by('-data_inscricao').first()
                
                if inscricao:
                    if inscricao.status != 'A':
                        inscricao.pagamento_simulado = False
                        inscricao.forma_pagamento = 'CARTAO_CREDITO'
                        inscricao.valor_pago = pagamento.valor_final
                        inscricao.data_pagamento = timezone.now()
                        inscricao.status = 'A'
                        inscricao.data_confirmacao = timezone.now()
                        inscricao.save()
                        
                        # Atribuir turma automática
                        atribuir_turma_automatica(inscricao)
                        
                        # Enviar email de status
                        try:
                            inscricao.enviar_email_status()
                        except Exception as e_mail:
                            logger.error(f"Erro ao enviar email de status da inscrição: {e_mail}")
                            
                        logger.info(f"Inscrição {inscricao.id} ativada automaticamente pós-pagamento com sucesso!")
                    else:
                        logger.info(f"Inscrição {inscricao.id} já estava ativa.")
                else:
                    logger.warning(f"Nenhuma inscrição correspondente encontrada para pagamento {pagamento.referencia_pagamento}")

            elif pagamento.tipo_pagamento == 'BILHETE_EVENTO':
                from eventos_marketplace.models import Bilhete, LoteBilhete, PedidoBilhete
                metadados = pagamento.metadados or {}
                if isinstance(metadados, str):
                    try:
                        metadados = json.loads(metadados)
                    except (TypeError, ValueError):
                        metadados = {}
                pedido_id = metadados.get('pedido_bilhete_id')
                if pedido_id:
                    with transaction.atomic():
                        pedido = PedidoBilhete.objects.select_for_update().select_related('lote', 'evento').get(id=pedido_id)
                        if pedido.status != 'PAGO':
                            lote = LoteBilhete.objects.select_for_update().get(id=pedido.lote_id)
                            quantidade = pedido.quantidade
                            if lote.lugares_disponiveis < quantidade:
                                logger.error(f'Inventário insuficiente para o pedido de bilhete {pedido.referencia}.')
                                return
                            for _ in range(quantidade):
                                Bilhete.objects.create(
                                    pedido=pedido,
                                    lote=lote,
                                    nome_participante=pedido.nome_comprador,
                                    email_participante=pedido.email_comprador,
                                )
                            lote.quantidade_vendida += quantidade
                            lote.save(update_fields=['quantidade_vendida'])
                            pedido.status = 'PAGO'
                            pedido.pago_em = timezone.now()
                            pedido.save(update_fields=['status', 'pago_em'])
                            if pedido.evento.lotes.filter(activo=True, quantidade_vendida__lt=models.F('quantidade_total')).count() == 0:
                                pedido.evento.status = 'ESGOTADO'
                                pedido.evento.save(update_fields=['status', 'actualizado_em'])
                            logger.info(f'Pedido de bilhetes {pedido.referencia} confirmado e {quantidade} bilhete(s) emitido(s).')

            elif pagamento.tipo_pagamento == 'INSCRICAO_VIDEO':
                curso_video_id = None
                if pagamento.metadados:
                    if isinstance(pagamento.metadados, str):
                        try:
                            meta_dict = json.loads(pagamento.metadados)
                        except Exception:
                            meta_dict = {}
                    else:
                        meta_dict = pagamento.metadados
                    curso_video_id = meta_dict.get('curso_video_id')
                
                if curso_video_id:
                    from cursovideoapp.models import Curso_video
                    try:
                        curso_video = Curso_video.objects.get(id=curso_video_id)
                        aluno = pagamento.usuario.aluno_profile
                        curso_video.inscritos.add(aluno)
                        logger.info(f"Aluno {aluno.id} adicionado ao Curso Video {curso_video_id} após pagamento.")
                    except Exception as e:
                        logger.error(f"Erro ao processar INSCRICAO_VIDEO: {e}")

            elif pagamento.tipo_pagamento == 'ASSINATURA_PLANO' and pagamento.plano:
                from planos.models import AssinaturaMembro
                try:
                    # O pagamento da subscrição é feito pelo utilizador associado à sede do centro.
                    assinatura = AssinaturaMembro.objects.get(centro__usuario=pagamento.usuario)

                    # Webhooks repetidos não podem prolongar a mesma subscrição duas vezes.
                    metadados = pagamento.metadados or {}
                    if isinstance(metadados, str):
                        try:
                            metadados = json.loads(metadados)
                        except (TypeError, ValueError):
                            metadados = {}
                    if metadados.get('assinatura_ativada_em'):
                        logger.info(
                            f"Assinatura já processada para o pagamento {pagamento.referencia_pagamento}."
                        )
                        return

                    agora = timezone.now()
                    mesma_assinatura_ativa = (
                        assinatura.status == 'ATIVO'
                        and assinatura.plano_id == pagamento.plano_id
                        and assinatura.data_fim
                        and assinatura.data_fim > agora
                    )

                    assinatura.plano = pagamento.plano
                    assinatura.data_inicio = assinatura.data_fim if mesma_assinatura_ativa else agora
                    assinatura.data_fim = (
                        assinatura.data_fim + timedelta(days=30)
                        if mesma_assinatura_ativa
                        else agora + timedelta(days=30)
                    )
                    assinatura.status = 'ATIVO'
                    assinatura.save(update_fields=['plano', 'data_inicio', 'data_fim', 'status'])

                    metadados['assinatura_ativada_em'] = agora.isoformat()
                    metadados['assinatura_id'] = assinatura.pk
                    pagamento.metadados = metadados
                    pagamento.save(update_fields=['metadados'])

                    logger.info(
                        f"Assinatura do centro {assinatura.centro.nome} atualizada para plano "
                        f"{pagamento.plano.nome} com sucesso!"
                    )
                except AssinaturaMembro.DoesNotExist:
                    logger.error(
                        f"Nenhuma assinatura encontrada para o utilizador {pagamento.usuario_id} "
                        f"ao processar o pagamento {pagamento.referencia_pagamento}."
                    )
                except AssinaturaMembro.MultipleObjectsReturned:
                    logger.error(
                        f"Mais de uma assinatura encontrada para o utilizador {pagamento.usuario_id}."
                    )
                except Exception as e:
                    logger.error(f"Erro ao processar ASSINATURA_PLANO: {e}")

            logger.info(f"Ações pós-pagamento executadas: {pagamento.referencia_pagamento}")
        
        except Exception as e:
            logger.error(f"Erro ao executar ações pós-pagamento: {str(e)}")
            # Não falhar o fluxo principal
    
    def _enviar_email_confirmacao(self, pagamento: Pagamento):
        """Envia email de confirmação de pagamento"""
        
        try:
            contexto = {
                'usuario': pagamento.usuario,
                'pagamento': pagamento,
                'curso': pagamento.curso,
                'data': timezone.now(),
            }
            
            mensagem_html = render_to_string(
                'pagamentos/email_confirmacao.html',
                contexto
            )
            
            send_mail(
                subject=f'Pagamento Confirmado - {pagamento.referencia_pagamento}',
                message='Seu pagamento foi confirmado com sucesso.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[pagamento.usuario.email],
                html_message=mensagem_html,
                fail_silently=True
            )
            
            logger.info(f"Email de confirmação enviado: {pagamento.usuario.email}")
        
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
    
    def _notificar_admin(self, pagamento: Pagamento):
        """Notifica administrador sobre novo pagamento"""
        
        try:
            from django.contrib.auth import get_user_model
            Admin = get_user_model()
            
            admins = Admin.objects.filter(is_staff=True, is_superuser=True)
            
            if not admins:
                return
            
            contexto = {
                'pagamento': pagamento,
                'usuario': pagamento.usuario,
                'curso': pagamento.curso,
            }
            
            mensagem_html = render_to_string(
                'pagamentos/email_notificacao_admin.html',
                contexto
            )
            
            send_mail(
                subject=f'Novo Pagamento Recebido - {pagamento.referencia_pagamento}',
                message=f'Pagamento de {pagamento.valor_final} {pagamento.moeda}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email for admin in admins],
                html_message=mensagem_html,
                fail_silently=True
            )
        
        except Exception as e:
            logger.error(f"Erro ao notificar admin: {str(e)}")
    
    def _gerar_referencia_pagamento(self) -> str:
        """Gera referência única de pagamento"""
        
        while True:
            # Formato: PAG-[TIMESTAMP]-[RANDOM]
            referencia = f"PAG-{timezone.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Verificar se já existe
            if not Pagamento.objects.filter(referencia_pagamento=referencia).exists():
                return referencia
    
    def _construir_url_callback(self, referencia_pagamento: str) -> str:
        """Constrói URL de callback do webhook"""
        
        base_url = settings.PRONTU_CALLBACK_URL or f"{settings.SITE_DOMAIN}/api/v1/pagamentos/webhook/prontu/"
        return f"{base_url}?ref={referencia_pagamento}"
    
    def _gerar_descricao_pagamento(
        self,
        tipo_pagamento: str,
        curso=None,
        numero_parcela: int = None
    ) -> str:
        """Gera descrição do pagamento para o gateway"""
        
        tipos = dict(Pagamento.TIPO_CHOICES)
        tipo_texto = tipos.get(tipo_pagamento, tipo_pagamento)
        
        if curso:
            descricao = f"{tipo_texto} - {curso.titulo}"
        else:
            descricao = tipo_texto
        
        if numero_parcela:
            descricao += f" (Parcela {numero_parcela})"
        
        return descricao[:500]  # Limitar comprimento


def get_payment_service() -> PaymentService:
    """Factory para obter instância do serviço de pagamentos.
    
    Cria nova instância a cada chamada para garantir que configurações
    actualizadas (ex: GATEWAY_MOCK) sejam sempre utilizadas.
    """
    return PaymentService()
