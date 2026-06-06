from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from .models import AvaliacaoHibridaCentro, FeedbackExterno, Comentario

@admin.register(AvaliacaoHibridaCentro)
class AvaliacaoHibridaCentroAdmin(UnfoldModelAdmin):
    list_display = ('centro', 'score_confianca', 'ultima_atualizacao')
    readonly_fields = ('score_confianca', 'ultima_atualizacao')

@admin.register(FeedbackExterno)
class FeedbackExternoAdmin(UnfoldModelAdmin):
    list_display = ('centro', 'aluno', 'data', 'moderado')
    list_filter = ('moderado', 'data')
    search_fields = ('centro__nome', 'aluno__nome', 'comentario')

@admin.register(Comentario)
class ComentarioAdmin(UnfoldModelAdmin):
    list_display = ('aluno', 'curso', 'avaliacao', 'status_aluno', 'data_comentario', 'aprovado')
    list_filter = ('aprovado', 'avaliacao', 'status_aluno', 'data_comentario')
    search_fields = ('aluno__nome', 'curso__nome', 'comentario')
    readonly_fields = ('data_comentario', 'atualizado_em')
    
    fieldsets = (
        (None, {
            'fields': ('aluno', 'curso', 'curso_video', 'comentario', 'avaliacao', 'status_aluno')
        }),
        ('Moderação', {
            'fields': ('aprovado', 'resposta', 'resposta_data')
        }),
        ('Datas', {
            'fields': ('data_comentario', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
