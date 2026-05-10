from django.contrib import admin
from .models import CategoriaEscola, Escola, PerfilEscola, CursoEnsinoMedio, GaleriaEscola, AreaFormacao

@admin.register(CategoriaEscola)
class CategoriaEscolaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativa')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome',)

class PerfilEscolaInline(admin.StackedInline):
    model = PerfilEscola
    can_delete = False

class CursoEnsinoMedioInline(admin.TabularInline):
    model = CursoEnsinoMedio
    extra = 1

class GaleriaEscolaInline(admin.TabularInline):
    model = GaleriaEscola
    extra = 1

@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo_rede', 'provincia', 'municipio', 'ativa')
    list_filter = ('tipo_rede', 'provincia', 'ativa')
    search_fields = ('nome', 'municipio')
    inlines = [PerfilEscolaInline, CursoEnsinoMedioInline, GaleriaEscolaInline]

@admin.register(AreaFormacao)
class AreaFormacaoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
