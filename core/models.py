from django.db import models


class Galeria(models.Model):
    imagem = models.ImageField("Imagem", upload_to="galeria/")
    link = models.URLField("Link", blank=True, null=True)  # opcional, p/ link do Instagram
    usuario = models.CharField("Usuário", max_length=100, blank=True, null=True)  # ex: @Edukangola
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Imagem da Galeria"
        verbose_name_plural = "Galeria de Imagens"
        ordering = ['-criado_em']

    def __str__(self):
        return self.usuario or f"Imagem {self.id}"
