from django.contrib import admin
from .models import SobreNos, MensagemContato, Galeria, Publicidade

@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'link', 'criado_em')
    search_fields = ('titulo', 'usuario')


@admin.register(SobreNos)
class SobreNosAdmin(admin.ModelAdmin):
    list_display = ("titulo", "data_atualizacao", "telefone", "email_contato")
    search_fields = ("titulo", "descricao", "missao", "visao", "valores")
    list_filter = ("data_atualizacao",)


@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'assunto', 'lido', 'criado_em')
    list_filter = ('lido', 'criado_em')
    search_fields = ('nome', 'email', 'assunto', 'mensagem')
    readonly_fields = ('criado_em',)
    actions = ['marcar_como_lido']

    def marcar_como_lido(self, request, queryset):
        queryset.update(lido=True)
    marcar_como_lido.short_description = "Marcar mensagens selecionadas como lidas"

@admin.register(Publicidade)
class PublicidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ativo', 'data_criacao')
    list_filter = ('ativo',)
    search_fields = ('titulo', 'descricao')
