from django.contrib import admin
from .models import AvaliacaoHibridaCentro, FeedbackExterno, Comentario

@admin.register(AvaliacaoHibridaCentro)
class AvaliacaoHibridaCentroAdmin(admin.ModelAdmin):
    list_display = ('centro', 'score_confianca', 'ultima_atualizacao')
    readonly_fields = ('score_confianca', 'ultima_atualizacao')

@admin.register(FeedbackExterno)
class FeedbackExternoAdmin(admin.ModelAdmin):
    list_display = ('centro', 'aluno', 'data', 'moderado')
    list_filter = ('moderado', 'data')
    search_fields = ('centro__nome', 'aluno__nome', 'comentario')

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
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
