from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class AvaliacaoHibridaCentro(models.Model):
    centro = models.OneToOneField(
        'gestoreduka.CentroDeFormacao', 
        on_delete=models.CASCADE, 
        related_name='avaliacao_hibrida'
    )
    
    # Métricas Base
    media_alunos = models.FloatField(_('Média de Avaliações (Alunos)'), default=0.0)
    taxa_conclusao = models.FloatField(_('Taxa de Conclusão (%)'), default=0.0)
    frequencia_media = models.FloatField(_('Frequência Média (%)'), default=0.0)
    
    # Score Calculado (IA/Estatístico)
    score_confianca = models.FloatField(_('Score de Confiança'), default=0.0)
    
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    
    def calcular_score_final(self):
        """
        Peso: 
        40% Avaliação dos alunos
        40% Taxa de conclusão
        20% Frequência/Engajamento
        """
        # Normalizando média_alunos (1-5) para 0-100
        score_alunos = (self.media_alunos / 5.0) * 100
        
        score_final = (score_alunos * 0.4) + (self.taxa_conclusao * 0.4) + (self.frequencia_media * 0.2)
        self.score_confianca = score_final
        self.save()
        return score_final

    class Meta:
        verbose_name = _('Avaliação Híbrida de Centro')
        verbose_name_plural = _('Avaliações Híbridas de Centros')

class FeedbackExterno(models.Model):
    """
    Feedback textual moderado, como solicitado.
    """
    centro = models.ForeignKey('gestoreduka.CentroDeFormacao', on_delete=models.CASCADE)
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE)
    curso = models.ForeignKey('cursos_app.Curso', on_delete=models.SET_NULL, null=True, blank=True)
    
    comentario = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    moderado = models.BooleanField(default=False)
    util = models.PositiveIntegerField(default=0)  # "Isso ajudou?"

    class Meta:
        verbose_name = _('Feedback Moderado')
        verbose_name_plural = _('Feedbacks Moderados')
