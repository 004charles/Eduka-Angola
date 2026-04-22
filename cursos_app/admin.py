from django.contrib import admin
from .models import *

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug')
    search_fields = ('nome',)
    prepopulated_fields = {'slug': ('nome',)}

class InstrutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'area_especializacao', 'ativo')
    search_fields = ('nome', 'email')
    list_filter = ('area_especializacao', 'ativo')
    readonly_fields = ('data_cadastro',)
    fieldsets = (
        (None, {
            'fields': ('centro_de_formacao', 'nome', 'email', 'area_especializacao', 'biografia', 'foto', 'ativo')
        }),
        ('Informações Adicionais (Antigo Perfil)', {
            'classes': ('collapse',),
            'fields': ('foto_capa', 'facebook', 'twitter', 'instagram', 'linkedin', 'total_alunos', 'total_cursos', 'total_avaliacoes', 'nota_media')
        }),
        ('Datas', {
            'fields': ('data_cadastro',),
        }),
    )


class PreRequisitoCursoInline(admin.TabularInline):
    model = PreRequisitoCurso
    extra = 3

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    # ... (restante configurado abaixo)
    inlines = [PreRequisitoCursoInline]
    list_display = [
        'titulo', 
        'centro', 
        'categoria', 
        'nivel', 
        'data_criacao',
        'publicado', 
        'ativo', 
        'destaque'
    ]
    list_filter = ['centro', 'categoria', 'nivel', 'publicado', 'ativo', 'destaque']
    search_fields = ['titulo', 'descricao', 'descricao_curta']
    filter_horizontal = ['instrutores']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('centro', 'titulo', 'descricao', 'descricao_curta', 'categoria', 'imagem', 'video_preview_file', 'video_previa_url')
        }),
        ('Configurações do Curso', {
            'fields': ('nivel', 'idioma', 'modalidade', 'carga_horaria', 'certificado')
        }),
        ('Preços', {
            'fields': ('preco', 'preco_inscricao', 'preco_promocional')
        }),
        ('Datas', {
            'fields': ('data_inicio', 'data_inicio_promocao', 'data_fim_promocao')
        }),
        ('Status', {
            'fields': ('publicado', 'ativo', 'destaque')
        }),
        ('Instrutores', {
            'fields': ('instrutores',)
        }),
    )

admin.site.register(Instrutor, InstrutorAdmin)
admin.site.register(Inscricao)
admin.site.register(PreRequisitoCurso)

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'curso', 'data_inicio', 'data_fim', 'vagas_ocupadas', 'vagas_totais', 'status')
    list_filter = ('status', 'curso', 'turno')
    search_fields = ('nome', 'curso__titulo')
