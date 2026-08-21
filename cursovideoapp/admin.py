from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Curso_video, Aula, Exercicio, Questao, Alternativa, TurmaVideo, PlanoSubscricaoVideo, AssinaturaVideoAluno, AvisoExpiracaoSubscricaoVideo
# from inteligencia.ai_utils import gerar_exercicios_ia
from django.contrib.auth.models import Group

class AulaInline(UnfoldTabularInline):
    model = Aula
    extra = 1

@admin.register(Curso_video)
class Curso_videoAdmin(UnfoldModelAdmin):
    list_display = ('titulo', 'instrutor', 'categoria', 'data_publicacao', 'import_playlist_link')
    search_fields = ('titulo', 'descricao')
    list_filter = ('categoria', 'instrutor')
    inlines = [AulaInline]

    def import_playlist_link(self, obj):
        return format_html(
            '<a class="button" href="/curso_video/curso/{}/importar-playlist-admin/" style="background: #d9534f; color: white;">Importar Playlist</a>',
            obj.id
        )
    import_playlist_link.short_description = "Ação YouTube"


@admin.register(PlanoSubscricaoVideo)
class PlanoSubscricaoVideoAdmin(UnfoldModelAdmin):
    list_display = ('nome', 'preco', 'moeda', 'periodo_dias', 'ativo', 'destaque', 'ordem')
    list_filter = ('ativo', 'destaque', 'moeda')
    search_fields = ('nome', 'descricao')
    list_editable = ('preco', 'periodo_dias', 'ativo', 'destaque', 'ordem')


@admin.register(AssinaturaVideoAluno)
class AssinaturaVideoAlunoAdmin(UnfoldModelAdmin):
    list_display = ('aluno', 'plano', 'status', 'data_inicio', 'data_fim', 'valor_cobrado', 'referencia_pagamento')
    list_filter = ('status', 'plano', 'moeda')
    search_fields = ('aluno__nome', 'aluno__usuario__email', 'referencia_pagamento')
    readonly_fields = ('referencia_pagamento', 'data_criacao', 'data_atualizacao')


@admin.register(AvisoExpiracaoSubscricaoVideo)
class AvisoExpiracaoSubscricaoVideoAdmin(UnfoldModelAdmin):
    list_display = ('assinatura', 'antecedencia_horas', 'notificacao', 'email_processado_em', 'criado_em')
    list_filter = ('antecedencia_horas', 'email_processado_em')
    search_fields = ('assinatura__aluno__nome', 'assinatura__aluno__usuario__email', 'assinatura__plano__nome')
    readonly_fields = ('assinatura', 'antecedencia_horas', 'notificacao', 'email_processado_em', 'criado_em', 'atualizado_em')

@admin.register(Aula)
class AulaAdmin(UnfoldModelAdmin):
    list_display = ('ordem', 'titulo', 'curso', 'duracao_formatada', 'tem_exercicio')
    list_filter = ('curso',)
    search_fields = ('titulo',)
    actions = ['gerar_exercicios_ia_action']

    def tem_exercicio(self, obj):
        return hasattr(obj, 'exercicio')
    tem_exercicio.boolean = True
    tem_exercicio.short_description = "Exercício?"

    @admin.action(description="Gerar Exercícios com Eduka AI")
    def gerar_exercicios_ia_action(self, request, queryset):
        for aula in queryset:
            if hasattr(aula, 'exercicio'):
                continue # Evitar sobrescrever se já existir
            
            data = gerar_exercicios_ia(aula.titulo, aula.descricao or "")
            if "error" in data:
                self.message_user(request, f"Erro na aula {aula.titulo}: {data['error']}", level='error')
                continue
            
            exercicio = Exercicio.objects.create(aula=aula)
            for q_data in data.get('questoes', []):
                questao = Questao.objects.create(
                    exercicio=exercicio,
                    texto=q_data['texto'],
                    explicacao=q_data.get('explicacao', '')
                )
                for a_data in q_data.get('alternativas', []):
                    Alternativa.objects.create(
                        questao=questao,
                        texto=a_data['texto'],
                        is_correta=a_data['correta']
                    )
        self.message_user(request, "Processamento concluído.")


@admin.register(TurmaVideo)
class TurmaVideoAdmin(UnfoldModelAdmin):
    list_display = ('nome', 'curso', 'data_inicio', 'turno', 'vagas_disponiveis', 'status')
    list_filter = ('status', 'turno', 'curso__centro')
    search_fields = ('nome', 'codigo', 'curso__titulo')

class AlternativaInline(UnfoldTabularInline):
    model = Alternativa
    extra = 4

@admin.register(Questao)
class QuestaoAdmin(UnfoldModelAdmin):
    list_display = ('texto', 'exercicio')
    inlines = [AlternativaInline]

class QuestaoInline(UnfoldStackedInline):
    model = Questao
    extra = 1

@admin.register(Exercicio)
class ExercicioAdmin(UnfoldModelAdmin):
    list_display = ('aula', 'data_criacao')
    inlines = [QuestaoInline]

admin.site.site_header = "Edukangola"
admin.site.site_title = "Edukangola Administração"
admin.site.index_title = "Administração do Site"
admin.site.unregister(Group)
