from django.db import models
from usuarios.models import Usuario
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from core.upload_validators import validate_image_file


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
    TIPO_CONTEUDO_CHOICES = (
        ('artigo', 'Artigo'),
        ('video', 'Notícia em vídeo'),
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
    imagem_capa = models.ImageField(
        _('Imagem de Capa'), upload_to='posts/capas/', blank=True, null=True,
        validators=[validate_image_file]
    )
    tipo_conteudo = models.CharField(_('Tipo de conteúdo'), max_length=12, choices=TIPO_CONTEUDO_CHOICES, default='artigo')
    video_url = models.URLField(_('URL do vídeo'), blank=True, help_text='URL pública do vídeo, por exemplo YouTube ou Vimeo.')
    duracao_video = models.CharField(_('Duração do vídeo'), max_length=20, blank=True)
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


class ReacaoComentario(models.Model):
    REACOES_CHOICES = [
        ('like', 'Curtir 👍'),
        ('love', 'Amei ❤️'),
        ('laugh', 'Haha 😂'),
        ('surprised', 'Uau 😮'),
        ('sad', 'Triste 😢'),
        ('angry', 'Bravo 😡'),
    ]
    comentario = models.ForeignKey('Comentario', on_delete=models.CASCADE, related_name='reacoes')
    usuario = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=REACOES_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('comentario', 'usuario', 'tipo')

    def __str__(self):
        return f"{self.usuario} reagiu com {self.get_tipo_display()} no comentário {self.comentario.id}"


from usuarios.models import Aluno

class Comentario(models.Model):
    REACOES_CHOICES = ReacaoComentario.REACOES_CHOICES 
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    aluno = models.ForeignKey(Aluno, on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_comentarios')
    nome = models.CharField(_('Nome'), max_length=100)
    email = models.EmailField(_('E-mail'))
    mensagem = models.TextField(_('Mensagem'))
    criado_em = models.DateTimeField(_('Criado em'), default=timezone.now)
    aprovado = models.BooleanField(_('Aprovado'), default=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='respostas'
    )

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-criado_em']

    def __str__(self):
        return f"Comentário de {self.nome} no post {self.post.titulo}"

    def contar_reacoes(self, tipo):
        return self.reacoes.filter(tipo=tipo).count()

    def is_resposta(self):
        return self.parent is not None

    def get_user_reaction(self, user):
        if user.is_authenticated:
            try:
                return self.reacoes.get(usuario=user).tipo
            except ReacaoComentario.DoesNotExist:
                return None
        return None