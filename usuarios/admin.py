from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from django.contrib.auth.admin import UserAdmin
from .models import *
from cursos_app.models import Instrutor

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


class AlunoAdmin(UnfoldModelAdmin):
    list_display = ('nome', 'get_email', 'data_cadastro', 'ativo')
    search_fields = ('nome', 'usuario__email')
    list_filter = ('ativo',)
    readonly_fields = ('data_cadastro',)

    def get_email(self, obj):
        return obj.usuario.email if obj.usuario else "N/A"
    get_email.short_description = 'E-mail'


@admin.register(PerfilAluno)
class PerfilAlunoAdmin(UnfoldModelAdmin):
    list_display = ['aluno', 'biografia']

# Registro dos modelos
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Aluno, AlunoAdmin)

@admin.register(PreferenciaNotificacaoAluno)
class PreferenciaNotificacaoAlunoAdmin(UnfoldModelAdmin):
    list_display = ('aluno', 'receber_na_plataforma', 'receber_por_email', 'receber_push', 'resumo_semanal', 'atualizado_em')
    list_filter = ('receber_na_plataforma', 'receber_por_email', 'receber_push', 'resumo_semanal')
    search_fields = ('aluno__nome', 'aluno__usuario__email')
    readonly_fields = ('atualizado_em',)


@admin.register(SubscricaoWebPush)
class SubscricaoWebPushAdmin(UnfoldModelAdmin):
    list_display = ('aluno', 'ativa', 'criada_em', 'ultimo_envio_em', 'falhas_consecutivas')
    list_filter = ('ativa',)
    search_fields = ('aluno__nome', 'aluno__usuario__email', 'endpoint')
    readonly_fields = ('criada_em', 'atualizada_em', 'ultimo_envio_em', 'ultima_falha_em', 'falhas_consecutivas', 'endpoint', 'chave_p256dh', 'chave_auth', 'agente')


@admin.register(CandidaturaFormador)
class CandidaturaFormadorAdmin(UnfoldModelAdmin):
    list_display = ('aluno', 'titulo_profissional', 'area_especializacao', 'pontuacao_teste', 'estado', 'criado_em')
    list_filter = ('estado', 'area_especializacao', 'teste_aprovado')
    search_fields = ('aluno__nome', 'aluno__usuario__email', 'titulo_profissional')
    readonly_fields = ('codigo_confirmado_em', 'pontuacao_teste', 'teste_aprovado', 'criado_em', 'atualizado_em')
    actions = ('aprovar_candidaturas',)

    @admin.action(description='Aprovar candidaturas seleccionadas e activar permissão de formador')
    def aprovar_candidaturas(self, request, queryset):
        aprovadas = 0
        for candidatura in queryset.filter(estado='PENDENTE_ANALISE', teste_aprovado=True).select_related('aluno__usuario'):
            instrutor, _ = Instrutor.objects.update_or_create(
                usuario=candidatura.aluno.usuario,
                defaults={
                    'nome': candidatura.aluno.nome,
                    'email': candidatura.aluno.usuario.email,
                    'titulo': candidatura.titulo_profissional,
                    'biografia': candidatura.biografia,
                    'area_especializacao': candidatura.area_especializacao,
                    'ativo': True,
                },
            )
            candidatura.estado = 'APROVADA'
            candidatura.save(update_fields=['estado', 'atualizado_em'])
            aprovadas += 1
        self.message_user(request, f'{aprovadas} candidatura(s) aprovada(s). A conta continua a ser de aluno e recebeu o perfil de formador.')
