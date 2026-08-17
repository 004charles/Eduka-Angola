from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
# from django.contrib.gis.db import models as gis_models
from django.utils.safestring import mark_safe
# Note: CentroDeFormacao will be imported where used to avoid circular imports if needed
# or we can rely on string references.

class UsuarioManager(BaseUserManager):
    """
    Gestor personalizado para o modelo Usuario.
    Lida com o registro de usuários normais e administradores usando email como identificador.
    """
    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        if not password:
            raise ValueError("Superuser deve ter uma senha definida.")

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, nome, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de Usuário Centralizado para todo o projeto.
    Suporta diferentes funções: ADMIN, ALUNO, GESTOR, INSTRUTOR.
    Usa o email para autenticação em vez de nome de usuário.
    """
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('ALUNO', 'Aluno'),
        ('GESTOR', 'Gestor de Centro Principal'),
        ('GESTOR_FILIAL', 'Gestor de Filial'),
        ('INSTRUTOR', 'Instrutor da Plataforma'),
    ]

    nome = models.CharField(_('Nome Completo'), max_length=100, blank=True, null=True)
    email = models.EmailField(_('E-mail'), unique=True)
    tipo_usuario = models.CharField(_('Tipo de Usuário'), max_length=20, choices=TIPO_USUARIO_CHOICES, default='ALUNO', db_index=True)
    is_active = models.BooleanField(_('Ativo'), default=True, db_index=True)
    is_staff = models.BooleanField(_('Equipe'), default=False)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True, db_index=True)
    data_atualizacao = models.DateTimeField(_('Data de Atualização'), auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    objects = UsuarioManager()

    def get_full_name(self):
        return self.nome

    def get_short_name(self):
        return self.nome.split()[0] if self.nome else self.email

    def __str__(self):
        return self.nome if self.nome else self.email

    def get_foto_perfil_url(self):
        """Retorna a URL da foto de perfil do aluno se existir."""
        if hasattr(self, 'aluno_profile'):
            if hasattr(self.aluno_profile, 'perfil') and self.aluno_profile.perfil.get_foto_perfil_url():
                return self.aluno_profile.perfil.get_foto_perfil_url()
        return None

    def get_iniciais(self):
        """Retorna as iniciais do nome para o avatar."""
        if self.nome:
            return "".join([n[0].upper() for n in self.nome.split()[:2]])
        return self.email[:2].upper()

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuarios'





class Aluno(models.Model):
    """
    Representa um perfil de aluno no sistema.
    Vinculado a uma conta de Usuario com a função 'ALUNO'.
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='aluno_profile', null=True, blank=True)
    nome = models.CharField(_('Nome Completo'), max_length=100)
    # email and senha are now in usuario
    data_cadastro = models.DateTimeField(_('Data de Cadastro'), default=timezone.now, db_index=True)
    ativo = models.BooleanField(_('Ativo'), default=True, db_index=True)
    
    def __str__(self):
        return f"Aluno: {self.nome}"

    def get_foto_perfil_url(self):
        """Retorna a URL da foto de perfil do aluno se existir."""
        if hasattr(self, 'perfil'):
            return self.perfil.get_foto_perfil_url()
        return None

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


# CentroSeguimento moved to gestoreduka/models.py


        

class PerfilAluno(models.Model):
    NIVEL_CONHECIMENTO_CHOICES = [
        ('B', _('Básico - Estou a começar agora')),
        ('I', _('Intermédio - Já tenho alguma base')),
        ('A', _('Avançado - Quero aprofundar conhecimentos')),
    ]

    aluno = models.OneToOneField('Aluno', on_delete=models.CASCADE, related_name='perfil')
    onboarding_completo = models.BooleanField(_('Onboarding Completo'), default=False)
    nivel_conhecimento = models.CharField(_('Nível de Conhecimento'), max_length=1, choices=NIVEL_CONHECIMENTO_CHOICES, default='B')
    interesses = models.ManyToManyField('cursos_app.Categoria', blank=True, related_name='alunos_interessados')
    
    imagem = models.ImageField(_('Imagem de Perfil'), upload_to='perfil_alunos/', null=True, blank=True)
    foto_de_perfil = models.ImageField(_('Foto de Perfil'), upload_to='fotos_perfil/', null=True, blank=True)
    foto_de_capa = models.ImageField(_('Foto de Capa'), upload_to='fotos_capa/', null=True, blank=True)
    biografia = models.TextField(_('Biografia'), blank=True)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True, null=True)
    github = models.URLField(_('GitHub'), blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)
    
    bilhete_frente = models.FileField(_('BI Frente'), upload_to='documentos/bilhetes/', null=True, blank=True)
    bilhete_verso = models.FileField(_('BI Verso'), upload_to='documentos/bilhetes/', null=True, blank=True)

    from django.conf import settings
    if ('django.contrib.gis' in settings.INSTALLED_APPS and 
        'gis' in settings.DATABASES['default']['ENGINE']):
        from django.contrib.gis.db import models as gis_models
        localizacao = gis_models.PointField(
            _('Localização Geográfica'),
            geography=True,
            blank=True,
            null=True,
            srid=4326
        )
    else:
        localizacao = models.CharField(
            _('Localização (Fallback)'),
            max_length=100,
            blank=True,
            null=True
        )

    def __str__(self):
        return f"Perfil de {self.aluno.nome}"

    def get_foto_perfil_url(self):
        """Retorna a URL da foto de perfil ou um avatar padrão se não existir"""
        if self.foto_de_perfil:
            return self.foto_de_perfil.url
        elif self.imagem:
            return self.imagem.url
        return '/static/assets/images/client/avatar_default.png'


    def get_foto_ou_inicial(self):
        """Retorna a foto de perfil ou a inicial do nome"""
        foto_url = self.get_foto_perfil_url()
        if foto_url:
            return f'<img src="{foto_url}" alt="{self.aluno.nome}" class="rounded-circle" style="width: 40px; height: 40px; object-fit: cover;">'
        else:
            inicial = self.aluno.nome[0].upper() if self.aluno.nome else 'A'
            return f'<div class="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">{inicial}</div>'

    def get_foto_ou_inicial_html(self, size=40):
        """Retorna HTML para exibir foto ou inicial com tamanho personalizado"""
        foto_url = self.get_foto_perfil_url()
        if foto_url:
            return f'<img src="{foto_url}" alt="{self.aluno.nome}" class="rounded-circle" style="width: {size}px; height: {size}px; object-fit: cover;">'
        else:
            inicial = self.aluno.nome[0].upper() if self.aluno.nome else 'A'
            return f'<div class="rounded-circle bg-main-600 text-white d-flex align-items-center justify-content-center fw-bold" style="width: {size}px; height: {size}px; font-size: {size*0.4}px;">{inicial}</div>'

    def get_inicial_nome(self):
        """Retorna apenas a inicial do nome"""
        return self.aluno.nome[0].upper() if self.aluno.nome else 'A'

    class Meta:
        verbose_name = 'Perfil do Aluno'
        verbose_name_plural = 'Perfis dos Alunos'
                


class PreferenciaAprendizagem(models.Model):
    """Preferências explícitas do aluno, separadas da actividade e fáceis de evoluir."""
    FAIXA_PRECO_CHOICES = [
        ('QUALQUER', 'Qualquer valor'),
        ('GRATUITOS', 'Apenas gratuitos'),
        ('ATE_25000', 'Até 25 000 Kz'),
        ('ATE_50000', 'Até 50 000 Kz'),
    ]
    aluno = models.OneToOneField('Aluno', on_delete=models.CASCADE, related_name='preferencias_aprendizagem')
    categorias = models.ManyToManyField('cursos_app.Categoria', blank=True, related_name='preferencias_aprendizagem')
    modalidades = models.JSONField(default=list, blank=True)
    objectivos = models.JSONField(default=list, blank=True)
    disponibilidades = models.JSONField(default=list, blank=True)
    provincias = models.JSONField(default=list, blank=True)
    faixa_preco = models.CharField(max_length=20, choices=FAIXA_PRECO_CHOICES, default='QUALQUER')
    quer_certificado = models.BooleanField(null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Preferência de aprendizagem'
        verbose_name_plural = 'Preferências de aprendizagem'


# models.py (adicione ou atualize esta classe)


# usuarios/models.py
# Biblioteca, Empresa and Comentario models removed from here.
# Empresa was deleted as requested.
# Biblioteca moved to biblioteca/models.py
# Comentario moved to avaliacoes/models.py

# Empresa model deleted as requested.

class CodigoVerificacao(models.Model):
    TIPO_CHOICES = [
        ('CADASTRO', 'Cadastro'),
        ('RECUPERACAO', 'Recuperação de Senha'),
    ]
    
    email = models.EmailField(_('E-mail'))
    codigo = models.CharField(_('Código'), max_length=6)
    tipo = models.CharField(_('Tipo'), max_length=20, choices=TIPO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Código para {self.email} ({self.tipo})"
class NotificacaoAluno(models.Model):
    TIPO_CHOICES = [
        ('CURSO', 'Novo Curso'),
        ('EVENTO', 'Novo Evento'),
        ('ANUNCIO', 'Anúncio Institucional'),
        ('CHAT', 'Nova Mensagem'),
        ('CARREIRA', 'Carreira e Vagas'),
        ('SISTEMA', 'Sistema'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(_('Título'), max_length=150)
    mensagem = models.TextField(_('Mensagem'))
    link = models.CharField(_('Link (opcional)'), max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='SISTEMA')
    lida = models.BooleanField(default=False, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Notificação do Aluno'
        verbose_name_plural = 'Notificações dos Alunos'

    def __str__(self):
        return f"{self.titulo} - {self.aluno.nome}"
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Aluno)
def criar_perfil_aluno(sender, instance, created, **kwargs):
    if created:
        PerfilAluno.objects.get_or_create(aluno=instance)

class PreferenciaNotificacaoAluno(models.Model):
    """Controlos explícitos de comunicação do aluno por tema e canal."""
    aluno = models.OneToOneField(Aluno, on_delete=models.CASCADE, related_name='preferencias_notificacao')
    receber_na_plataforma = models.BooleanField('Notificações na plataforma', default=True)
    receber_por_email = models.BooleanField('Resumo por e-mail', default=True)
    novos_cursos = models.BooleanField('Novos cursos', default=True)
    novas_turmas = models.BooleanField('Novas turmas', default=True)
    novos_livros = models.BooleanField('Novos livros', default=True)
    novos_eventos = models.BooleanField('Novos eventos', default=True)
    atualizacoes_aprendizagem = models.BooleanField('Lembretes de aprendizagem', default=True)
    calendario_e_feriados = models.BooleanField('Calendário e feriados', default=True)
    resumo_semanal = models.BooleanField('Resumo semanal', default=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Preferência de notificação'
        verbose_name_plural = 'Preferências de notificações'

    def __str__(self):
        return f'Notificações — {self.aluno.nome}'


@receiver(post_save, sender=Aluno)
def criar_preferencias_notificacao(sender, instance, created, **kwargs):
    if created:
        PreferenciaNotificacaoAluno.objects.get_or_create(aluno=instance)
