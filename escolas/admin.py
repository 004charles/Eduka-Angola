from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from .models import CategoriaEscola, Escola, PerfilEscola, CursoEnsinoMedio, GaleriaEscola, AreaFormacao, Infraestrutura, ParceriaEscola, RepresentanteEscola

@admin.register(CategoriaEscola)
class CategoriaEscolaAdmin(UnfoldModelAdmin):
    list_display = ('nome', 'ativa')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)

class PerfilEscolaInline(UnfoldStackedInline):
    model = PerfilEscola
    can_delete = False

class CursoEnsinoMedioInline(UnfoldTabularInline):
    model = CursoEnsinoMedio
    extra = 1

class GaleriaEscolaInline(UnfoldTabularInline):
    model = GaleriaEscola
    extra = 1

class ParceriaEscolaInline(UnfoldTabularInline):
    model = ParceriaEscola
    extra = 1

@admin.register(Escola)
class EscolaAdmin(UnfoldModelAdmin):
    list_display = ('nome', 'tipo_rede', 'provincia', 'municipio', 'ativa')
    list_filter = ('tipo_rede', 'provincia', 'ativa')
    search_fields = ('nome', 'municipio')
    inlines = [PerfilEscolaInline, CursoEnsinoMedioInline, GaleriaEscolaInline, ParceriaEscolaInline]

@admin.register(RepresentanteEscola)
class RepresentanteEscolaAdmin(UnfoldModelAdmin):
    list_display = ('user', 'escola', 'cargo', 'ativo', 'data_associacao')
    list_filter = ('cargo', 'ativo')
    search_fields = ('user__username', 'user__email', 'escola__nome')

@admin.register(AreaFormacao)
class AreaFormacaoAdmin(UnfoldModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Infraestrutura)
class InfraestruturaAdmin(UnfoldModelAdmin):
    list_display = ('nome', 'icone')
    search_fields = ('nome',)
