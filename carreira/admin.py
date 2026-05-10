from django.contrib import admin
from .models import Skill, Empresa, Vaga, CandidaturaVaga

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'nivel_demanda')
    list_filter = ('categoria', 'nivel_demanda')
    search_fields = ('nome', 'descricao')
    prepopulated_fields = {'slug': ('nome',)}
    filter_horizontal = ('cursos_relacionados',)

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'setor', 'nif', 'ativa')
    list_filter = ('ativa', 'setor')
    search_fields = ('nome', 'nif', 'descricao')

class CandidaturaInline(admin.TabularInline):
    model = CandidaturaVaga
    extra = 0
    readonly_fields = ('data_candidatura',)

@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empresa', 'localizacao', 'tipo', 'status', 'data_publicacao')
    list_filter = ('status', 'tipo', 'destaque', 'data_publicacao')
    search_fields = ('titulo', 'empresa__nome', 'descricao')
    prepopulated_fields = {'slug': ('titulo', 'empresa')}
    filter_horizontal = ('competencias_exigidas',)
    inlines = [CandidaturaInline]

@admin.register(CandidaturaVaga)
class CandidaturaVagaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'vaga', 'data_candidatura', 'status')
    list_filter = ('status', 'data_candidatura')
    search_fields = ('aluno__nome', 'vaga__titulo')
