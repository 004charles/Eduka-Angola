from django.db import models
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.utils import timezone
from usuarios.models import Aluno
from django.core.validators import MinValueValidator
from gestoreduka.models import CentroDeFormacao
from django.core.exceptions import ValidationError


class Instrutor(models.Model):
    TIPO_CHOICES_ESPECIALIZACAO = [
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
    nome = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    biografia = models.TextField()
    foto = models.ImageField(upload_to='instrutores/', null=True, blank=True)
    email = models.EmailField(unique=True)
    area_especializacao = models.CharField(max_length=100, choices=TIPO_CHOICES_ESPECIALIZACAO)
    data_cadastro = models.DateField(default=timezone.now)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Instrutor'
        verbose_name_plural = 'Instrutores'
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
    
class PerfilInstrutor(models.Model):
    instrutor = models.OneToOneField('Instrutor', on_delete=models.CASCADE, related_name='perfil')
    foto_capa = models.ImageField(upload_to='instrutores/capas/', null=True, blank=True)
    biografia_completa = models.TextField()
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    total_alunos = models.PositiveIntegerField(default=0)
    total_cursos = models.PositiveIntegerField(default=0)
    total_avaliacoes = models.PositiveIntegerField(default=0)
    nota_media = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    def __str__(self):
        return f'Perfil de {self.instrutor.nome}'
    
class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    imagem = models.ImageField(upload_to='categorias/', blank=True, null=True)
    mensagem_destaque = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Mensagem personalizada para exibir acima dos cursos desta categoria"
    )

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome
        
class Curso(models.Model):
    NIVEL_CHOICES = [
        ('B', 'Básico'),
        ('I', 'Intermediário'),
        ('A', 'Avançado'),
    ]

    IDIOMA_CHOICES = [
        ('PT', 'Português'),
        ('EN', 'Inglês'),
        ('ES', 'Espanhol'),
        ('FR', 'Francês'),
        ('OUTRO', 'Outro'),
    ]

    TURNO_CHOICES = [
        ('M', 'Manhã'),
        ('T', 'Tarde'),
        ('N', 'Noite'),
        ('I', 'Integral'),
    ]

    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, verbose_name=_('Centro de Formação'), related_name='cursos')
    titulo = models.CharField(_('Título do Curso'), max_length=200, validators=[MinLengthValidator(3)])
    descricao = models.TextField(_('Descrição Completa'))
    nivel = models.CharField(_('Nível'), max_length=1, choices=NIVEL_CHOICES, default='B')
    idioma = models.CharField(_('Idioma do Curso'), max_length=5, choices=IDIOMA_CHOICES, default='PT')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='curso')
    certificado = models.BooleanField(_('Fornece Certificado'), default=True)
    instrutores = models.ManyToManyField(Instrutor, related_name='cursos', verbose_name=_('Instrutores'))
    carga_horaria = models.PositiveIntegerField(_('Carga Horária (horas)'))
    preco = models.DecimalField(
        _('Valor do Curso'),
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)]
    )
    vagas = models.PositiveIntegerField(_('Número de Vagas'))
    data_inicio = models.DateTimeField(default=timezone.now)
    data_termino = models.DateField(_('Data de Término'))
    turno = models.CharField(_('Turno'), max_length=1, choices=TURNO_CHOICES, default='M')
    ativo = models.BooleanField(_('Curso Ativo'), default=True)
    publicado = models.BooleanField(_('Publicado'), default=False)
    imagem = models.ImageField(_('Imagem do Curso'), upload_to='cursos/', null=True, blank=True)
    requisitos = models.TextField(_('Pré-requisitos'), blank=True, null=True)
    video_apresentacao = models.URLField(_('Vídeo de Apresentação'), blank=True, null=True)
    destaque = models.BooleanField(_('Curso em Destaque'), default=False)

    def clean(self):
        if self.data_inicio and self.data_termino:
            if self.data_inicio.date() > self.data_termino:
                raise ValidationError(_('A data de início deve ser anterior à data de término'))

    def __str__(self):
        return f"{self.titulo} - {self.centro.nome}"

    class Meta:
        verbose_name = _('Curso')
        verbose_name_plural = _('Cursos')
        db_table = 'cursos'
        ordering = ['data_inicio']
        indexes = [models.Index(fields=['titulo', 'centro'])]

class Favorito(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='favoritos')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='favoritado_por')
    data_adicao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together = ('aluno', 'curso')  
        ordering = ['-data_adicao']

    def __str__(self):
        return f"{self.aluno.nome} - {self.curso.titulo}"


class Galeria(models.Model):
    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, related_name='galeria')
    imagem = models.ImageField(_('Imagem'), upload_to='galeria/')
    descricao = models.CharField(_('Descrição'), max_length=200, blank=True)
    categoria = models.CharField(_('Categoria'), max_length=50, choices=[
        ('SALAS', 'Salas de Aula'),
        ('LABS', 'Laboratórios'),
        ('EVENTOS', 'Eventos')
    ])



class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    titulo = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'

    def __str__(self):
        return f"{self.ordem}. {self.titulo}"
    
    
class Video(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='videos')
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    url = models.URLField(max_length=200, blank=True)
    arquivo = models.FileField(upload_to='cursos/videos/', blank=True, null=True)
    duracao = models.DurationField(blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)
    liberado = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordem']  
        verbose_name = 'Vídeo'
        verbose_name_plural = 'Vídeos'

    def __str__(self):
        return self.titulo

    @property
    def fonte_video(self):
        """Retorna a fonte do vídeo (URL externa ou arquivo local)"""
        return self.url if self.url else self.arquivo.url if self.arquivo else None
    
class MaterialApoio(models.Model):
    TIPO_CHOICES = [
        ('PDF', 'Documento PDF'),
        ('SLIDE', 'Apresentação de Slides'),
        ('PLANILHA', 'Planilha'),
        ('CODIGO', 'Código-fonte'),
        ('OUTRO', 'Outro'),
    ]

    curso = models.ForeignKey(
        Curso, 
        on_delete=models.CASCADE, 
        related_name='materiais_apoio'
    )
    titulo = models.CharField(max_length=100)
    arquivo = models.FileField(upload_to='cursos/materiais/')
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        default='PDF'
    )
    data_adicao = models.DateTimeField(default=timezone.now)
    disponivel = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Material de Apoio'
        verbose_name_plural = 'Materiais de Apoio'
        ordering = ['-data_adicao']

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"


class Inscricao(models.Model):
    STATUS_CHOICES = [
        ('PEN', 'Pendente'),
        ('APR', 'Aprovado'),
        ('REJ', 'Rejeitado'),
        ('CAN', 'Cancelado'),
    ]
    
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, verbose_name=_('Aluno'))
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, verbose_name=_('Curso'))
    data_inscricao = models.DateTimeField(_('Data de Inscrição'), default=timezone.now)
    status = models.CharField(_('Status'), max_length=3, choices=STATUS_CHOICES, default='PEN')
    certificado_emitido = models.BooleanField(_('Certificado Emitido'), default=False)
    nota_final = models.DecimalField(_('Nota Final'), max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Inscrição #{self.id} - {self.aluno.nome} em {self.curso.titulo}"

    class Meta:
        verbose_name = 'Inscrição'
        verbose_name_plural = 'Inscrições'
        unique_together = ['aluno', 'curso']

