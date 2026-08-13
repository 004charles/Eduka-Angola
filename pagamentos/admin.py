from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Pagamento, HistoricoPagamento, TentativaPagamento, ConfiguracaoPagamento


@admin.register(Pagamento)
class PagamentoAdmin(UnfoldModelAdmin):
    list_display = [
        'referencia_pagamento',
        'usuario_display',
        'tipo_pagamento',
        'valor_final',
        'moeda',
        'status_colored',
        'gateway',
        'data_criacao_formatada'
    ]
    list_filter = [
        'status',
        'gateway',
        'tipo_pagamento',
        'moeda',
        'data_criacao',
        'data_pagamento'
    ]
    search_fields = [
        'referencia_pagamento',
        'usuario__email',
        'usuario__first_name',
        'usuario__last_name',
        'referencia_gateway'
    ]
    readonly_fields = [
        'id',
        'referencia_pagamento',
        'data_criacao',
        'data_atualizacao',
        'data_pagamento',
        'resposta_gateway',
        'webhook_processado',
        'historico_display'
    ]
    
    fieldsets = (
        (_('Identificação'), {
            'fields': ('id', 'referencia_pagamento', 'referencia_gateway')
        }),
        (_('Informações do Usuário e Item'), {
            'fields': ('usuario', 'tipo_pagamento', 'curso', 'numero_parcela')
        }),
        (_('Valores'), {
            'fields': ('moeda', 'valor', 'valor_desconto', 'valor_final')
        }),
        (_('Gateway de Pagamento'), {
            'fields': ('gateway', 'url_pagamento', 'status')
        }),
        (_('URLs de Retorno'), {
            'fields': ('url_sucesso', 'url_cancelamento')
        }),
        (_('Datas'), {
            'fields': ('data_criacao', 'data_atualizacao', 'data_vencimento', 'data_pagamento'),
            'classes': ('collapse',)
        }),
        (_('Tentativas e Processamento'), {
            'fields': ('tentativas_pagamento', 'webhook_processado'),
            'classes': ('collapse',)
        }),
        (_('Resposta do Gateway'), {
            'fields': ('resposta_gateway',),
            'classes': ('collapse',)
        }),
        (_('Metadados'), {
            'fields': ('metadados',),
            'classes': ('collapse',)
        }),
        (_('Histórico'), {
            'fields': ('historico_display',),
            'classes': ('collapse',)
        }),
    )
    
    def usuario_display(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}"
    usuario_display.short_description = _('Usuário')
    usuario_display.admin_order_field = 'usuario__last_name'
    
    def status_colored(self, obj):
        colors = {
            'PENDING': '#FFA500',
            'REQUESTED': '#87CEEB',
            'PROCESSING': '#FFB6C1',
            'ACCEPTED': '#90EE90',
            'REJECTED': '#FF6347',
            'EXPIRED': '#D3D3D3',
            'CANCELLED': '#A9A9A9',
            'REFUNDED': '#DDA0DD',
        }
        color = colors.get(obj.status, '#000000')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = _('Status')
    status_colored.admin_order_field = 'status'
    
    def data_criacao_formatada(self, obj):
        return obj.data_criacao.strftime('%d/%m/%Y %H:%M')
    data_criacao_formatada.short_description = _('Criado em')
    data_criacao_formatada.admin_order_field = 'data_criacao'
    
    def historico_display(self, obj):
        historico = obj.historico.all()[:5]
        if not historico:
            return '-'
        return format_html(
            '<ul>{}</ul>',
            ''.join([
                format_html(
                    '<li>{} → {} ({})</li>',
                    h.get_status_anterior_display(),
                    h.get_status_novo_display(),
                    h.data_criacao.strftime('%d/%m/%Y %H:%M')
                )
                for h in historico
            ])
        )
    historico_display.short_description = _('Histórico Recente')
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    actions = ['marcar_como_processado']
    
    def marcar_como_processado(self, request, queryset):
        queryset.update(webhook_processado=True)
    marcar_como_processado.short_description = _('Marcar webhook como processado')


class HistoricoPagamentoInline(UnfoldTabularInline):
    model = HistoricoPagamento
    extra = 0
    readonly_fields = ['status_anterior', 'status_novo', 'motivo', 'criado_por', 'data_criacao']
    can_delete = False


@admin.register(HistoricoPagamento)
class HistoricoPagamentoAdmin(UnfoldModelAdmin):
    list_display = [
        'pagamento',
        'status_anterior',
        'seta',
        'status_novo',
        'criado_por',
        'data_criacao'
    ]
    list_filter = ['status_novo', 'criado_por', 'data_criacao']
    search_fields = ['pagamento__referencia_pagamento', 'motivo']
    readonly_fields = ['data_criacao', 'pagamento']
    
    def seta(self, obj):
        return '→'
    seta.short_description = ''
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TentativaPagamento)
class TentativaPagamentoAdmin(UnfoldModelAdmin):
    list_display = [
        'pagamento',
        'numero_tentativa',
        'status_resposta_colored',
        'codigo_erro',
        'tempo_resposta_ms',
        'data_criacao'
    ]
    list_filter = ['status_resposta', 'data_criacao']
    search_fields = ['pagamento__referencia_pagamento', 'codigo_erro', 'mensagem_erro']
    readonly_fields = ['pagamento', 'data_criacao', 'resposta_gateway']
    
    def status_resposta_colored(self, obj):
        colors = {
            'SUCESSO': '#90EE90',
            'ERRO': '#FF6347',
            'TIMEOUT': '#FFA500',
            'INVALIDO': '#D3D3D3',
        }
        color = colors.get(obj.status_resposta, '#000000')
        return format_html(
            '<span style="background-color: {}; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_resposta_display()
        )
    status_resposta_colored.short_description = _('Status')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConfiguracaoPagamento)
class ConfiguracaoPagamentoAdmin(UnfoldModelAdmin):
    fieldsets = (
        (_('Geral'), {
            'fields': ('pagamentos_ativados', 'gateway_padrao', 'moeda_padrao')
        }),
        (_('Tempos (minutos)'), {
            'fields': ('tempo_expiracao_link_minutos', 'tempo_confirmacao_automatica_minutos')
        }),
        (_('Tentativas'), {
            'fields': ('max_tentativas_pagamento', 'max_tentativas_webhook')
        }),
        (_('Descontos'), {
            'fields': ('desconto_inscricao_percentual',)
        }),
        (_('Notificações'), {
            'fields': ('notificar_admin_pagamento_recebido',)
        }),
        (_('Segurança'), {
            'fields': ('exigir_verificacao_email', 'exigir_cpf_valido')
        }),
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


from .models import FinanceiroCentro

@admin.register(FinanceiroCentro)
class FinanceiroCentroAdmin(UnfoldModelAdmin):
    list_display = [
        'centro',
        'periodo',
        'total_bruto_inscricoes',
        'percentual_comissao_plataforma',
        'valor_comissao_plataforma',
        'valor_liquido_centro',
        'pago',
        'data_criacao'
    ]
    list_filter = ['pago', 'periodo', 'centro']
    search_fields = ['centro__nome', 'periodo']
    readonly_fields = ['valor_comissao_plataforma', 'valor_liquido_centro', 'data_criacao']

    fieldsets = (
        (_('Centro & Período'), {
            'fields': ('centro', 'periodo')
        }),
        (_('Apuração e Comissão'), {
            'fields': ('total_bruto_inscricoes', 'percentual_comissao_plataforma', 'valor_comissao_plataforma', 'valor_liquido_centro')
        }),
        (_('Repasse & Transferência'), {
            'fields': ('pago', 'comprovativo_repasse', 'data_pagamento_repasse')
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.calcular_valores()
        super().save_model(request, obj, form, change)
