from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.utils import timezone
from gestoreduka.models import CentroDeFormacao
from django.contrib.gis.db import models as gis_models



from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UsuarioManager(BaseUserManager):
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
    nome = models.CharField(_('Nome Completo'), max_length=100, blank=True, null=True)
    email = models.EmailField(_('E-mail'), unique=True)
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
        return self.nome

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        db_table = 'usuarios'



class Escola(models.Model):
    TIPO_ESCOLA_CHOICES = [
        ('PUBLICA', 'Pública'),
        ('PARTICULAR', 'Particular'),
        ('COMUNITARIA', 'Comunitária'),
    ]
    
    nome = models.CharField(_('Nome da Escola'), max_length=100)
    codigo_escola = models.CharField(_('Código INEP'), max_length=8, unique=True, blank=True, null=True)
    tipo = models.CharField(_('Tipo de Escola'), max_length=20, choices=TIPO_ESCOLA_CHOICES)
    endereco = models.CharField(_('Endereço'), max_length=255)
    telefone = models.CharField(_('Telefone'), max_length=20)
    email = models.EmailField(_('E-mail'), unique=True)
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
    nome = models.CharField(_('Nome Completo'), max_length=100)
    email = models.EmailField(_('E-mail'), unique=True)
    senha = models.CharField(_('Senha'), max_length=128)
    data_cadastro = models.DateTimeField(_('Data de Cadastro'), default=timezone.now)
    ativo = models.BooleanField(_('Ativo'), default=True)
    
    def __str__(self):
        return f"Aluno: {self.nome}"

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


class CentroSeguimento(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='centros_seguidos', verbose_name=_('Aluno'))
    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, related_name='seguidores', verbose_name=_('Centro de Formação'))
    data_seguimento = models.DateTimeField(_('Data do Seguimento'), default=timezone.now)

    class Meta:
        unique_together = ('aluno', 'centro')  # evita duplicações
        verbose_name = _('Seguimento de Centro')
        verbose_name_plural = _('Seguimentos de Centros')

    def __str__(self):
        return f"{self.aluno.nome} segue {self.centro.nome}"


        

class PerfilAluno(models.Model):
    aluno = models.OneToOneField('Aluno', on_delete=models.CASCADE, related_name='perfil')
    imagem = models.ImageField(_('Imagem de Perfil'), upload_to='perfil_alunos/', null=True, blank=True)
    foto_de_perfil = models.ImageField(_('Foto de Perfil'), upload_to='fotos_perfil/', null=True, blank=True)
    biografia = models.TextField(_('Biografia'), blank=True)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True, null=True)
    github = models.URLField(_('GitHub'), blank=True, null=True)
    criado_em = models.DateTimeField(default=timezone.now)

    localizacao = gis_models.PointField(
        _('Localização Geográfica'),
        geography=True,
        blank=True,
        null=True,
        srid=4326
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
                
class Comentario(models.Model):
    aluno = models.ForeignKey('Aluno', on_delete=models.CASCADE, related_name='comentarios')
    curso = models.ForeignKey('cursos_app.Curso', on_delete=models.CASCADE, related_name='comentarios')

    comentario = models.TextField(_('Comentário'))
    data_comentario = models.DateTimeField(_('Data de Comentário'), default=timezone.now)
    avaliacao = models.IntegerField(_('Avaliação'), choices=[(i, i) for i in range(1, 6)], default=5)

    def __str__(self):
        return f"Comentário de {self.aluno.nome} no curso {self.curso.titulo}"

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-data_comentario']

class Biblioteca(models.Model):
    TIPO_BIBLIOTECA_CHOICES = [
        ('PUBLICA', 'Pública'),
        ('ESCOLAR', 'escolar'),
        ('UNVERSITARIA', 'universitaria'),
        ('ESPECIALIZADA', 'especializada'),
        ('COMUNITARIA', 'comunitaria'),
    ]
    nome = models.CharField(_('Nome Completo'), max_length=100)
    email = models.EmailField(_('E-mail'), unique=True)
    senha = models.CharField(_('Senha'), max_length=100)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    codigo_registro = models.CharField(_('Codigo de registro'), max_length=100, blank=True, null=True)
    ativo = models.BooleanField(default=True)
    tipo = models.CharField(_('Tipo de Biblioteca'), max_length=50, choices=TIPO_BIBLIOTECA_CHOICES)
    
    def __str__(self):
        return f"Bibliotecário: {self.nome}"

class Empresa(models.Model):
    TIPO_RAMO_ATUACAO = [
        ('TECNOLOGIA_INFORMACAO', 'tecnologia de informacao'),
        ('NEGOCIO', 'negocio'),
        ('LINGUAS', 'linguas'),
        ('ESPECIALIZADA', 'especializada'),
        ('CIENCIAS', 'ciencias'),
        ('ARTES', 'artes'),
        ('ENGENHARIA', 'engenharia'),
        ('SAUDE', 'saude'),
        ('OUTRO', 'outro'),
    ]
    nome = models.CharField(_('Nome Completo'), max_length=100)
    email = models.EmailField(_('E-mail'), unique=True)
    senha = models.CharField(_('Senha'), max_length=100)
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    experiencia_anos = models.IntegerField(_('Anos de Experiência'), default=0)
    nif = models.CharField(_('NIF'), max_length=18, unique=True)
    ramo_atuacao = models.CharField(_('Ramo de Atuação'), max_length=100, choices=TIPO_RAMO_ATUACAO)    
    numero_funcionarios = models.IntegerField(_('Número de Funcionários'))
    
    def __str__(self):
        return f"Empresa: {self.nome}"

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        db_table = 'empresas'
        
        
