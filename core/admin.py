from django.contrib import admin
from .models import Galeria
from django.contrib import admin
from .models import SobreNos

@admin.register(Galeria)
class GaleriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'link', 'criado_em')
    search_fields = ('titulo', 'usuario')


@admin.register(SobreNos)
class SobreNosAdmin(admin.ModelAdmin):
    list_display = ("titulo", "data_atualizacao")  # colunas que aparecem na listagem
    search_fields = ("titulo", "descricao", "missao", "visao", "valores")  # barra de pesquisa
    list_filter = ("data_atualizacao",)  # filtro lateral
