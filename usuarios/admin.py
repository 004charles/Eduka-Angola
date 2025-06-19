from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Configuração customizada para o modelo Usuario
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nome', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome',)}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'data_criacao', 'data_atualizacao')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'nome')
    ordering = ('email',)
    readonly_fields = ('data_criacao', 'data_atualizacao')

# Configurações para os outros modelos
class CentroDeFormacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nif', 'email', 'ativo')
    search_fields = ('nome', 'nif', 'email')
    list_filter = ('ativo',)
    readonly_fields = ('data_criacao',)

class EscolaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'email', 'ativo')
    search_fields = ('nome', 'codigo_escola', 'email')
    list_filter = ('tipo', 'ativo')
    readonly_fields = ('data_criacao',)

class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'data_cadastro', 'ativo')
    search_fields = ('nome', 'email')
    list_filter = ('ativo',)
    readonly_fields = ('data_cadastro',)

class BibliotecaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'email', 'ativo')
    search_fields = ('nome', 'email', 'codigo_registro')
    list_filter = ('tipo', 'ativo')

class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ramo_atuacao', 'email', 'numero_funcionarios')
    search_fields = ('nome', 'nif', 'email')
    list_filter = ('ramo_atuacao',)
    

@admin.register(PerfilCentroDeFormacao)
class PerfilCentroDeFormacaoAdmin(admin.ModelAdmin):
    list_display = ('centro', 'tipo', 'modalidade', 'destaque', 'dono')
    search_fields = ('centro__nome', 'tipo', 'dono')
    list_filter = ('modalidade', 'destaque')

    fields = (
        'centro', 'dono', 'imagem', 'banner', 'video_apresentacao',  # campo de vídeo adicionado aqui
        'descricao', 'tipo', 'modalidade', 
        'facebook', 'instagram', 'whatsapp', 
        'destaque', 'slug'
    )



class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 1  # Número de campos em branco para adicionar um novo comentário


@admin.register(PerfilAluno)
class PerfilAlunoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'biografia']

admin.site.register(Comentario)
# Registro dos modelos
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(CentroDeFormacao, CentroDeFormacaoAdmin)
admin.site.register(Escola, EscolaAdmin)
admin.site.register(Aluno, AlunoAdmin)
admin.site.register(Biblioteca, BibliotecaAdmin)
admin.site.register(Empresa, EmpresaAdmin)
