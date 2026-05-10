from django.db import models
from django.conf import settings
from usuarios.models import Aluno
from cursos_app.models import Curso

class Patrocinador(models.Model):
    TIPO_CHOICES = (
        ('EMPRESA', 'Empresa'),
        ('ESTADO', 'Estado/Governo'),
        ('ONG', 'ONG/Fundação'),
        ('INDIVIDUAL', 'Individual'),
    )
    
    nome = models.CharField("Nome da Instituição", max_length=200)
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES, default='EMPRESA')
    logo = models.ImageField("Logo", upload_to='sponsors/', blank=True, null=True)
    descricao = models.TextField("Descrição da Missão Social", blank=True)
    website = models.URLField("Website", blank=True, null=True)
    ativo = models.BooleanField(default=True)
    data_parceria = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Patrocinador"
        verbose_name_plural = "Patrocinadores"

    def __str__(self):
        return self.nome

class Bolsa(models.Model):
    STATUS_CHOICES = (
        ('ATIVA', 'Ativa'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
        ('SUSPENSA', 'Suspensa'),
    )

    patrocinador = models.ForeignKey(Patrocinador, on_delete=models.CASCADE, related_name='bolsas_concedidas')
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='bolsas')
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, null=True, related_name='bolsas_vinculadas')
    porcentagem = models.DecimalField("Porcentagem da Bolsa", max_digits=5, decimal_places=2, default=100.00)
    data_inicio = models.DateField("Data de Início")
    data_fim = models.DateField("Data de Término", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVA')
    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Bolsa de Estudo"
        verbose_name_plural = "Bolsas de Estudo"

    def __str__(self):
        return f"Bolsa {self.patrocinador} - {self.aluno}"

class CandidaturaBolsa(models.Model):
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente'),
        ('ANALISE', 'Em Análise'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
    )

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='candidaturas_bolsa')
    curso_pretendido = models.ForeignKey(Curso, on_delete=models.CASCADE)
    justificativa = models.TextField("Por que você precisa desta bolsa?")
    renda_familiar = models.DecimalField("Renda Familiar Estimada", max_digits=12, decimal_places=2, blank=True, null=True)
    documento_comprovativo = models.FileField(upload_to='bolsas/comprovantes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    data_candidatura = models.DateTimeField(auto_now_add=True)
    feedback_admin = models.TextField("Feedback da Administração", blank=True)

    class Meta:
        verbose_name = "Candidatura à Bolsa"
        verbose_name_plural = "Candidaturas às Bolsas"
        ordering = ['-data_candidatura']

    def __str__(self):
        return f"Candidatura de {self.aluno} para {self.curso_pretendido}"
