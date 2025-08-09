from django.db import models
from usuarios.models import Usuario
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(_('Nome'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), max_length=120, unique=True)
    descricao = models.TextField(_('Descrição'), blank=True)
    criada_em = models.DateTimeField(_('Criada em'), default=timezone.now)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Tag(models.Model):
    nome = models.CharField(_('Nome'), max_length=50, unique=True)
    slug = models.SlugField(_('Slug'), max_length=60, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['nome']

    def __str__(self):
        return self.nome



class Post(models.Model):
    STATUS_CHOICES = (
        ('rascunho', 'Rascunho'),
        ('publicado', 'Publicado'),
    )

    titulo = models.CharField(_('Título'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=220, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    conteudo = models.TextField(_('Conteúdo'))
    resumo = models.CharField(
        _('Resumo'), 
        max_length=300, 
        blank=True,
        help_text="Breve descrição que aparecerá nas listagens"
    )
    imagem_capa = models.ImageField(_('Imagem de Capa'), upload_to='posts/capas/', blank=True, null=True)
    publicado_em = models.DateTimeField(_('Publicado em'), default=timezone.now)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='rascunho')
    visualizacoes = models.PositiveIntegerField(_('Visualizações'), default=0)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        ordering = ['-publicado_em']

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    nome = models.CharField(_('Nome'), max_length=100)
    email = models.EmailField(_('E-mail'))
    mensagem = models.TextField(_('Mensagem'))
    criado_em = models.DateTimeField(_('Criado em'), default=timezone.now)
    aprovado = models.BooleanField(_('Aprovado'), default=True)

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Comentário de {self.nome} no post {self.post.titulo}"