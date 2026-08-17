from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from core.notification_events import queue_notification_event


class Autor(models.Model):
    nome = models.CharField(max_length=180, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    biografia = models.TextField(blank=True)
    pais = models.CharField(max_length=80, default="Angola", blank=True)
    foto = models.ImageField(upload_to="biblioteca/autores/", blank=True, null=True)
    em_destaque = models.BooleanField(default=False)

    class Meta:
        ordering = ("nome",)
        verbose_name = "Autor"
        verbose_name_plural = "Autores"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Livro(models.Model):
    FORMATO_DIGITAL = "DIGITAL"
    FORMATO_AUDIO = "AUDIO"
    FORMATO_AMBOS = "AMBOS"
    FORMATO_CHOICES = (
        (FORMATO_DIGITAL, "Leitura digital"),
        (FORMATO_AUDIO, "Audiolivro"),
        (FORMATO_AMBOS, "Leitura e áudio"),
    )
    ESTADO_RASCUNHO = "RASCUNHO"
    ESTADO_PUBLICADO = "PUBLICADO"
    ESTADO_CHOICES = (
        (ESTADO_RASCUNHO, "Rascunho"),
        (ESTADO_PUBLICADO, "Publicado"),
    )

    titulo = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    subtitulo = models.CharField(max_length=260, blank=True)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name="livros")
    editora = models.CharField(max_length=180, default="Edukangola", blank=True)
    sinopse = models.TextField()
    descricao_curta = models.CharField(max_length=260, blank=True)
    capa = models.ImageField(upload_to="biblioteca/capas/", blank=True, null=True)
    capa_url = models.URLField(blank=True, help_text="URL de uma capa editorial quando não for carregada no servidor.")
    categoria = models.CharField(max_length=100, db_index=True)
    temas = models.CharField(max_length=260, blank=True, help_text="Separar temas por vírgulas.")
    idioma = models.CharField(max_length=12, default="pt")
    paginas = models.PositiveIntegerField(default=0)
    ano_publicacao = models.PositiveIntegerField(blank=True, null=True)
    formato = models.CharField(max_length=12, choices=FORMATO_CHOICES, default=FORMATO_DIGITAL)
    conteudo_leitura = models.TextField(blank=True, help_text="Texto autorizado para leitura no navegador.")
    excerto = models.TextField(blank=True)
    narrador = models.CharField(max_length=180, blank=True)
    direitos_confirmados = models.BooleanField(default=False, help_text="Confirma que a Edukangola pode distribuir esta obra.")
    gratuito = models.BooleanField(default=True)
    em_destaque = models.BooleanField(default=False)
    selecao_semana = models.BooleanField(default=False)
    estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default=ESTADO_RASCUNHO, db_index=True)
    publicado_em = models.DateTimeField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-selecao_semana", "-em_destaque", "-publicado_em", "titulo")
        verbose_name = "Livro"
        verbose_name_plural = "Livros"

    def save(self, *args, **kwargs):
        previous_estado = None
        if self.pk:
            previous_estado = type(self).objects.filter(pk=self.pk).values_list('estado', flat=True).first()
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
        if self.estado == self.ESTADO_PUBLICADO and previous_estado != self.ESTADO_PUBLICADO:
            queue_notification_event(
                'book.published',
                f'book.published:{self.pk}',
                {'book_id': self.pk, 'title': self.titulo, 'author': self.autor.nome, 'link': f'/biblioteca/{self.slug}'},
                occurred_at=self.publicado_em or self.atualizado_em,
            )

    @property
    def tem_leitura(self):
        return bool(self.conteudo_leitura.strip())

    @property
    def tem_audio(self):
        return self.capitulos_audio.exists()

    def __str__(self):
        return self.titulo


class CapituloAudio(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name="capitulos_audio")
    titulo = models.CharField(max_length=220)
    ordem = models.PositiveIntegerField(default=1)
    duracao_segundos = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    audio = models.FileField(upload_to="biblioteca/audio/", blank=True, null=True)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ("ordem", "id")
        constraints = [models.UniqueConstraint(fields=("livro", "ordem"), name="biblioteca_capitulo_ordem_unica")]
        verbose_name = "Capítulo de áudio"
        verbose_name_plural = "Capítulos de áudio"

    def __str__(self):
        return f"{self.livro} · {self.ordem:02d} · {self.titulo}"


class BibliotecaPessoal(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="biblioteca_pessoal")
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name="presencas_biblioteca")
    guardado = models.BooleanField(default=True)
    progresso_leitura = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    pagina_leitura = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    progresso_audio_segundos = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    ultima_atividade = models.DateTimeField(auto_now=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-ultima_atividade",)
        constraints = [models.UniqueConstraint(fields=("usuario", "livro"), name="biblioteca_usuario_livro_unico")]
        verbose_name = "Livro na biblioteca pessoal"
        verbose_name_plural = "Biblioteca pessoal"

    def __str__(self):
        return f"{self.usuario} · {self.livro}"
