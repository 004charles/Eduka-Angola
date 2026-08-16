from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from .models import SobreNos, MensagemContato, Galeria, Publicidade, ClienteAPIKey, PerguntaFrequente

@admin.register(Galeria)
class GaleriaAdmin(UnfoldModelAdmin):
    list_display = ('usuario', 'link', 'criado_em')
    search_fields = ('titulo', 'usuario')


@admin.register(SobreNos)
class SobreNosAdmin(UnfoldModelAdmin):
    list_display = ("titulo", "data_atualizacao", "telefone", "email_contato")
    search_fields = ("titulo", "descricao", "missao", "visao", "valores")
    list_filter = ("data_atualizacao",)


@admin.register(MensagemContato)
class MensagemContatoAdmin(UnfoldModelAdmin):
    list_display = ('nome', 'email', 'assunto', 'lido', 'criado_em')
    list_filter = ('lido', 'criado_em')
    search_fields = ('nome', 'email', 'assunto', 'mensagem')
    readonly_fields = ('criado_em',)
    actions = ['marcar_como_lido']

    def marcar_como_lido(self, request, queryset):
        queryset.update(lido=True)
    marcar_como_lido.short_description = "Marcar mensagens selecionadas como lidas"

@admin.register(Publicidade)
class PublicidadeAdmin(UnfoldModelAdmin):
    list_display = ('titulo', 'ativo', 'data_criacao')
    list_filter = ('ativo',)
    search_fields = ('titulo', 'descricao')

@admin.register(ClienteAPIKey)
class ClienteAPIKeyAdmin(UnfoldModelAdmin):
    list_display = ('nome_cliente', 'chave', 'ativo', 'criado_em', 'ultimo_uso')
    list_filter = ('ativo', 'criado_em')
    search_fields = ('nome_cliente',)
    readonly_fields = ('chave', 'criado_em', 'ultimo_uso')


@admin.register(PerguntaFrequente)
class PerguntaFrequenteAdmin(UnfoldModelAdmin):
    list_display = ('pergunta', 'categoria', 'idioma', 'ordem', 'publicada', 'atualizado_em')
    list_filter = ('publicada', 'idioma', 'categoria')
    search_fields = ('pergunta', 'resposta', 'categoria')
    list_editable = ('ordem', 'publicada')
    ordering = ('idioma', 'categoria', 'ordem')
