from django.contrib import admin
from .models import InstrutorProxy
from django.utils.translation import gettext_lazy as _

@admin.register(InstrutorProxy)
class InstrutorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'area_especializacao', 'get_status_usuario', 'data_cadastro')
    list_filter = ('area_especializacao', 'ativo')
    search_fields = ('nome', 'email')
    readonly_fields = ('data_cadastro', 'get_status_usuario')
    actions = ['ativar_instrutores', 'desativar_instrutores']

    fieldsets = (
        ('Status de Segurança', {
            'fields': ('get_status_usuario', 'usuario', 'ativo'),
            'description': 'Verifique aqui se o instrutor já tem permissão para entrar na plataforma.'
        }),
        ('Informações Pessoais', {
            'fields': ('nome', 'email', 'biografia', 'foto', 'area_especializacao', 'data_cadastro')
        }),
        ('Redes Sociais e Métricas', {
            'classes': ('collapse',),
            'fields': ('foto_capa', 'facebook', 'twitter', 'instagram', 'linkedin', 'total_alunos', 'total_cursos', 'total_avaliacoes', 'nota_media')
        }),
    )

    def get_status_usuario(self, obj):
        if obj.usuario:
            return "✅ ATIVO (Pode fazer login)" if obj.usuario.is_active else "⏳ PENDENTE (Acesso bloqueado)"
        return "❌ Sem conta de usuário vinculada"
    get_status_usuario.short_description = "Status de Acesso do Instrutor"

    @admin.action(description="Ativar acesso dos instrutores selecionados")
    def ativar_instrutores(self, request, queryset):
        for obj in queryset:
            if obj.usuario:
                obj.usuario.is_active = True
                obj.usuario.save()
        self.message_user(request, "Os instrutores selecionados foram ativados com sucesso.")

    @admin.action(description="Desativar acesso dos instrutores selecionados")
    def desativar_instrutores(self, request, queryset):
        for obj in queryset:
            if obj.usuario:
                obj.usuario.is_active = False
                obj.usuario.save()
        self.message_user(request, "Os instrutores selecionados foram desativados.")
