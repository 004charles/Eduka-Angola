from django.db import models
from django.db import models
from django.core.validators import FileExtensionValidator



class Galeria(models.Model):
    imagem = models.ImageField("Imagem", upload_to="galeria/")
    link = models.URLField("Link", blank=True, null=True)  
    usuario = models.CharField("Usuário", max_length=100, blank=True, null=True)  
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagem da Galeria"
        verbose_name_plural = "Galeria de Imagens"
        ordering = ['-criado_em']

    def __str__(self):
        return self.usuario or f"Imagem {self.id}"

class SobreNos(models.Model):
    titulo = models.CharField(max_length=200) 
    descricao = models.TextField()  
    missao = models.TextField(blank=True, null=True)  
    visao = models.TextField(blank=True, null=True)  
    valores = models.TextField(blank=True, null=True) 

    # Campos de Contacto Adicionados
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)
    email_contato = models.EmailField("E-mail de Contacto", blank=True, null=True)
    endereco = models.TextField("Endereço", blank=True, null=True)
    mapa_iframe = models.TextField("Iframe do Google Maps", blank=True, null=True, help_text="Cole aqui o código de incorporação do Google Maps")

    imagem_destaque = models.ImageField(upload_to='sobre_nos/', blank=True, null=True)  

    video_explicacao = models.FileField(
        upload_to='videos/',
        blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv'])]
    )  

    data_atualizacao = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.titulo

class MensagemContato(models.Model):
    nome = models.CharField("Nome", max_length=150)
    email = models.EmailField("E-mail")
    assunto = models.CharField("Assunto", max_length=200)
    mensagem = models.TextField("Mensagem")
    lido = models.BooleanField("Lido?", default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mensagem de Contacto"
        verbose_name_plural = "Mensagens de Contacto"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome} - {self.assunto}"

class Publicidade(models.Model):
    POSICAO_CHOICES = [
        ('HERO_BOLSA', 'Hero Banner Principal (Bolsas)'),
        ('EMPRESAS', 'Banner Formação para Empresas'),
        ('GERAL', 'Geral / Outros'),
    ]

    titulo = models.CharField("Título", max_length=200, blank=True, null=True)
    subtitulo = models.TextField("Subtítulo / Descrição Curta", blank=True, null=True)
    tag_label = models.CharField("Etiqueta / Tag", max_length=100, blank=True, null=True, help_text="Ex: Publicidade · Jovem Digital")
    posicao = models.CharField("Posição no Site", max_length=20, choices=POSICAO_CHOICES, default='GERAL', db_index=True)
    descricao = models.TextField("Descrição", blank=True, null=True)
    imagem_fundo = models.ImageField("Imagem de Fundo / Banner", upload_to="publicidades/", blank=True, null=True)
    url_destino = models.URLField("URL de Destino", blank=True, null=True)
    texto_botao = models.CharField("Texto do Botão", max_length=50, default="Saiba Mais", blank=True)
    ativo = models.BooleanField("Ativo", default=True, db_index=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Publicidade"
        verbose_name_plural = "Publicidades"
        ordering = ['-data_criacao']

    def __str__(self):
        return f"[{self.get_posicao_display()}] {self.titulo or f'Publicidade {self.id}'}"


class ClienteAPIKey(models.Model):
    nome_cliente = models.CharField("Nome do Cliente / Site", max_length=150, unique=True, help_text="Ex: Mobile App, Site Parceiro, etc.")
    chave = models.CharField("Chave de API", max_length=64, unique=True, blank=True)
    ativo = models.BooleanField("Ativo?", default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    ultimo_uso = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Chave de API de Cliente"
        verbose_name_plural = "Chaves de API de Clientes"

    def save(self, *args, **kwargs):
        if not self.chave:
            import secrets
            self.chave = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome_cliente} ({'Ativo' if self.ativo else 'Inativo'})"


class PerguntaFrequente(models.Model):
    IDIOMA_PT = 'pt'
    IDIOMA_EN = 'en'
    IDIOMA_FR = 'fr'
    IDIOMA_ZH = 'zh'
    IDIOMA_CHOICES = (
        (IDIOMA_PT, 'Português'),
        (IDIOMA_EN, 'English'),
        (IDIOMA_FR, 'Français'),
        (IDIOMA_ZH, '中文'),
    )

    categoria = models.CharField('Categoria', max_length=120, db_index=True)
    pergunta = models.CharField('Pergunta', max_length=420)
    resposta = models.TextField('Resposta')
    idioma = models.CharField('Idioma', max_length=8, choices=IDIOMA_CHOICES, default=IDIOMA_PT, db_index=True)
    ordem = models.PositiveIntegerField('Ordem', default=0)
    publicada = models.BooleanField('Publicada', default=False, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pergunta frequente'
        verbose_name_plural = 'Perguntas frequentes'
        ordering = ('idioma', 'categoria', 'ordem', 'id')
        constraints = [models.UniqueConstraint(fields=('idioma', 'categoria', 'pergunta'), name='core_faq_idioma_categoria_pergunta_unica')]

    def __str__(self):
        return f'[{self.get_idioma_display()}] {self.pergunta}'


class EventoNotificacaoOutbox(models.Model):
    """Evento de negócio aguardando publicação no serviço de notificações."""
    event_id = models.CharField('ID do evento', max_length=120, unique=True)
    event_type = models.CharField('Tipo do evento', max_length=80, db_index=True)
    payload = models.JSONField('Dados do evento', default=dict)
    occurred_at = models.DateTimeField('Ocorrido em')
    tentativas = models.PositiveIntegerField('Tentativas', default=0)
    publicado_em = models.DateTimeField('Publicado em', null=True, blank=True)
    ultimo_erro = models.TextField('Último erro', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Evento de notificação pendente'
        verbose_name_plural = 'Eventos de notificação pendentes'
        ordering = ('publicado_em', 'criado_em')
        indexes = [models.Index(fields=('publicado_em', 'criado_em'), name='core_outbox_pending_idx')]

    def __str__(self):
        estado = 'publicado' if self.publicado_em else 'pendente'
        return f'{self.event_type} — {self.event_id} ({estado})'
