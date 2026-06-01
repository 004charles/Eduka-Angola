import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
import json

User = get_user_model()


class Pagamento(models.Model):
    """
    Modelo central para todos os pagamentos no sistema.
    Suporta múltiplos gateways de pagamento (Prontu, etc).
    """
    
    MOEDA_CHOICES = [
        ('AOA', _('Kwanza (AOA)')),
        ('EUR', _('Euro (EUR)')),
        ('USD', _('Dólar (USD)')),
    ]
    
    GATEWAY_CHOICES = [
        ('PRONTU', 'Prontu'),
        ('STRIPE', 'Stripe'),
        ('PAYPAL', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', _('Pendente')),
        ('REQUESTED', _('Solicitado')),
        ('PROCESSING', _('Processando')),
        ('ACCEPTED', _('Aceite')),
        ('REJECTED', _('Rejeitado')),
        ('EXPIRED', _('Expirado')),
        ('CANCELLED', _('Cancelado')),
        ('REFUNDED', _('Reembolsado')),
    ]
    
    TIPO_CHOICES = [
        ('INSCRICAO', _('Inscrição em Curso')),
        ('PAGAMENTO_CURSO', _('Pagamento do Curso')),
        ('PARCELAMENTO', _('Parcela do Curso')),
        ('TAXA_ADMINISTRATIVO', _('Taxa Administrativa')),
        ('OUTRO', _('Outro')),
    ]
    
    # Identificadores únicos
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    referencia_pagamento = models.CharField(
        _('Referência de Pagamento'),
        max_length=100,
        unique=True,
        db_index=True,
        help_text='ID único do pagamento gerado pelo sistema'
    )
    
    # Informações do usuário e item pago
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='pagamentos',
        verbose_name=_('Usuário')
    )
    tipo_pagamento = models.CharField(
        _('Tipo de Pagamento'),
        max_length=50,
        choices=TIPO_CHOICES,
        default='INSCRICAO'
    )
    curso = models.ForeignKey(
        'cursos_app.Curso',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='pagamentos',
        verbose_name=_('Curso')
    )
    numero_parcela = models.PositiveIntegerField(
        _('Número da Parcela'),
        null=True,
        blank=True,
        help_text='Se aplicável, indica qual parcela está sendo paga'
    )
    
    # Valores
    moeda = models.CharField(
        _('Moeda'),
        max_length=3,
        choices=MOEDA_CHOICES,
        default='AOA'
    )
    valor = models.DecimalField(
        _('Valor do Pagamento'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    valor_desconto = models.DecimalField(
        _('Valor do Desconto'),
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    valor_final = models.DecimalField(
        _('Valor Final'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Informações do gateway
    gateway = models.CharField(
        _('Gateway de Pagamento'),
        max_length=50,
        choices=GATEWAY_CHOICES,
        default='PRONTU'
    )
    referencia_gateway = models.CharField(
        _('Referência do Gateway'),
        max_length=200,
        blank=True,
        null=True,
        db_index=True,
        help_text='ID da transação fornecido pelo gateway'
    )
    url_pagamento = models.URLField(
        _('URL de Pagamento'),
        blank=True,
        null=True,
        help_text='URL para redirecionamento do cliente'
    )
    
    # Status
    status = models.CharField(
        _('Status do Pagamento'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )
    
    # URLs de retorno
    url_sucesso = models.URLField(
        _('URL de Sucesso'),
        blank=True,
        null=True,
        help_text='Onde redirecionar após pagamento bem-sucedido'
    )
    url_cancelamento = models.URLField(
        _('URL de Cancelamento'),
        blank=True,
        null=True,
        help_text='Onde redirecionar em caso de cancelamento'
    )
    
    # Metadados
    metadados = models.JSONField(
        _('Metadados'),
        default=dict,
        blank=True,
        help_text='Dados adicionais em formato JSON'
    )
    resposta_gateway = models.JSONField(
        _('Resposta do Gateway'),
        default=dict,
        blank=True,
        help_text='Resposta completa do gateway (para auditoria)'
    )
    
    # Datas
    data_criacao = models.DateTimeField(
        _('Data de Criação'),
        auto_now_add=True,
        db_index=True
    )
    data_atualizacao = models.DateTimeField(
        _('Data de Atualização'),
        auto_now=True
    )
    data_vencimento = models.DateTimeField(
        _('Data de Vencimento'),
        null=True,
        blank=True,
        help_text='Quando o link de pagamento expira'
    )
    data_pagamento = models.DateTimeField(
        _('Data do Pagamento'),
        null=True,
        blank=True,
        help_text='Quando o pagamento foi confirmado'
    )
    
    # Tentativos
    tentativas_pagamento = models.PositiveIntegerField(
        _('Tentativas de Pagamento'),
        default=0,
        help_text='Número de tentativas de pagamento'
    )
    
    # Controle de processamento
    webhook_processado = models.BooleanField(
        _('Webhook Processado'),
        default=False,
        help_text='Se o callback do gateway foi processado'
    )
    
    class Meta:
        verbose_name = _('Pagamento')
        verbose_name_plural = _('Pagamentos')
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['curso', 'status']),
            models.Index(fields=['referencia_pagamento']),
            models.Index(fields=['referencia_gateway']),
            models.Index(fields=['data_criacao']),
        ]
    
    def __str__(self):
        return f"{self.referencia_pagamento} - {self.usuario} - {self.get_status_display()}"
    
    def eh_pago(self):
        """Verifica se o pagamento foi confirmado"""
        return self.status in ['ACCEPTED', 'REFUNDED']
    
    def pode_fazer_retry(self):
        """Verifica se pode fazer retry de pagamento"""
        return self.status in ['REJECTED', 'EXPIRED', 'CANCELLED']
    
    def pode_reembolsar(self):
        """Verifica se pode reembolsar"""
        return self.status == 'ACCEPTED'
    
    def atualizar_status(self, novo_status, resposta_gateway=None):
        """Atualiza o status do pagamento de forma segura"""
        if novo_status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Status inválido: {novo_status}")
        
        self.status = novo_status
        if resposta_gateway:
            self.resposta_gateway = resposta_gateway
        self.data_atualizacao = timezone.now()
        
        if novo_status == 'ACCEPTED':
            self.data_pagamento = timezone.now()
            self.webhook_processado = True
        
        self.save(update_fields=['status', 'resposta_gateway', 'data_atualizacao', 'data_pagamento', 'webhook_processado'])


class HistoricoPagamento(models.Model):
    """
    Auditoria completa de todas as mudanças de pagamento.
    Mantém rastreabilidade do fluxo de pagamento.
    """
    
    pagamento = models.ForeignKey(
        Pagamento,
        on_delete=models.CASCADE,
        related_name='historico',
        verbose_name=_('Pagamento')
    )
    status_anterior = models.CharField(
        _('Status Anterior'),
        max_length=20,
        choices=Pagamento.STATUS_CHOICES
    )
    status_novo = models.CharField(
        _('Status Novo'),
        max_length=20,
        choices=Pagamento.STATUS_CHOICES
    )
    motivo = models.TextField(
        _('Motivo'),
        blank=True,
        help_text='Motivo da mudança de status'
    )
    referencia_gateway = models.CharField(
        _('Referência do Gateway'),
        max_length=200,
        blank=True,
        help_text='ID da transação do gateway'
    )
    resposta_gateway = models.JSONField(
        _('Resposta do Gateway'),
        default=dict,
        blank=True
    )
    criado_por = models.CharField(
        _('Criado Por'),
        max_length=100,
        choices=[
            ('SISTEMA', 'Sistema'),
            ('WEBHOOK', 'Webhook'),
            ('MANUAL', 'Manual'),
            ('ADMIN', 'Admin'),
        ],
        default='SISTEMA'
    )
    data_criacao = models.DateTimeField(
        _('Data de Criação'),
        auto_now_add=True,
        db_index=True
    )
    ip_address = models.GenericIPAddressField(
        _('Endereço IP'),
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        _('User Agent'),
        blank=True
    )
    
    class Meta:
        verbose_name = _('Histórico de Pagamento')
        verbose_name_plural = _('Históricos de Pagamento')
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['pagamento', 'data_criacao']),
        ]
    
    def __str__(self):
        return f"{self.pagamento.referencia_pagamento}: {self.status_anterior} → {self.status_novo}"


class TentativaPagamento(models.Model):
    """
    Registra cada tentativa de pagamento para análise e debugging.
    """
    
    pagamento = models.ForeignKey(
        Pagamento,
        on_delete=models.CASCADE,
        related_name='tentativas',
        verbose_name=_('Pagamento')
    )
    numero_tentativa = models.PositiveIntegerField(
        _('Número da Tentativa')
    )
    status_resposta = models.CharField(
        _('Status da Resposta'),
        max_length=20,
        choices=[
            ('SUCESSO', 'Sucesso'),
            ('ERRO', 'Erro'),
            ('TIMEOUT', 'Timeout'),
            ('INVALIDO', 'Inválido'),
        ]
    )
    codigo_erro = models.CharField(
        _('Código de Erro'),
        max_length=50,
        blank=True
    )
    mensagem_erro = models.TextField(
        _('Mensagem de Erro'),
        blank=True
    )
    resposta_gateway = models.JSONField(
        _('Resposta do Gateway'),
        default=dict,
        blank=True
    )
    tempo_resposta_ms = models.PositiveIntegerField(
        _('Tempo de Resposta (ms)'),
        null=True,
        blank=True
    )
    data_criacao = models.DateTimeField(
        _('Data de Criação'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        verbose_name = _('Tentativa de Pagamento')
        verbose_name_plural = _('Tentativas de Pagamento')
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Tentativa {self.numero_tentativa} - {self.pagamento.referencia_pagamento}"


class ConfiguracaoPagamento(models.Model):
    """
    Configurações globais de pagamento do sistema.
    Permite controlar comportamento sem mudar código.
    """
    
    # Gerais
    pagamentos_ativados = models.BooleanField(
        _('Pagamentos Ativados'),
        default=True
    )
    gateway_padrao = models.CharField(
        _('Gateway Padrão'),
        max_length=50,
        choices=Pagamento.GATEWAY_CHOICES,
        default='PRONTU'
    )
    moeda_padrao = models.CharField(
        _('Moeda Padrão'),
        max_length=3,
        choices=Pagamento.MOEDA_CHOICES,
        default='AOA'
    )
    
    # Tempos
    tempo_expiracao_link_minutos = models.PositiveIntegerField(
        _('Tempo de Expiração do Link (minutos)'),
        default=30,
        help_text='Quanto tempo o link de pagamento fica válido'
    )
    tempo_confirmacao_automatica_minutos = models.PositiveIntegerField(
        _('Tempo para Confirmação Automática (minutos)'),
        default=5,
        help_text='Aguarda este tempo para confirmar pagamento antes de expirar'
    )
    
    # Tentativas
    max_tentativas_pagamento = models.PositiveIntegerField(
        _('Máximo de Tentativas'),
        default=3
    )
    max_tentativas_webhook = models.PositiveIntegerField(
        _('Máximo de Tentativas de Webhook'),
        default=5
    )
    
    # Desconto
    desconto_inscricao_percentual = models.DecimalField(
        _('Desconto na Inscrição (%)'),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # Notificações
    notificar_admin_pagamento_recebido = models.BooleanField(
        _('Notificar Admin ao Receber Pagamento'),
        default=True
    )
    
    # Segurança
    exigir_verificacao_email = models.BooleanField(
        _('Exigir Verificação de Email'),
        default=True
    )
    exigir_cpf_valido = models.BooleanField(
        _('Exigir CPF/NIF Válido'),
        default=False
    )
    
    data_atualizacao = models.DateTimeField(
        _('Data de Atualização'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('Configuração de Pagamento')
        verbose_name_plural = _('Configurações de Pagamento')
        constraints = [
            models.CheckConstraint(
                condition=models.Q(tempo_expiracao_link_minutos__gt=0),
                name='tempo_expiracao_positivo'
            ),
            models.CheckConstraint(
                condition=models.Q(max_tentativas_pagamento__gt=0),
                name='max_tentativas_positivo'
            ),
        ]
    
    def __str__(self):
        return _("Configuração Global de Pagamentos")
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração global (sempre uma instância)"""
        config, created = cls.objects.get_or_create(id=1)
        return config


# Signals para auditoria automática
@receiver(post_save, sender=Pagamento)
def registrar_mudanca_pagamento(sender, instance, created, **kwargs):
    """
    Registra automaticamente mudanças no status do pagamento no histórico.
    """
    if created:
        # Novo pagamento criado
        HistoricoPagamento.objects.create(
            pagamento=instance,
            status_anterior='PENDING',
            status_novo=instance.status,
            motivo='Pagamento criado',
            criado_por='SISTEMA'
        )
