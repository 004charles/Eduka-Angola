from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from .models import Plano, AssinaturaMembro, VoucherPlano

@admin.register(Plano)
class PlanoAdmin(UnfoldModelAdmin):
    list_display = ('nome', 'preco', 'limite_cursos', 'alcance_km', 'prioridade_busca', 'ativo')
    list_filter = ('ativo', 'selo_verificacao', 'destaque_home')
    search_fields = ('nome',)

@admin.register(AssinaturaMembro)
class AssinaturaMembroAdmin(UnfoldModelAdmin):
    list_display = ('centro', 'plano', 'status', 'data_inicio', 'data_fim', 'renovacao_automatica')
    list_filter = ('status', 'plano', 'renovacao_automatica')
    search_fields = ('centro__nome', 'centro__email')


@admin.register(VoucherPlano)
class VoucherPlanoAdmin(UnfoldModelAdmin):
    list_display = ('codigo', 'plano', 'centro', 'usado', 'data_criacao')
    list_filter = ('usado', 'plano')
    search_fields = ('codigo', 'centro__nome', 'centro__email')
