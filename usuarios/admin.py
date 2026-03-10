from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Configuração customizada para o modelo Usuario
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nome', 'tipo_usuario', 'is_staff', 'is_active')
    list_filter = ('tipo_usuario', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'tipo_usuario')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'data_criacao', 'data_atualizacao')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'tipo_usuario', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email', 'nome')
    ordering = ('email',)
    readonly_fields = ('data_criacao', 'data_atualizacao')
    filter_horizontal = ('groups', 'user_permissions',)


class EscolaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'get_email', 'ativo')
    search_fields = ('nome', 'codigo_escola', 'usuario__email')
    list_filter = ('tipo', 'ativo')
    readonly_fields = ('data_criacao',)

    def get_email(self, obj):
        return obj.usuario.email if obj.usuario else "N/A"
    get_email.short_description = 'E-mail'

class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_email', 'data_cadastro', 'ativo')
    search_fields = ('nome', 'usuario__email')
    list_filter = ('ativo',)
    readonly_fields = ('data_cadastro',)

    def get_email(self, obj):
        return obj.usuario.email if obj.usuario else "N/A"
    get_email.short_description = 'E-mail'


@admin.register(PerfilAluno)
class PerfilAlunoAdmin(admin.ModelAdmin):
    list_display = ['aluno', 'biografia']

# Registro dos modelos
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Escola, EscolaAdmin)
admin.site.register(Aluno, AlunoAdmin)
