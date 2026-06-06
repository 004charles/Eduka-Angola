from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from .models import AreaEstagio, Estagio, InscricaoEstagio, BeneficioEstagio

@admin.register(AreaEstagio)
class AreaEstagioAdmin(UnfoldModelAdmin):
    list_display = ['nome', 'ativa']
    list_filter = ['ativa']
    search_fields = ['nome']

class BeneficioEstagioInline(UnfoldTabularInline):
    model = BeneficioEstagio
    extra = 1

@admin.register(Estagio)
class EstagioAdmin(UnfoldModelAdmin):
    list_display = [
        'titulo', 
        'centro_formacao', 
        'area', 
        'tipo_remuneracao', 
        'vagas_disponiveis',
        'vagas_preenchidas',
        'data_inicio',
        'ativo',
        'destaque'
    ]
    list_filter = [
        'centro_formacao', 
        'area', 
        'tipo_remuneracao', 
        'modalidade',
        'ativo',
        'destaque',
        'data_publicacao'
    ]
    search_fields = ['titulo', 'centro_formacao__nome', 'descricao']
    readonly_fields = ['visualizacoes', 'data_publicacao']
    inlines = [BeneficioEstagioInline]
    prepopulated_fields = {'slug': ['titulo']}

@admin.register(InscricaoEstagio)
class InscricaoEstagioAdmin(UnfoldModelAdmin):
    list_display = [
        'aluno', 
        'estagio', 
        'status', 
        'data_inscricao',  # REMOVI 'data_entrevista' daqui
    ]
    list_filter = ['status', 'data_inscricao', 'estagio']
    search_fields = ['aluno__nome', 'aluno__email', 'estagio__titulo']
    readonly_fields = ['data_inscricao']