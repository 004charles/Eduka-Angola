from django.contrib import admin
from .models import Patrocinador, Bolsa, CandidaturaBolsa

@admin.register(Patrocinador)
class PatrocinadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'ativo', 'data_parceria')
    list_filter = ('tipo', 'ativo')
    search_fields = ('nome', 'descricao')

@admin.register(Bolsa)
class BolsaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'patrocinador', 'curso', 'porcentagem', 'status')
    list_filter = ('status', 'patrocinador')
    search_fields = ('aluno__nome', 'aluno__usuario__email', 'curso__titulo')

@admin.register(CandidaturaBolsa)
class CandidaturaBolsaAdmin(admin.ModelAdmin):
    list_display = ('aluno', 'curso_pretendido', 'status', 'data_candidatura')
    list_filter = ('status',)
    search_fields = ('aluno__nome', 'curso_pretendido__titulo')
    readonly_fields = ('data_candidatura',)
    actions = ['aprovar_candidaturas', 'rejeitar_candidaturas']

    def aprovar_candidaturas(self, request, queryset):
        queryset.update(status='APROVADO')
    aprovar_candidaturas.short_description = "Aprovar candidaturas selecionadas"

    def rejeitar_candidaturas(self, request, queryset):
        queryset.update(status='REJEITADO')
    rejeitar_candidaturas.short_description = "Rejeitar candidaturas selecionadas"
