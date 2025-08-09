from django.contrib import admin
from .models import Categoria, Tag, Post, Comentario
from django.utils.html import format_html

class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'status', 'publicado_em', 'visualizacoes')
    list_filter = ('status', 'categoria', 'tags', 'publicado_em')
    search_fields = ('titulo', 'conteudo')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'publicado_em'
    ordering = ('-publicado_em',)
    filter_horizontal = ('tags',)
    
    fieldsets = (
        (None, {
            'fields': ('titulo', 'slug', 'categoria', 'tags', 'status')
        }),
        ('Conteúdo', {
            'fields': ('imagem_capa', 'resumo', 'conteudo')
        }),
        ('Datas', {
            'fields': ('publicado_em',)
        }),
    )

class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'post', 'criado_em', 'aprovado')
    list_filter = ('aprovado', 'criado_em')
    search_fields = ('nome', 'email', 'mensagem')
    actions = ['aprovar_comentarios']

    def aprovar_comentarios(self, request, queryset):
        queryset.update(aprovado=True)
    aprovar_comentarios.short_description = "Aprovar comentários selecionados"


# Registre os outros modelos (remova a linha duplicada do Autor)
admin.site.register(Categoria)
admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
admin.site.register(Comentario, ComentarioAdmin)