from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

class Skill(models.Model):
    DEMAND_CHOICES = [
        ('BAIXA', _('Baixa')),
        ('MEDIA', _('Média')),
        ('ALTA', _('Alta')),
        ('CRITICA', _('Crítica')),
    ]

    CATEGORIA_CHOICES = [
        ('TECNOLOGIA', _('Tecnologia')),
        ('NEGOCIOS', _('Negócios')),
        ('SAUDE', _('Saúde')),
        ('ENGENHARIA', _('Engenharia')),
        ('ARTES', _('Artes')),
        ('OUTRO', _('Outro')),
    ]

    nome = models.CharField(_('Nome da Competência'), max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField(_('Descrição'), blank=True)
    categoria = models.CharField(_('Categoria'), max_length=20, choices=CATEGORIA_CHOICES, default='TECNOLOGIA')
    nivel_demanda = models.CharField(_('Nível de Demanda no Mercado'), max_length=10, choices=DEMAND_CHOICES, default='MEDIA')
    
    # Relação com cursos: Quais cursos ensinam esta skill
    cursos_relacionados = models.ManyToManyField('cursos_app.Curso', related_name='skills', blank=True)
    cursos_video_relacionados = models.ManyToManyField('cursovideoapp.Curso_video', related_name='skills', blank=True)
    
    icone = models.CharField(_('Ícone (Feather)'), max_length=50, default='feather-activity')

    class Meta:
        verbose_name = _('Competência')
        verbose_name_plural = _('Competências')
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

class Empresa(models.Model):
    nome = models.CharField(_('Nome da Empresa'), max_length=150)
    nif = models.CharField(_('NIF'), max_length=20, unique=True)
    setor = models.CharField(_('Setor de Atuação'), max_length=100)
    website = models.URLField(_('Website'), blank=True, null=True)
    descricao = models.TextField(_('Sobre a Empresa'))
    logo = models.ImageField(_('Logo'), upload_to='empresas/logos/', blank=True, null=True)
    email_contato = models.EmailField(_('E-mail de Contato'))
    
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Empresa Parceira')
        verbose_name_plural = _('Empresas Parceiras')

    def __str__(self):
        return self.nome

class Vaga(models.Model):
    TIPO_VAGA = [
        ('FULLTIME', _('Tempo Inteiro')),
        ('PARTTIME', _('Meio Período')),
        ('CONTRATO', _('Contrato / Projecto')),
        ('ESTAGIO', _('Estágio')),
        ('REMOTO', _('Remoto')),
    ]

    STATUS_VAGA = [
        ('ABERTA', _('Aberta')),
        ('FECHADA', _('Fechada')),
        ('SUSPENSA', _('Suspensa')),
    ]

    titulo = models.CharField(_('Título da Vaga'), max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='vagas')
    descricao = models.TextField(_('Descrição da Vaga'))
    
    # Competências exigidas para esta vaga
    competencias_exigidas = models.ManyToManyField(Skill, related_name='vagas', verbose_name=_('Competências Exigidas'))
    
    salario_min = models.DecimalField(_('Salário Mínimo (Opcional)'), max_digits=12, decimal_places=2, null=True, blank=True)
    salario_max = models.DecimalField(_('Salário Máximo (Opcional)'), max_digits=12, decimal_places=2, null=True, blank=True)
    
    localizacao = models.CharField(_('Localização'), max_length=150, help_text="Ex: Luanda, Talatona")
    tipo = models.CharField(_('Tipo de Vaga'), max_length=10, choices=TIPO_VAGA, default='FULLTIME')
    
    data_publicacao = models.DateTimeField(auto_now_add=True)
    data_limite = models.DateField(_('Data Limite (Opcional)'), null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_VAGA, default='ABERTA')
    destaque = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Vaga de Emprego')
        verbose_name_plural = _('Vagas de Emprego')
        ordering = ['-data_publicacao']

    def __str__(self):
        return f"{self.titulo} - {self.empresa.nome}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.titulo}-{self.empresa.nome}")
        super().save(*args, **kwargs)

class CandidaturaVaga(models.Model):
    vaga = models.ForeignKey(Vaga, on_delete=models.CASCADE, related_name='candidaturas')
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='minhas_candidaturas')
    data_candidatura = models.DateTimeField(auto_now_add=True)
    curriculo_atualizado = models.FileField(upload_to='vagas/curriculos/', blank=True, null=True)
    mensagem = models.TextField(_('Mensagem para a Empresa (Opcional)'), blank=True)
    
    status = models.CharField(max_length=20, default='PENDENTE', choices=[
        ('PENDENTE', _('Pendente')),
        ('ENTREVISTA', _('Entrevista')),
        ('ACEITE', _('Aceite')),
        ('REJEITADA', _('Rejeitada')),
    ])

    class Meta:
        unique_together = ('vaga', 'aluno')
        verbose_name = _('Candidatura')
        verbose_name_plural = _('Candidaturas')

    def __str__(self):
        return f"{self.aluno.nome} -> {self.vaga.titulo}"

class AlunoSkill(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='minhas_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='alunos_com_esta_skill')
    data_aquisicao = models.DateTimeField(auto_now_add=True)
    comprovada = models.BooleanField(default=False, help_text="Se a skill foi comprovada por conclusão de curso")

    class Meta:
        unique_together = ('aluno', 'skill')
        verbose_name = _('Competência do Aluno')
        verbose_name_plural = _('Competências dos Alunos')

    def __str__(self):
        return f"{self.aluno.nome} - {self.skill.nome}"
