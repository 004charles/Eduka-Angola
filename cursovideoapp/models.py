from django.db import models
from django.utils.text import slugify
from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import os
from datetime import timedelta
from usuarios.models import Aluno

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class Curso_video(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    instrutor = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="cursos")
    data_publicacao = models.DateTimeField(auto_now_add=True)
    capa = models.ImageField(upload_to="cursos/capas/", blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)
    inscritos = models.ManyToManyField('usuarios.Aluno', related_name='cursos_inscritos', blank=True)
    destaque = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)

    def total_inscritos(self):
        return self.inscritos.count()
    
    def duracao_total(self):
        total_segundos = sum(aula.duracao_segundos for aula in self.aulas.all() if aula.duracao_segundos)
        horas, remainder = divmod(total_segundos, 3600)
        minutos, segundos = divmod(remainder, 60)
        
        if horas > 0:
            return f"{int(horas)}h {int(minutos)}min"
        return f"{int(minutos)}min"
    
    def total_visualizacoes(self):
        return sum(aula.visualizacoes for aula in self.aulas.all())
    
    def __str__(self):
        return self.titulo

class Aula(models.Model):
    curso = models.ForeignKey(Curso_video, on_delete=models.CASCADE, related_name="aulas", null=True)
    titulo = models.CharField(max_length=200)
    video = models.FileField(
        upload_to="cursos/aulas/", 
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov', 'mkv'])]
    )
    ordem = models.PositiveIntegerField(default=0)
    duracao_segundos = models.PositiveIntegerField(default=0, help_text="Duração em segundos")
    visualizacoes = models.PositiveIntegerField(default=0)
    requer_conclusao_anterior = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["ordem"]

    def duracao_formatada(self):
        if self.duracao_segundos:
            minutos, segundos = divmod(self.duracao_segundos, 60)
            horas, minutos = divmod(minutos, 60)
            
            if horas > 0:
                return f"{int(horas)}:{int(minutos):02d}:{int(segundos):02d}"
            return f"{int(minutos)}:{int(segundos):02d}"
        return "0:00"
    
    def __str__(self):
        return f"{self.ordem} - {self.titulo}"

class ProgressoAula(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, null=True)
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, null=True)
    concluida = models.BooleanField(default=False)
    tempo_assistido = models.PositiveIntegerField(default=0, help_text="Tempo assistido em segundos")
    data_ultimo_acesso = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['aluno', 'aula']
    
    def progresso_percentual(self):
        if self.aula.duracao_segundos > 0:
            return min(100, int((self.tempo_assistido / self.aula.duracao_segundos) * 100))
        return 0



class FavoritoCursoVideo(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='favoritos_video')
    curso = models.ForeignKey(Curso_video, on_delete=models.CASCADE, related_name='favoritado_por')
    data_adicao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favorito Curso Vídeo'
        verbose_name_plural = 'Favoritos Cursos Vídeo'
        unique_together = ('aluno', 'curso')
        ordering = ['-data_adicao']

    def __str__(self):
        return f"{self.aluno.nome} - {self.curso.titulo}"
