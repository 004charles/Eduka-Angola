from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline as UnfoldTabularInline
from unfold.admin import StackedInline as UnfoldStackedInline
from django.contrib.auth.hashers import make_password
from django.utils.html import format_html
from .models import *

# ========== FILTROS PERSONALIZADOS ==========
class CentroAtivoFilter(admin.SimpleListFilter):
    title = 'Status do Centro'
    parameter_name = 'ativo'
    
    def lookups(self, request, model_admin):
        return (
            ('ativos', 'Centros Ativos'),
            ('inativos', 'Centros Inativos'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'ativos':
            return queryset.filter(ativo=True)
        if self.value() == 'inativos':
            return queryset.filter(ativo=False)

class DestaqueFilter(admin.SimpleListFilter):
    title = 'Status de Destaque'
    parameter_name = 'destaque'
    
    def lookups(self, request, model_admin):
        return (
            ('destaque', 'Em Destaque'),
            ('normal', 'Normal'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'destaque':
            return queryset.filter(destaque=True)
        if self.value() == 'normal':
            return queryset.filter(destaque=False)

# ========== ACTION PERSONALIZADAS ==========
def ativar_centros(modeladmin, request, queryset):
    queryset.update(ativo=True)
ativar_centros.short_description = "Ativar centros selecionados"

def desativar_centros(modeladmin, request, queryset):
    queryset.update(ativo=False)
desativar_centros.short_description = "Desativar centros selecionados"

def marcar_como_destaque(modeladmin, request, queryset):
    queryset.update(destaque=True)
marcar_como_destaque.short_description = "Marcar como destaque"

def aprovar_depoimentos(modeladmin, request, queryset):
    queryset.update(aprovado=True)
aprovar_depoimentos.short_description = "Aprovar depoimentos selecionados"

def enviar_convite_centro(modeladmin, request, queryset):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.conf import settings
    from .models import ConviteCentro
    from core.email_utils import enviar_email_brevo
    import uuid

    invites_sent = 0
    for centro in queryset:
        convite, created = ConviteCentro.objects.get_or_create(centro=centro)
        # Se já foi usado, não reenviar (opcional, ou gerar novo token se quiser forçar)
        if convite.usado:
            continue
            
        site_domain = getattr(settings, 'SITE_DOMAIN', 'http://127.0.0.1:8000')
        link = f"{site_domain}/gestoreduka/cadastro/confirmar/{convite.token}/"
        
        subject = 'Convite para EdukAngola - Complete seu Registro'
        try:
            html_content = render_to_string('emails/convite_centro.html', {
                'link_convite': link,
                'email_centro': centro.email
            })
            text_content = strip_tags(html_content)
            
            sucesso = enviar_email_brevo(
                to_email=centro.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
            if sucesso:
                invites_sent += 1
            else:
                modeladmin.message_user(request, f"Erro ao enviar para {centro.email}: falha na API do Brevo. Verifique os logs.", level='error')
        except Exception as e:
            modeladmin.message_user(request, f"Erro ao enviar para {centro.email}: {str(e)}", level='error')
    
    if invites_sent > 0:
        modeladmin.message_user(request, f"{invites_sent} convites enviados com sucesso.")

enviar_convite_centro.short_description = "Enviar convite de registro por e-mail"

# ========== INLINES ==========
class CertificacaoInline(UnfoldTabularInline):
    model = Certificacao
    extra = 1
    fields = ['nome', 'orgao_emissor', 'logo_preview']
    readonly_fields = ['logo_preview']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'Preview'

class DiferencialInline(UnfoldTabularInline):
    model = Diferencial
    extra = 1

class AreaFormacaoInline(UnfoldTabularInline):
    model = AreaFormacao
    extra = 1

class EquipeInline(UnfoldTabularInline):
    model = Equipe
    extra = 1
    fields = ['nome', 'cargo', 'foto_preview']
    readonly_fields = ['foto_preview']
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.foto.url)
        return "-"
    foto_preview.short_description = 'Foto'

class RecursoInline(UnfoldTabularInline):
    model = Recurso
    extra = 1

class DepoimentoInline(UnfoldTabularInline):
    model = Depoimento
    extra = 0
    fields = ['nome', 'nota', 'aprovado']
    readonly_fields = ['data']

class EstatisticaInline(UnfoldTabularInline):
    model = Estatistica
    extra = 1

class ParceriaInline(UnfoldTabularInline):
    model = Parceria
    extra = 1
    fields = ['nome_empresa', 'logo_preview', 'ativa']
    readonly_fields = ['logo_preview']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'Logo'

class EventoInline(UnfoldTabularInline):
    model = Evento
    extra = 1
    fields = ['titulo', 'tipo', 'data_inicio', 'destaque']

class GaleriaImagemInline(UnfoldTabularInline):
    model = GaleriaImagem
    extra = 1
    fields = ['titulo', 'imagem_preview']
    readonly_fields = ['imagem_preview']
    
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.imagem.url)
        return "-"
    imagem_preview.short_description = 'Preview'

class ReelCentroInline(UnfoldTabularInline):
    model = ReelCentro
    extra = 0
    fields = ['titulo', 'video', 'visualizacoes', 'curtidas']
    readonly_fields = ['visualizacoes', 'curtidas']

class FilialInline(UnfoldTabularInline):
    model = Filial
    extra = 1

# ========== MODEL ADMINS ==========
@admin.register(CentroDeFormacao)
class CentroDeFormacaoAdmin(UnfoldModelAdmin):
    """
    Configuração do painel administrativo para os Centros de Formação.
    """
    list_display = [
        'nome', 
        'email', 
        'telefone', 
        'ativo_display', 
        'data_criacao_formatada',
        'total_cursos_display'
    ]
    list_filter = [CentroAtivoFilter, 'data_criacao']
    search_fields = ['nome', 'email', 'nif', 'telefone']
    readonly_fields = ['data_criacao', 'senha_hash_display']
    actions = [ativar_centros, desativar_centros, enviar_convite_centro]
    
    def get_fields(self, request, obj=None):
        if obj is None:  # Formulário de Adição
            return ['email']
        return ['nome', 'nif', 'email', 'telefone', 'endereco', 'site', 'ativo', 'data_criacao']

    fieldsets = (
        ('Informações do Convite', {
            'fields': ('email',)
        }),
        ('Dados Institucionais (Preenchidos pelo Centro)', {
            'fields': ('nome', 'nif', 'telefone', 'endereco', 'site', 'ativo'),
            'classes': ('collapse',)
        }),
        ('Segurança e Sistema', {
            'fields': ('senha_hash_display', 'data_criacao'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = []
    
    def ativo_display(self, obj):
        return format_html(
            '<span style="color: {};">●</span> {}',
            'green' if obj.ativo else 'red',
            'Ativo' if obj.ativo else 'Inativo'
        )
    ativo_display.short_description = 'Status'
    
    def data_criacao_formatada(self, obj):
        return obj.data_criacao.strftime('%d/%m/%Y %H:%M')
    data_criacao_formatada.short_description = 'Data de Criação'
    
    def senha_hash_display(self, obj):
        if obj.senha_hash:
            return "Senha definida (hash seguro)"
        return "Senha não definida"
    senha_hash_display.short_description = 'Status da Senha'
    
    def total_cursos_display(self, obj):
        # Assumindo que você tem um model Curso relacionado
        return "0"  # Substituir por obj.cursos.count() quando tiver o model Curso
    total_cursos_display.short_description = 'Total Cursos'

@admin.register(PerfilCentroDeFormacao)
class PerfilCentroDeFormacaoAdmin(UnfoldModelAdmin):
    """
    Gerenciamento detalhado do perfil institucional e branding do Centro.
    """
    list_display = [
        'centro_nome',
        'tipo',
        'modalidade',
        'destaque',  # ADICIONADO
        'verificado',  # ADICIONADO
        'total_seguidores',
        'total_visualizacoes'
    ]
    list_filter = ['tipo', 'modalidade', DestaqueFilter, 'verificado']
    search_fields = ['centro__nome', 'centro__email', 'dono']
    list_editable = ['destaque', 'verificado']  

    fieldsets = (
        ('Identificação', {
            'fields': ('centro', 'dono')
        }),
        ('Imagens e Mídia', {
            'fields': ('imagem', 'banner', 'video_apresentacao')
        }),
        ('Descrição Institucional', {
            'fields': ('descricao', 'missao', 'visao', 'valores')
        }),
        ('Informações Adicionais', {
            'fields': ('ano_fundacao', 'horario_funcionamento', 'tipo', 'modalidade')
        }),
        ('Redes Sociais', {
            'fields': ('facebook', 'instagram', 'linkedin', 'youtube', 'tiktok', 'whatsapp')
        }),
        ('Configurações', {
            'fields': ('destaque', 'verificado', 'slug')
        }),
        ('Métricas', {
            'fields': ('total_seguidores', 'total_visualizacoes'),
            'classes': ('collapse',)
        }),
    )
    
    def centro_nome(self, obj):
        return obj.centro.nome
    centro_nome.short_description = 'Centro'
    
    def destaque_display(self, obj):
        return format_html(
            '<span style="color: {};">●</span>',
            'gold' if obj.destaque else 'gray'
        )
    destaque_display.short_description = 'D'
    
    def verificado_display(self, obj):
        return format_html(
            '<span style="color: {};">●</span>',
            'blue' if obj.verificado else 'gray'
        )
    verificado_display.short_description = 'V'

@admin.register(ConviteCentro)
class ConviteCentroAdmin(UnfoldModelAdmin):
    list_display = ['centro', 'token', 'criado_em', 'usado_display']
    list_filter = ['usado', 'criado_em']
    search_fields = ['centro__nome', 'centro__email', 'token']
    readonly_fields = ['token', 'criado_em']
    
    def usado_display(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.usado else 'red',
            'Sim' if obj.usado else 'Não'
        )
    usado_display.short_description = 'Usado'

# ========== ADMINS PARA MODELOS RELACIONADOS ==========
@admin.register(Certificacao)
class CertificacaoAdmin(UnfoldModelAdmin):
    list_display = ['nome', 'orgao_emissor', 'centro', 'logo_preview']
    list_filter = ['orgao_emissor']
    search_fields = ['nome', 'orgao_emissor', 'centro__nome']
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="max-height: 30px;" />', obj.logo.url)
        return "-"
    logo_preview.short_description = 'Logo'

@admin.register(Equipe)
class EquipeAdmin(UnfoldModelAdmin):
    list_display = ['nome', 'cargo', 'centro', 'ordem', 'foto_preview']
    list_filter = ['cargo']
    search_fields = ['nome', 'cargo', 'centro__nome']
    list_editable = ['ordem']
    
    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="max-height: 40px; border-radius: 50%;" />', obj.foto.url)
        return "-"
    foto_preview.short_description = 'Foto'

@admin.register(Depoimento)
class DepoimentoAdmin(UnfoldModelAdmin):
    list_display = ['nome', 'cargo', 'nota', 'centro', 'aprovado', 'data']
    list_filter = ['aprovado', 'nota', 'data']
    search_fields = ['nome', 'cargo', 'centro__nome', 'texto']
    list_editable = ['aprovado']
    actions = [aprovar_depoimentos]
    
    def nota_display(self, obj):
        return '★' * obj.nota
    nota_display.short_description = 'Nota'

@admin.register(Evento)
class EventoAdmin(UnfoldModelAdmin):
    list_display = ['titulo', 'tipo', 'centro', 'data_inicio', 'destaque']
    list_filter = ['tipo', 'destaque', 'data_inicio']
    search_fields = ['titulo', 'centro__nome', 'local']
    list_editable = ['destaque']
    date_hierarchy = 'data_inicio'

@admin.register(ReelCentro)
class ReelCentroAdmin(UnfoldModelAdmin):
    list_display = [
        'titulo', 
        'centro', 
        'visualizacoes', 
        'curtidas', 
        'destaque', 
        'publico',
        'data_publicacao'
    ]
    list_filter = ['destaque', 'publico', 'data_publicacao']
    search_fields = ['titulo', 'centro__nome', 'descricao']
    list_editable = ['destaque', 'publico']
    readonly_fields = ['visualizacoes', 'curtidas', 'comentarios', 'compartilhamentos']

@admin.register(CurtidaReel)
class CurtidaReelAdmin(UnfoldModelAdmin):
    list_display = ['reel', 'aluno', 'data_curtida']
    list_filter = ['data_curtida']
    search_fields = ['reel__titulo', 'aluno__nome']

@admin.register(ComentarioReel)
class ComentarioReelAdmin(UnfoldModelAdmin):
    list_display = ['reel', 'aluno', 'texto_resumido', 'aprovado', 'data_comentario']
    list_filter = ['aprovado', 'data_comentario']
    search_fields = ['reel__titulo', 'aluno__nome', 'texto']
    list_editable = ['aprovado']
    
    def texto_resumido(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_resumido.short_description = 'Comentário'

@admin.register(Conversa)
class ConversaAdmin(UnfoldModelAdmin):
    list_display = ['centro', 'aluno', 'data_criacao', 'ultima_mensagem', 'ativa']
    list_filter = ['ativa', 'data_criacao']
    search_fields = ['centro__nome', 'aluno__nome']

@admin.register(Mensagem)
class MensagemAdmin(UnfoldModelAdmin):
    list_display = ['conversa', 'remetente_info', 'tipo', 'data_envio', 'lida']
    list_filter = ['tipo', 'lida', 'data_envio']
    
    def remetente_info(self, obj):
        if obj.remetente_aluno:
            return f"Aluno: {obj.remetente_aluno.nome}"
        return f"Centro: {obj.remetente_centro.nome}"
    remetente_info.short_description = 'Remetente'

# ========== REGISTRO DOS MODELOS RESTANTES ==========
@admin.register(Diferencial)
class DiferencialAdmin(UnfoldModelAdmin):
    list_display = ['titulo', 'centro', 'icone']
    search_fields = ['titulo', 'centro__nome']

@admin.register(AreaFormacao)
class AreaFormacaoAdmin(UnfoldModelAdmin):
    list_display = ['nome', 'centro', 'ordem']
    list_editable = ['ordem']
    search_fields = ['nome', 'centro__nome']

@admin.register(Recurso)
class RecursoAdmin(UnfoldModelAdmin):
    list_display = ['nome', 'centro', 'icone']
    search_fields = ['nome', 'centro__nome']

@admin.register(Estatistica)
class EstatisticaAdmin(UnfoldModelAdmin):
    list_display = ['titulo', 'valor', 'centro', 'ordem']
    list_editable = ['ordem']
    search_fields = ['titulo', 'centro__nome']

@admin.register(Parceria)
class ParceriaAdmin(UnfoldModelAdmin):
    list_display = ['nome_empresa', 'centro', 'tipo_parceria', 'ativa']
    list_filter = ['ativa', 'tipo_parceria']
    search_fields = ['nome_empresa', 'centro__nome']
    list_editable = ['ativa']

@admin.register(GaleriaImagem)
class GaleriaImagemAdmin(UnfoldModelAdmin):
    list_display = ['titulo', 'centro', 'imagem_preview', 'ordem']
    list_editable = ['ordem']
    search_fields = ['titulo', 'centro__nome']
    
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="max-height: 40px;" />', obj.imagem.url)
        return "-"
    imagem_preview.short_description = 'Imagem'

@admin.register(VisualizacaoPerfil)
class VisualizacaoPerfilAdmin(UnfoldModelAdmin):
    list_display = ['centro', 'aluno', 'ip_address', 'data_visualizacao']
    list_filter = ['data_visualizacao']
    search_fields = ['centro__nome', 'aluno__nome', 'ip_address']

@admin.register(Filial)
class FilialAdmin(UnfoldModelAdmin):
    list_display = ['nome', 'centro_principal', 'telefone', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'centro_principal__nome', 'email']

# ========== CONFIGURAÇÃO DO ADMIN SITE ==========
admin.site.site_header = "Administração do Sistema de Centros de Formação"
admin.site.site_title = "Sistema de Centros"
admin.site.index_title = "Gestão de Centros de Formação"