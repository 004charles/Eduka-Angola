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

    imagem_destaque = models.ImageField(upload_to='sobre_nos/', blank=True, null=True)  

    video_explicacao = models.FileField(
        upload_to='videos/',
        blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv'])]
    )  

    data_atualizacao = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.titulo
