from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class HistoricoNavegacao(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='navegacao')
    url = models.CharField(max_length=255)
    modulo = models.CharField(max_length=50, blank=True)  # ex: 'cursos', 'blog', 'centros'
    data_acesso = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = _('Histórico de Navegação')
        verbose_name_plural = _('Históricos de Navegação')
        ordering = ['-data_acesso']

class VisualizacaoInteligente(models.Model):
    TIPO_CHOICES = [
        ('CURSO_PRESENCIAL', 'Curso Presencial'),
        ('CURSO_VIDEO', 'Curso de Vídeo'),
        ('CENTRO', 'Centro de Formação'),
    ]
    
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='visualizacoes_ia')
    item_id = models.PositiveIntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    categoria = models.ForeignKey('cursos_app.Categoria', on_delete=models.SET_NULL, null=True, blank=True)
    
    data_visualizacao = models.DateTimeField(default=timezone.now)
    duracao_segundos = models.PositiveIntegerField(default=0)  # Tempo de permanência na página

    class Meta:
        verbose_name = _('Visualização Inteligente')
        verbose_name_plural = _('Visualizações Inteligentes')

class PontuacaoInteresse(models.Model):
    """
    Score calculado para determinar o que recomendar.
    Pode ser atualizado por um comando de gerenciamento periódico.
    """
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='interesses')
    categoria = models.ForeignKey('cursos_app.Categoria', on_delete=models.CASCADE)
    peso = models.FloatField(default=0.0)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['aluno', 'categoria']
        verbose_name = _('Pontuação de Interesse')
        verbose_name_plural = _('Pontuações de Interesses')
