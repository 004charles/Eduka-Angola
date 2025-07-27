from django.contrib import admin
from .models import *

# Configurações para os outros modelos
class CentroDeFormacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nif', 'email', 'ativo')
    search_fields = ('nome', 'nif', 'email')
    list_filter = ('ativo',)
    readonly_fields = ('data_criacao',)


@admin.register(PerfilCentroDeFormacao)
class PerfilCentroDeFormacaoAdmin(admin.ModelAdmin):
    list_display = ('centro', 'tipo', 'modalidade', 'destaque', 'dono')
    search_fields = ('centro__nome', 'tipo', 'dono')
    list_filter = ('modalidade', 'destaque')

    fields = (
        'centro', 'dono', 'imagem', 'banner', 'video_apresentacao',  # campo de vídeo adicionado aqui
        'descricao', 'tipo', 'modalidade', 
        'facebook', 'instagram', 'whatsapp', 
        'destaque', 'slug'
    )



admin.site.register(CentroDeFormacao, CentroDeFormacaoAdmin)
