from django import forms
from django.contrib import admin

from .models import Bilhete, EventoMarketplace, LoteBilhete, OrganizadorEvento, PedidoBilhete


class LoteBilheteAdminForm(forms.ModelForm):
    class Meta:
        model = LoteBilhete
        fields = "__all__"
        widgets = {
            "cor_primaria": forms.TextInput(attrs={"type": "color", "title": "Escolher azul principal do bilhete"}),
            "cor_secundaria": forms.TextInput(attrs={"type": "color", "title": "Escolher fundo azul claro do bilhete"}),
        }


class LoteBilheteInline(admin.TabularInline):
    model = LoteBilhete
    form = LoteBilheteAdminForm
    extra = 0
    fields = ("nome", "descricao", "texto_ingresso", "beneficios", "regras", "cor_primaria", "cor_secundaria", "imagem_ingresso", "preco", "moeda", "quantidade_total", "quantidade_vendida", "inicio_vendas", "fim_vendas", "activo", "ordem")


@admin.register(OrganizadorEvento)
class OrganizadorEventoAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "email", "verificado", "ativo", "criado_em")
    list_filter = ("tipo", "verificado", "ativo")
    search_fields = ("nome", "email", "slug")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(EventoMarketplace)
class EventoMarketplaceAdmin(admin.ModelAdmin):
    list_display = ("titulo", "organizador", "data_inicio", "status", "destaque", "comissao_percentual")
    list_filter = ("status", "modalidade", "categoria", "destaque")
    search_fields = ("titulo", "slug", "organizador__nome", "cidade", "provincia")
    prepopulated_fields = {"slug": ("titulo",)}
    date_hierarchy = "data_inicio"
    inlines = (LoteBilheteInline,)
    fieldsets = (
        ("Publicação", {"fields": ("organizador", "titulo", "slug", "resumo", "descricao", "imagem_capa", "categoria", "status", "destaque")}),
        ("Agenda e local", {"fields": ("modalidade", "data_inicio", "data_fim", "local", "cidade", "provincia", "url_online")}),
        ("Financeiro", {"fields": ("comissao_percentual",)}),
    )


@admin.register(LoteBilhete)
class LoteBilheteAdmin(admin.ModelAdmin):
    form = LoteBilheteAdminForm
    list_display = ("nome", "evento", "preco", "quantidade_total", "quantidade_vendida", "lugares_disponiveis", "cor_primaria", "activo")
    list_filter = ("activo", "moeda", "evento__status")
    search_fields = ("nome", "evento__titulo")
    autocomplete_fields = ("evento",)
    readonly_fields = ("lugares_disponiveis",)


@admin.register(PedidoBilhete)
class PedidoBilheteAdmin(admin.ModelAdmin):
    list_display = ("referencia", "evento", "nome_comprador", "quantidade", "valor_bruto", "valor_comissao", "valor_organizador", "status", "criado_em")
    list_filter = ("status", "evento", "criado_em")
    search_fields = ("referencia", "nome_comprador", "email_comprador", "referencia_pagamento")
    autocomplete_fields = ("evento", "lote", "utilizador")
    readonly_fields = ("referencia", "valor_bruto", "valor_comissao", "valor_organizador", "referencia_pagamento", "criado_em", "pago_em")


@admin.register(Bilhete)
class BilheteAdmin(admin.ModelAdmin):
    list_display = ("codigo", "evento_relacionado", "nome_participante", "email_participante", "status", "emitido_em", "utilizado_em")
    list_filter = ("status", "lote__evento", "emitido_em")

    @admin.display(description="Evento", ordering="pedido__evento__titulo")
    def evento_relacionado(self, obj):
        return obj.pedido.evento
    search_fields = ("codigo", "nome_participante", "email_participante", "pedido__referencia", "pedido__evento__titulo")
    autocomplete_fields = ("pedido", "lote")
    readonly_fields = ("codigo", "emitido_em", "utilizado_em")
