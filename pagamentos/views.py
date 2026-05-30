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


class AllowAnyForCriar(BasePermission):
    """Permite acesso sem autenticação ao endpoint de criar pagamentos"""
    def has_permission(self, request, view):
        if view.action == 'criar':
            return True
        return request.user and request.user.is_authenticated


class PagamentoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para gerenciar pagamentos.
    
    Endpoints:
    - GET /api/pagamentos/ - Listar pagamentos do usuário
    - GET /api/pagamentos/{id}/ - Detalhes do pagamento
    - POST /api/pagamentos/criar/ - Criar novo pagamento (sem autenticação obrigatória para testes)
    - POST /api/pagamentos/{id}/retry/ - Fazer retry de pagamento
    - GET /api/pagamentos/{id}/historico/ - Ver histórico do pagamento
    """
    
    permission_classes = [AllowAnyForCriar]
    
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
        """Cria novo pagamento"""
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            servico = get_payment_service()
            
            # Se usuário anônimo, tentar obter usuário de teste ou criar
            usuario = request.user
            if not usuario or not usuario.is_authenticated:
                # Usar usuário de teste para pagamentos sem autenticação
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    usuario, created = User.objects.get_or_create(
                        email='test.payment@edukangola.ao',
                        defaults={
                            'nome': 'Test User',
                            'tipo_usuario': 'ALUNO'
                        }
                    )
                except:
                    # Se falhar, tentar usar admin
                    usuario = User.objects.filter(is_superuser=True).first()
                    if not usuario:
                        return Response(
                            {'error': 'Usuário não autenticado'},
                            status=status.HTTP_401_UNAUTHORIZED
                        )
            
            # Buscar curso se fornecido
            curso = None
            if 'curso_id' in serializer.validated_data:
                from cursos_app.models import Curso
                curso_id = serializer.validated_data['curso_id']
                if curso_id:
                    curso = get_object_or_404(Curso, id=curso_id)
            
            # Criar pagamento
            pagamento = servico.criar_pagamento(
                usuario=usuario,
                tipo_pagamento=serializer.validated_data['tipo_pagamento'],
                valor=serializer.validated_data['valor'],
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
                {
                    'sucesso': False,
                    'erro': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro inesperado ao criar pagamento: {str(e)}")
            return Response(
                {
                    'sucesso': False,
                    'erro': _('Erro ao criar pagamento. Tente novamente.')
                },
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
    """
    
    @action(detail=False, methods=['get', 'post'], url_path='prontu', url_name='prontu')
    def prontu_callback(self, request):
        """Processa callback do Prontu"""
        
        if request.method == 'GET':
            from django.conf import settings
            from django.shortcuts import redirect
            from django.contrib import messages
            from .models import Pagamento
            
            ref = request.GET.get('ref')
            if ref and settings.DEBUG:
                try:
                    pagamento = Pagamento.objects.get(referencia_pagamento=ref)
                    if not pagamento.eh_pago():
                        servico = get_payment_service()
                        servico._atualizar_status_pagamento(
                            pagamento,
                            'ACCEPTED',
                            {'motivo': 'Simulação de pagamento local'},
                            'Simulação de pagamento local',
                            criado_por='WEBHOOK'
                        )
                        servico._processar_pagamento_aceito(pagamento)
                        
                    messages.success(request, f"Pagamento {ref} simulado com sucesso!")
                    url_retorno = pagamento.url_sucesso or '/teste-pagamento/'
                    return redirect(url_retorno)
                except Exception as e:
                    logger.error(f"Erro na simulação do webhook: {e}")
                    
            return Response(
                {
                    'erro': 'Método não permitido ou parâmetros inválidos.'
                },
                status=status.HTTP_400_BAD_REQUEST
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
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            if sucesso:
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
                    {
                        'sucesso': False,
                        'mensagem': _('Erro ao processar callback')
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except ValidationError as e:
            logger.error(f"Erro de validação no webhook: {e}")
            return Response(
                {
                    'sucesso': False,
                    'erro': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except PagamentoInvalido as e:
            logger.error(f"Pagamento inválido: {str(e)}")
            return Response(
                {
                    'sucesso': False,
                    'erro': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return Response(
                {
                    'sucesso': False,
                    'erro': _('Erro ao processar callback')
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _obter_ip_cliente(self, request):
        """Extrai IP do cliente da request"""
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
