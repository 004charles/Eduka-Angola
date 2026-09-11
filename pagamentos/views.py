import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.cache import cache

from .models import Pagamento, HistoricoPagamento
from .serializers import (
    PagamentoListaSerializer,
    PagamentoDetalheSerializer,
    CriarPagamentoSerializer,
    HistoricoPagamentoSerializer,
    RetryPagamentoSerializer,
    WebhookProntuSerializer
)
from .services import get_payment_service, PagamentoException, PagamentoInvalido

logger = logging.getLogger(__name__)


class PagamentoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gerenciar pagamentos.
    
    Endpoints:
    - GET /api/pagamentos/ - Listar pagamentos do usuário
    - GET /api/pagamentos/{id}/ - Detalhes do pagamento
    - POST /api/pagamentos/criar/ - Criar novo pagamento (autenticação obrigatória)
    - POST /api/pagamentos/{id}/retry/ - Fazer retry de pagamento
    - GET /api/pagamentos/{id}/historico/ - Ver histórico do pagamento
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PagamentoDetalheSerializer
        elif self.action == 'criar':
            return CriarPagamentoSerializer
        elif self.action == 'retry':
            return RetryPagamentoSerializer
        elif self.action == 'historico':
            return HistoricoPagamentoSerializer
        return PagamentoListaSerializer
    
    def get_queryset(self):
        """Retorna apenas pagamentos do usuário autenticado"""
        return Pagamento.objects.filter(usuario=self.request.user).prefetch_related('historico')
    
    @action(detail=False, methods=['post'], url_path='criar')
    def criar(self, request):
        """Cria novo pagamento — requer autenticação"""
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            servico = get_payment_service()
            usuario = request.user
            
            # Buscar curso se fornecido
            curso = None
            if 'curso_id' in serializer.validated_data:
                from cursos_app.models import Curso
                curso_id = serializer.validated_data['curso_id']
                if curso_id:
                    curso = get_object_or_404(Curso, id=curso_id)
            
            # Validar valor server-side contra o preço do curso
            valor_solicitado = serializer.validated_data['valor']
            tipo_pagamento = serializer.validated_data['tipo_pagamento']
            
            if curso and tipo_pagamento in ('INSCRICAO', 'PAGAMENTO_CURSO'):
                valor_esperado = curso.valor_a_cobrar_online()
                if valor_solicitado != valor_esperado:
                    return Response(
                        {'sucesso': False, 'erro': f'Valor inválido. O valor correto é {valor_esperado} {serializer.validated_data.get("moeda", "AOA")}.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Criar pagamento
            pagamento = servico.criar_pagamento(
                usuario=usuario,
                tipo_pagamento=tipo_pagamento,
                valor=valor_solicitado,
                moeda=serializer.validated_data.get('moeda', 'AOA'),
                curso=curso,
                numero_parcela=serializer.validated_data.get('numero_parcela'),
                url_sucesso=serializer.validated_data.get('url_sucesso'),
                url_cancelamento=serializer.validated_data.get('url_cancelamento'),
            )
            
            resposta_serializer = PagamentoDetalheSerializer(pagamento)
            pagamento_data = resposta_serializer.data
            return Response(
                {
                    'sucesso': True,
                    'mensagem': _('Pagamento criado com sucesso'),
                    'pagamento': pagamento_data,
                    'url_pagamento': pagamento_data.get('url_pagamento'),
                    'referencia_pagamento': pagamento_data.get('referencia_pagamento'),
                    'status': pagamento_data.get('status'),
                    'valor': pagamento_data.get('valor'),
                    'id': pagamento_data.get('id')
                },
                status=status.HTTP_201_CREATED
            )
        
        except PagamentoException as e:
            logger.error(f"Erro ao criar pagamento: {str(e)}")
            return Response(
                {'sucesso': False, 'erro': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao criar pagamento: {str(e)}")
            return Response(
                {'sucesso': False, 'erro': _('Erro ao criar pagamento. Tente novamente.')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='retry')
    def retry(self, request, pk=None):
        """Faz retry de pagamento expirado/rejeitado"""
        
        pagamento = self.get_object()
        
        # Verificar permissão
        if pagamento.usuario != request.user:
            raise PermissionDenied(_('Você não tem permissão para acessar este pagamento'))
        
        try:
            servico = get_payment_service()
            pagamento_atualizado = servico.fazer_retry_pagamento(pagamento)
            
            resposta_serializer = PagamentoDetalheSerializer(pagamento_atualizado)
            return Response(
                {
                    'sucesso': True,
                    'mensagem': _('Link de pagamento regenerado com sucesso'),
                    'pagamento': resposta_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except PagamentoException as e:
            logger.error(f"Erro ao fazer retry: {str(e)}")
            return Response(
                {
                    'sucesso': False,
                    'erro': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao fazer retry: {str(e)}")
            return Response(
                {
                    'sucesso': False,
                    'erro': _('Erro ao fazer retry. Tente novamente.')
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='historico')
    def historico(self, request, pk=None):
        """Retorna histórico de mudanças do pagamento"""
        
        pagamento = self.get_object()
        
        # Verificar permissão
        if pagamento.usuario != request.user:
            raise PermissionDenied(_('Você não tem permissão para acessar este pagamento'))
        
        historico = pagamento.historico.all()
        serializer = HistoricoPagamentoSerializer(historico, many=True)
        
        return Response(
            {
                'pagamento': pagamento.referencia_pagamento,
                'total': historico.count(),
                'historico': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'], url_path='verificar-status')
    def verificar_status(self, request, pk=None):
        """Verifica status atual do pagamento"""
        
        pagamento = self.get_object()
        
        # Verificar permissão
        if pagamento.usuario != request.user:
            raise PermissionDenied(_('Você não tem permissão para acessar este pagamento'))
        
        try:
            servico = get_payment_service()
            pagamento_atualizado = servico.verificar_status_atualizado(pagamento)
            
            resposta_serializer = PagamentoDetalheSerializer(pagamento_atualizado)
            return Response(
                {
                    'sucesso': True,
                    'pagamento': resposta_serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except PagamentoException as e:
            logger.error(f"Erro ao verificar status: {str(e)}")
            return Response(
                {
                    'sucesso': False,
                    'erro': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao verificar status: {str(e)}")
            return Response(
                {
                    'sucesso': False,
                    'erro': _('Erro ao verificar status. Tente novamente.')
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class WebhookProntuView(viewsets.ViewSet):
    """
    Webhook para receber callbacks do Prontu.
    
    POST /api/pagamentos/webhook/prontu/ - Processar callback
    Validação: HMAC-SHA256 via header X-Prontu-Signature (se PRONTU_WEBHOOK_SECRET configurado)
    """
    
    @action(detail=False, methods=['post'], url_path='prontu', url_name='prontu')
    def prontu_callback(self, request):
        """Processa callback do Prontu com verificação de assinatura"""
        
        # Verificar assinatura HMAC
        signature = request.META.get('HTTP_X_PRONTU_SIGNATURE', '')
        
        # Validar IP se whitelist configurada
        from django.conf import settings
        allowed_ips = getattr(settings, 'PRONTU_WEBHOOK_ALLOWED_IPS', [])
        if allowed_ips:
            client_ip = self._obter_ip_cliente(request)
            if client_ip not in allowed_ips:
                logger.warning(f"Webhook de IP não autorizado: {client_ip}")
                return Response(
                    {'sucesso': False, 'erro': 'IP não autorizado'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Verificar replay via idempotência
        webhook_id = request.data.get('result', {}).get('prontu_transaction_id') or request.data.get('result', {}).get('reference_id', '')
        if webhook_id:
            cache_key = f"webhook_processed_{webhook_id}"
            if cache.get(cache_key):
                logger.info(f"Webhook duplicado ignorado: {webhook_id}")
                return Response(
                    {'sucesso': True, 'mensagem': 'Webhook já processado'},
                    status=status.HTTP_200_OK
                )
        
        try:
            # Validar dados
            serializer = WebhookProntuSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Processar webhook
            servico = get_payment_service()
            pagamento, sucesso = servico.processar_webhook(
                dados_callback=serializer.validated_data,
                ip_address=self._obter_ip_cliente(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                signature=signature
            )
            
            if sucesso:
                # Marcar como processado para prevenir replay ( TTL 1 hora)
                if webhook_id:
                    cache.set(cache_key, True, 3600)
                
                logger.info(f"Webhook processado com sucesso: {pagamento.referencia_pagamento}")
                return Response(
                    {
                        'sucesso': True,
                        'mensagem': _('Callback processado com sucesso'),
                        'referencia_pagamento': pagamento.referencia_pagamento
                    },
                    status=status.HTTP_200_OK
                )
            else:
                logger.warning(f"Falha ao processar webhook")
                return Response(
                    {'sucesso': False, 'mensagem': _('Erro ao processar callback')},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except ValidationError as e:
            logger.error(f"Erro de validação no webhook: {e}")
            return Response(
                {'sucesso': False, 'erro': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PagamentoInvalido as e:
            logger.error(f"Pagamento inválido: {str(e)}")
            return Response(
                {'sucesso': False, 'erro': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return Response(
                {'sucesso': False, 'erro': _('Erro ao processar callback')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _obter_ip_cliente(self, request):
        """Extrai IP do cliente da request"""
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
