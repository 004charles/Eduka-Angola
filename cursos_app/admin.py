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

class ModuloInline(admin.TabularInline):
    model = Modulo
    extra = 1

class VideoInline(admin.TabularInline):
    model = Video
    extra = 1
    fields = ('titulo', 'url', 'arquivo', 'ordem', 'liberado')
    readonly_fields = ('duracao',)

class MaterialApoioInline(admin.TabularInline):
    model = MaterialApoio
    extra = 1
    fields = ('titulo', 'arquivo', 'tipo', 'disponivel')

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
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
            'fields': ('centro', 'titulo', 'descricao', 'descricao_curta', 'categoria', 'imagem')
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

class ModuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'ordem')
    list_filter = ('curso',)
    inlines = [VideoInline]
    ordering = ('curso', 'ordem')

class VideoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'ordem', 'liberado')
    list_filter = ('modulo__curso', 'liberado')
    search_fields = ('titulo', 'descricao')
    readonly_fields = ('duracao',)

class MaterialApoioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'tipo', 'disponivel', 'data_adicao')
    list_filter = ('tipo', 'disponivel', 'curso')
    search_fields = ('titulo',)
    readonly_fields = ('data_adicao',)

class PerfilInstrutorInline(admin.StackedInline):
    model = PerfilInstrutor
    can_delete = False
    verbose_name_plural = 'Perfil do Instrutor'

admin.site.register(Instrutor, InstrutorAdmin)
admin.site.register(Modulo, ModuloAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(MaterialApoio, MaterialApoioAdmin)
admin.site.register(Inscricao)
admin.site.register(PerfilInstrutor)
