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
    Suporta diferentes funções: ADMIN, ALUNO, GESTOR, BIBLIOTECA, ESCOLA.
    Usa o email para autenticação em vez de nome de usuário.
    """
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('ALUNO', 'Aluno'),
        ('GESTOR', 'Gestor de Centro Principal'),
        ('GESTOR_FILIAL', 'Gestor de Filial'),
        ('ESCOLA', 'Escola'),
    ]

    nome = models.CharField(_('Nome Completo'), max_length=100, blank=True, null=True)
    email = models.EmailField(_('E-mail'), unique=True)
    tipo_usuario = models.CharField(_('Tipo de Usuário'), max_length=20, choices=TIPO_USUARIO_CHOICES, default='ALUNO')
    is_active = models.BooleanField(_('Ativo'), default=True)
    is_staff = models.BooleanField(_('Equipe'), default=False)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
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



class Escola(models.Model):
    """
    Representa uma Instituição de Ensino (Escola).
    Vinculada a uma conta de Usuario com a função 'ESCOLA'.
    """
    TIPO_ESCOLA_CHOICES = [
        ('PUBLICA', 'Pública'),
        ('PARTICULAR', 'Particular'),
        ('COMUNITARIA', 'Comunitária'),
    ]
    
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='escola_profile', null=True, blank=True)
    nome = models.CharField(_('Nome da Escola'), max_length=100)
    codigo_escola = models.CharField(_('Código INEP'), max_length=8, unique=True, blank=True, null=True)
    tipo = models.CharField(_('Tipo de Escola'), max_length=20, choices=TIPO_ESCOLA_CHOICES)
    endereco = models.CharField(_('Endereço'), max_length=255)
    telefone = models.CharField(_('Telefone'), max_length=20)
    # email is now in usuario
    site = models.URLField(_('Site'), blank=True, null=True)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    ativo = models.BooleanField(_('Ativo'), default=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'
        db_table = 'escolas'
        ordering = ['nome']


class Aluno(models.Model):
    """
    Representa um perfil de aluno no sistema.
    Vinculado a uma conta de Usuario com a função 'ALUNO'.
    """
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='aluno_profile', null=True, blank=True)
    nome = models.CharField(_('Nome Completo'), max_length=100)
    # email and senha are now in usuario
    data_cadastro = models.DateTimeField(_('Data de Cadastro'), default=timezone.now)
    ativo = models.BooleanField(_('Ativo'), default=True)
    
    def __str__(self):
        return f"Aluno: {self.nome}"

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


# CentroSeguimento moved to gestoreduka/models.py


        

class PerfilAluno(models.Model):
    aluno = models.OneToOneField('Aluno', on_delete=models.CASCADE, related_name='perfil')
    imagem = models.ImageField(_('Imagem de Perfil'), upload_to='perfil_alunos/', null=True, blank=True)
    foto_de_perfil = models.ImageField(_('Foto de Perfil'), upload_to='fotos_perfil/', null=True, blank=True)
    biografia = models.TextField(_('Biografia'), blank=True)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True, null=True)
    github = models.URLField(_('GitHub'), blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)
    
    bilhete_frente = models.FileField(_('BI Frente'), upload_to='documentos/bilhetes/', null=True, blank=True)
    bilhete_verso = models.FileField(_('BI Verso'), upload_to='documentos/bilhetes/', null=True, blank=True)

    from django.conf import settings
    if 'django.contrib.gis' in settings.INSTALLED_APPS and not settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
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
        """Retorna a URL da foto de perfil ou None se não existir"""
        if self.foto_de_perfil:
            return self.foto_de_perfil.url
        elif self.imagem:
            return self.imagem.url
        return None

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
        ('SISTEMA', 'Sistema'),
    ]

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(_('Título'), max_length=150)
    mensagem = models.TextField(_('Mensagem'))
    link = models.CharField(_('Link (opcional)'), max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='SISTEMA')
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Notificação do Aluno'
        verbose_name_plural = 'Notificações dos Alunos'

    def __str__(self):
        return f"{self.titulo} - {self.aluno.nome}"
