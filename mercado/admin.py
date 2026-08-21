from django.contrib import admin, messages
from django.utils import timezone

from .models import CategoriaMercado, ItemPedidoMercado, LojaParceira, PedidoMercado, ProdutoMercado


class ItemPedidoMercadoInline(admin.TabularInline):
    model = ItemPedidoMercado
    extra = 0
    readonly_fields = ("produto", "titulo", "quantidade", "preco_unitario", "custo_unitario")
    can_delete = False


@admin.register(LojaParceira)
class LojaParceiraAdmin(admin.ModelAdmin):
    list_display = ("nome", "municipio", "verificada", "ativa", "atualizado_em")
    list_filter = ("verificada", "ativa", "municipio")
    search_fields = ("nome", "email_operacional", "telefone_operacional")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(CategoriaMercado)
class CategoriaMercadoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ordem", "ativa")
    list_editable = ("ordem", "ativa")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(ProdutoMercado)
class ProdutoMercadoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "loja", "categoria", "preco", "quantidade_disponivel", "status", "destaque", "atualizado_em")
    list_filter = ("status", "destaque", "categoria", "loja")
    search_fields = ("titulo", "resumo", "loja__nome")
    list_editable = ("status", "destaque")
    prepopulated_fields = {"slug": ("titulo",)}
    readonly_fields = ("disponibilidade_confirmada_em", "disponibilidade_confirmada_por", "criado_em", "atualizado_em")

    @admin.action(description="Confirmar a disponibilidade seleccionada agora")
    def confirmar_disponibilidade(self, request, queryset):
        for produto in queryset:
            produto.confirmar_disponibilidade(request.user)
        self.message_user(request, "Disponibilidade actualizada para os produtos seleccionados.", messages.SUCCESS)

    actions = ("confirmar_disponibilidade",)


@admin.register(PedidoMercado)
class PedidoMercadoAdmin(admin.ModelAdmin):
    list_display = ("referencia", "nome_comprador", "status", "total", "municipio", "criado_em")
    list_filter = ("status", "municipio", "provincia")
    search_fields = ("referencia", "nome_comprador", "email_comprador", "telefone_comprador")
    readonly_fields = (
        "referencia", "utilizador", "nome_comprador", "email_comprador", "telefone_comprador",
        "subtotal", "total", "referencia_pagamento", "codigo_entrega", "criado_em", "atualizado_em",
        "disponibilidade_confirmada_em", "pagamento_confirmado_em", "recolhido_em", "entregue_em",
    )
    inlines = (ItemPedidoMercadoInline,)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        pedido = form.instance
        pedido.recalcular_totais()
        pedido.save(update_fields=["subtotal", "total", "atualizado_em"])

    @admin.action(description="Confirmar disponibilidade e abrir pagamento")
    def confirmar_disponibilidade(self, request, queryset):
        pedidos = queryset.filter(status="A_VALIDAR")
        for pedido in pedidos:
            pedido.recalcular_totais()
            pedido.status = "AGUARDA_PAGAMENTO"
            pedido.disponibilidade_confirmada_em = timezone.now()
            pedido.save(update_fields=["subtotal", "total", "status", "disponibilidade_confirmada_em", "atualizado_em"])
        self.message_user(request, f"{pedidos.count()} pedido(s) pronto(s) para pagamento.", messages.SUCCESS)

    @admin.action(description="Marcar como recolhido e preparar entrega")
    def marcar_recolhido(self, request, queryset):
        pedidos = queryset.filter(status="PAGO_RECOLHA")
        pedidos.update(status="PREPARAR_ENTREGA", recolhido_em=timezone.now())
        self.message_user(request, f"{pedidos.count()} pedido(s) marcado(s) como recolhido(s).", messages.SUCCESS)

    @admin.action(description="Marcar como em entrega")
    def marcar_em_entrega(self, request, queryset):
        pedidos = queryset.filter(status="PREPARAR_ENTREGA")
        pedidos.update(status="EM_ENTREGA")
        self.message_user(request, f"{pedidos.count()} pedido(s) está/estão agora em entrega.", messages.SUCCESS)

    @admin.action(description="Confirmar entrega dos pedidos")
    def marcar_entregue(self, request, queryset):
        pedidos = queryset.filter(status="EM_ENTREGA")
        pedidos.update(status="ENTREGUE", entregue_em=timezone.now())
        self.message_user(request, f"{pedidos.count()} pedido(s) confirmado(s) como entregue(s).", messages.SUCCESS)

    actions = ("confirmar_disponibilidade", "marcar_recolhido", "marcar_em_entrega", "marcar_entregue")
