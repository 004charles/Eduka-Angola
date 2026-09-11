from rest_framework import serializers
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from .models import Pagamento, HistoricoPagamento


class PagamentoListaSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas"""
    
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    curso_titulo = serializers.CharField(source='curso.titulo', read_only=True, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Pagamento
        fields = [
            'referencia_pagamento',
            'usuario_nome',
            'tipo_pagamento',
            'curso_titulo',
            'valor_final',
            'moeda',
            'status',
            'status_display',
            'data_criacao',
            'data_pagamento'
        ]


class PagamentoDetalheSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes"""
    
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_email = serializers.EmailField(source='usuario.email', read_only=True)
    curso_titulo = serializers.CharField(source='curso.titulo', read_only=True, allow_null=True)
    curso_preco = serializers.DecimalField(
        source='curso.preco',
        max_digits=12,
        decimal_places=2,
        read_only=True,
        allow_null=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_pagamento_display', read_only=True)
    pode_fazer_retry = serializers.SerializerMethodField()
    eh_pago = serializers.SerializerMethodField()
    
    class Meta:
        model = Pagamento
        fields = [
            'id',
            'referencia_pagamento',
            'referencia_gateway',
            'usuario_nome',
            'usuario_email',
            'tipo_pagamento',
            'tipo_display',
            'curso_titulo',
            'curso_preco',
            'numero_parcela',
            'moeda',
            'valor',
            'valor_desconto',
            'valor_final',
            'gateway',
            'status',
            'status_display',
            'url_pagamento',
            'data_criacao',
            'data_atualizacao',
            'data_vencimento',
            'data_pagamento',
            'tentativas_pagamento',
            'pode_fazer_retry',
            'eh_pago',
            'metadados'
        ]
        read_only_fields = fields
    
    def get_pode_fazer_retry(self, obj):
        return obj.pode_fazer_retry()
    
    def get_eh_pago(self, obj):
        return obj.eh_pago()


class CriarPagamentoSerializer(serializers.Serializer):
    """Serializer para criação de pagamentos"""
    
    tipo_pagamento = serializers.ChoiceField(
        choices=Pagamento.TIPO_CHOICES,
        help_text=_('Tipo de pagamento')
    )
    valor = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01'),
        help_text=_('Valor a pagar')
    )
    moeda = serializers.ChoiceField(
        choices=Pagamento.MOEDA_CHOICES,
        default='AOA',
        required=False,
        help_text=_('Moeda do pagamento')
    )
    curso_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text=_('ID do curso (se aplicável)')
    )
    numero_parcela = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text=_('Número da parcela (se for parcelamento)')
    )
    url_sucesso = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text=_('URL para redirecionamento após sucesso')
    )
    url_cancelamento = serializers.URLField(
        required=False,
        allow_blank=True,
        help_text=_('URL para redirecionamento após cancelamento')
    )
    
    def _validate_return_url(self, value):
        """HIGH-14 FIX: Validar que URL de retorno pertence ao domínio permitido."""
        if not value:
            return value
        from urllib.parse import urlparse
        try:
            parsed = urlparse(value)
            allowed_hosts = [settings.FRONTEND_URL, settings.SITE_DOMAIN]
            # Adicionar localhost apenas em desenvolvimento
            if settings.DEBUG:
                allowed_hosts.extend(['localhost', '127.0.0.1'])
            if parsed.hostname and parsed.hostname not in allowed_hosts:
                raise serializers.ValidationError(
                    _('URL de retorno não pertence ao domínio permitido.')
                )
        except Exception:
            pass
        return value
    
    def validate_url_sucesso(self, value):
        return self._validate_return_url(value)
    
    def validate_url_cancelamento(self, value):
        return self._validate_return_url(value)
    
    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError(_('Valor deve ser maior que zero'))
        return value


class HistoricoPagamentoSerializer(serializers.ModelSerializer):
    """Serializer para histórico de pagamentos"""
    
    status_anterior_display = serializers.CharField(
        source='get_status_anterior_display',
        read_only=True
    )
    status_novo_display = serializers.CharField(
        source='get_status_novo_display',
        read_only=True
    )
    criado_por_display = serializers.CharField(
        source='get_criado_por_display',
        read_only=True
    )
    
    class Meta:
        model = HistoricoPagamento
        fields = [
            'status_anterior',
            'status_anterior_display',
            'status_novo',
            'status_novo_display',
            'motivo',
            'criado_por',
            'criado_por_display',
            'data_criacao'
        ]
        read_only_fields = fields


class RetryPagamentoSerializer(serializers.Serializer):
    """Serializer para fazer retry de pagamento"""
    
    referencia_pagamento = serializers.CharField(
        help_text=_('Referência do pagamento a fazer retry')
    )


class WebhookProntuSerializer(serializers.Serializer):
    """Serializer para validar webhook do Prontu"""
    
    result = serializers.JSONField(
        help_text=_('Resultado do pagamento')
    )
