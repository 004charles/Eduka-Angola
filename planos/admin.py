from django.contrib import admin
from .models import Plano, AssinaturaMembro

@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco', 'limite_cursos', 'alcance_km', 'prioridade_busca', 'ativo')
    list_filter = ('ativo', 'selo_verificacao', 'destaque_home')
    search_fields = ('nome',)

@admin.register(AssinaturaMembro)
class AssinaturaMembroAdmin(admin.ModelAdmin):
    list_display = ('centro', 'plano', 'status', 'data_inicio', 'data_fim')
    list_filter = ('status', 'plano')
    search_fields = ('centro__nome', 'centro__email')
