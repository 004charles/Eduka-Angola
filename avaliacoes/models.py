from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.safestring import mark_safe

class AvaliacaoHibridaCentro(models.Model):
    """
    Calcula e armazena a pontuação de confiança de um Centro baseada em múltiplas métricas.
    """
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
    Registra feedback geral dos usuários sobre a plataforma Edukangola.
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

class Comentario(models.Model):
    """
    Avaliações de usuários para cursos.
    Suporta classificações, detecção automática de status e moderação.
    """
    ALUNO_STATUS_CHOICES = [
        ('INS', 'Inscrito'),
        ('COM', 'Concluído'),
        ('AND', 'Em Andamento'),
    ]
    
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='comentarios')
    curso = models.ForeignKey('cursos_app.Curso', on_delete=models.CASCADE, related_name='comentarios', null=True, blank=True)
    curso_video = models.ForeignKey('cursovideoapp.Curso_video', on_delete=models.CASCADE, related_name='comentarios', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='respostas_comunidade')
    
    comentario = models.TextField(_('Comentário'), max_length=1000)
    avaliacao = models.IntegerField(
        _('Avaliação'),
        choices=[(1, '1 Estrela'), (2, '2 Estrelas'), (3, '3 Estrelas'), 
                (4, '4 Estrelas'), (5, '5 Estrelas')],
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    status_aluno = models.CharField(
        _('Status do Aluno'),
        max_length=3,
        choices=ALUNO_STATUS_CHOICES,
        default='AND'
    )
    
    data_comentario = models.DateTimeField(_('Data de Comentário'), default=timezone.now)
    atualizado_em = models.DateTimeField(_('Atualizado em'), auto_now=True)
    aprovado = models.BooleanField(_('Aprovado'), default=True)
    resposta = models.TextField(_('Resposta'), blank=True, null=True, max_length=1000)
    resposta_data = models.DateTimeField(_('Data da Resposta'), blank=True, null=True)
    
    # Campos para moderar o conteúdo
    denuncias = models.PositiveIntegerField(_('Denúncias'), default=0)
    editado = models.BooleanField(_('Editado'), default=False)
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentários'
        ordering = ['-data_comentario']
    
    def __str__(self):
        obj_titulo = self.curso.titulo if self.curso else self.curso_video.titulo if self.curso_video else "N/A"
        return f"Avaliação de {self.aluno.nome} para {obj_titulo}"
    
    def save(self, *args, **kwargs):
        # Verificar se é um update
        if self.pk:
            try:
                original = Comentario.objects.get(pk=self.pk)
                if original.comentario != self.comentario or original.avaliacao != self.avaliacao:
                    self.editado = True
            except Comentario.DoesNotExist:
                pass
        
        # Definir status do aluno automaticamente
        if hasattr(self.aluno, 'inscricoes'):
            curso_obj = self.curso or self.curso_video
            if curso_obj:
                if self.curso:
                    inscricao = self.aluno.inscricoes.filter(curso=self.curso).first()
                else:
                    inscricao = self.curso_video.inscritos.filter(id=self.aluno.id).exists()
                
                if inscricao:
                    if self.curso and hasattr(inscricao, 'status'):
                        if inscricao.status == 'C':
                            self.status_aluno = 'COM'
                        elif inscricao.status == 'A':
                            self.status_aluno = 'AND'
                    else:
                        self.status_aluno = 'AND'
        
        super().save(*args, **kwargs)
    
    @property
    def get_estrelas(self):
        """Retorna HTML das estrelas"""
        estrelas = ''
        for i in range(1, 6):
            if i <= self.avaliacao:
                estrelas += '<i class="fa fa-star text-warning"></i>'
            else:
                estrelas += '<i class="fa fa-star-o text-muted"></i>'
        return mark_safe(estrelas)
    
    def denunciar(self):
        """Incrementa o contador de denúncias"""
        self.denuncias += 1
        if self.denuncias >= 3:
            self.aprovado = False
        self.save()
    
    def responder(self, resposta_texto):
        """Adiciona uma resposta ao comentário"""
        self.resposta = resposta_texto
        self.resposta_data = timezone.now()
        self.save()
