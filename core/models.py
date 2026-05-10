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
    titulo = models.CharField("Título", max_length=200, blank=True, null=True)
    descricao = models.TextField("Descrição", blank=True, null=True)
    imagem_fundo = models.ImageField("Imagem de Fundo", upload_to="publicidades/")
    url_destino = models.URLField("URL de Destino", blank=True, null=True)
    texto_botao = models.CharField("Texto do Botão", max_length=50, default="Saiba Mais", blank=True)
    ativo = models.BooleanField("Ativo", default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Publicidade"
        verbose_name_plural = "Publicidades"
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo or f"Publicidade {self.id}"
