from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify

class AreaEstagio(models.Model):
    nome = models.CharField(_('Nome da Área'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100, unique=True, blank=True)
    descricao = models.TextField(_('Descrição'), blank=True)
    icone = models.CharField(_('Ícone'), max_length=50, blank=True, null=True)
    ativa = models.BooleanField(_('Ativa'), default=True)
    
    class Meta:
        verbose_name = _('Área de Estágio')
        verbose_name_plural = _('Áreas de Estágio')
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

class Estagio(models.Model):
    TIPO_REMUNERACAO = [
        ('remunerado', 'Remunerado'),
        ('bolsa_auxilio', 'Bolsa Auxílio'),
        ('nao_remunerado', 'Não Remunerado'),
        ('beneficios', 'Apenas Benefícios'),
    ]
    
    MODALIDADE = [
        ('presencial', 'Presencial'),
        ('hibrido', 'Híbrido'),
        ('remoto', 'Remoto'),
    ]
    
    DURACAO = [
        (3, '3 Meses'),
        (4, '4 Meses'),
        (5, '5 Meses'),
        (6, '6 Meses'),
        (8, '8 Meses'),
        (12, '12 Meses'),
    ]
    
    # Informações básicas
    titulo = models.CharField(_('Título do Estágio'), max_length=200)
    slug = models.SlugField(_('Slug'), max_length=250, unique=True, blank=True)
    descricao = models.TextField(_('Descrição Completa'))
    resumo = models.TextField(_('Resumo'), max_length=200)
    
    # Relacionamentos - usando string reference
    centro_formacao = models.ForeignKey(
        'gestoreduka.CentroDeFormacao', 
        on_delete=models.CASCADE, 
        verbose_name=_('Centro de Formação'),
        related_name='estagios'
    )
    area = models.ForeignKey(
        'AreaEstagio',
        on_delete=models.SET_NULL,
        verbose_name=_('Área do Estágio'),
        null=True,
        blank=True
    )
    
    # Detalhes do estágio
    tipo_remuneracao = models.CharField(
        _('Tipo de Remuneração'), 
        max_length=20, 
        choices=TIPO_REMUNERACAO, 
        default='bolsa_auxilio'
    )
    valor_remuneracao = models.DecimalField(
        _('Valor da Remuneração'), 
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    beneficios = models.TextField(_('Benefícios Oferecidos'), blank=True)
    
    # Informações práticas
    modalidade = models.CharField(
        _('Modalidade'), 
        max_length=20, 
        choices=MODALIDADE, 
        default='presencial'
    )
    duracao_meses = models.IntegerField(_('Duração (meses)'), choices=DURACAO, default=6)
    carga_horaria_semanal = models.IntegerField(_('Carga Horária Semanal (horas)'), default=30)
    vagas_disponiveis = models.IntegerField(_('Vagas Disponíveis'), default=1)
    vagas_preenchidas = models.IntegerField(_('Vagas Preenchidas'), default=0)
    
    # Localização
    local_trabalho = models.CharField(_('Local de Trabalho'), max_length=255)
    cidade = models.CharField(_('Cidade'), max_length=100)
    provincia = models.CharField(_('Província'), max_length=100)
    
    # Requisitos
    requisitos = models.TextField(_('Requisitos'))
    competencias_desejadas = models.TextField(_('Competências Desejadas'), blank=True)
    
    # Datas importantes
    data_inicio = models.DateField(_('Data de Início'))
    data_fim = models.DateField(_('Data de Término'), null=True, blank=True)
    data_publicacao = models.DateTimeField(_('Data de Publicação'), auto_now_add=True)
    data_limite_inscricao = models.DateField(_('Data Limite para Inscrições'))
    
    # Status e visualização
    ativo = models.BooleanField(_('Ativo'), default=True)
    destaque = models.BooleanField(_('Em Deste'), default=False)
    visualizacoes = models.PositiveIntegerField(_('Visualizações'), default=0)
    
    # Imagens
    imagem_principal = models.ImageField(
        _('Imagem Principal'), 
        upload_to='estagios/imagens/', 
        blank=True, 
        null=True
    )
    
    class Meta:
        verbose_name = _('Estágio')
        verbose_name_plural = _('Estágios')
        ordering = ['-data_publicacao', '-destaque']
    
    def __str__(self):
        return f"{self.titulo} - {self.centro_formacao.nome}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.titulo}-{self.centro_formacao.nome}")
        super().save(*args, **kwargs)
    
    @property
    def vagas_restantes(self):
        return self.vagas_disponiveis - self.vagas_preenchidas
    
    @property
    def esta_aceitando_inscricoes(self):
        return (self.ativo and 
                self.vagas_restantes > 0 and 
                timezone.now().date() <= self.data_limite_inscricao)

class InscricaoEstagio(models.Model):
    STATUS_INSCRICAO = [
        ('pendente', 'Pendente'),
        ('analise', 'Em Análise'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('cancelada', 'Cancelada'),
    ]
    
    estagio = models.ForeignKey(
        'Estagio', 
        on_delete=models.CASCADE, 
        verbose_name=_('Estágio'),
        related_name='inscricoes'
    )
    aluno = models.ForeignKey(
        'usuarios.Aluno',  # String reference
        on_delete=models.CASCADE, 
        verbose_name=_('Aluno'),
        related_name='inscricoes_estagio'
    )
    curriculo = models.FileField(
        _('Currículo'), 
        upload_to='estagios/curriculos/',
        blank=True,
        null=True
    )
    carta_motivacao = models.TextField(_('Carta de Motivação'))
    data_inscricao = models.DateTimeField(_('Data de Inscrição'), auto_now_add=True)
    status = models.CharField(
        _('Status da Inscrição'), 
        max_length=20, 
        choices=STATUS_INSCRICAO, 
        default='pendente'
    )
    observacoes = models.TextField(_('Observações'), blank=True)
    
    class Meta:
        verbose_name = _('Inscrição de Estágio')
        verbose_name_plural = _('Inscrições de Estágio')
        unique_together = ['estagio', 'aluno']
        ordering = ['-data_inscricao']
    
    def __str__(self):
        return f"Inscrição de {self.aluno.nome} para {self.estagio.titulo}"

class BeneficioEstagio(models.Model):
    estagio = models.ForeignKey(
        'Estagio',
        on_delete=models.CASCADE,
        verbose_name=_('Estágio'),
        related_name='beneficios_estagio'
    )
    nome = models.CharField(_('Nome do Benefício'), max_length=100)
    descricao = models.TextField(_('Descrição'), blank=True)
    icone = models.CharField(_('Ícone'), max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = _('Benefício do Estágio')
        verbose_name_plural = _('Benefícios do Estágio')
    
    def __str__(self):
        return self.nome