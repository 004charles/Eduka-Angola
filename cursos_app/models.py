from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models import Avg, Count, Sum
from django.conf import settings
from django.urls import reverse
import uuid
from datetime import timedelta



def validate_video_size(value):
    filesize = value.size
    if filesize > 50 * 1024 * 1024:  # 50MB
        raise ValidationError(_("O tamanho máximo do vídeo não pode exceder 50MB."))
    return value


class Instrutor(models.Model):
    TIPO_CHOICES_ESPECIALIZACAO = [
        ('TECNOLOGIA_INFORMACAO', 'Tecnologia de Informação'),
        ('NEGOCIO', 'Negócio'),
        ('LINGUAS', 'Línguas'),
        ('ESPECIALIZADA', 'Especializada'),
        ('CIENCIAS', 'Ciências'),
        ('ARTES', 'Artes'),
        ('ENGENHARIA', 'Engenharia'),
        ('SAUDE', 'Saúde'),
        ('OUTRO', 'Outro'),
    ]
    
    usuario = models.OneToOneField(
        'usuarios.Usuario', 
        on_delete=models.CASCADE, 
        related_name='instrutor_profile',
        null=True, 
        blank=True
    )
    centro_de_formacao = models.ForeignKey(
        'gestoreduka.CentroDeFormacao', 
        on_delete=models.CASCADE, 
        related_name='instrutores',
        verbose_name='Centro de Formação',
        null=True,
        blank=True
    )
    filial = models.ForeignKey(
        'gestoreduka.Filial', 
        on_delete=models.CASCADE, 
        related_name='instrutores',
        verbose_name='Filial',
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100, validators=[MinLengthValidator(3)])
    titulo = models.CharField(max_length=100, blank=True, null=True, help_text="Ex: Especialista em Django, Mestre em Economia")
    biografia = models.TextField()
    foto = models.ImageField(upload_to='instrutores/', null=True, blank=True)
    email = models.EmailField(unique=True)
    area_especializacao = models.CharField(max_length=100, choices=TIPO_CHOICES_ESPECIALIZACAO)
    data_cadastro = models.DateField(default=timezone.now)
    ativo = models.BooleanField(default=True)

    # Campos consolidados do PerfilInstrutor
    foto_capa = models.ImageField(upload_to='instrutores/capas/', null=True, blank=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    total_alunos = models.PositiveIntegerField(default=0)
    total_cursos = models.PositiveIntegerField(default=0)
    total_avaliacoes = models.PositiveIntegerField(default=0)
    nota_media = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    class Meta:
        verbose_name = 'Instrutor'
        verbose_name_plural = 'Instrutores'
        ordering = ['nome']

    def __str__(self):
        if self.centro_de_formacao:
            return f"{self.nome} - {self.centro_de_formacao.nome}"
        return f"{self.nome} (Independente)"
    
    def get_especializacao_display(self):
        return dict(self.TIPO_CHOICES_ESPECIALIZACAO).get(self.area_especializacao, self.area_especializacao)
        
            
class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    imagem = models.ImageField(upload_to='categorias/', blank=True, null=True)
    mensagem_destaque = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Mensagem personalizada para exibir acima dos cursos desta categoria"
    )

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

class Curso(models.Model):
    NIVEL_CHOICES = [
        ('B', 'Básico'),
        ('I', 'Intermediário'),
        ('A', 'Avançado'),
    ]

    IDIOMA_CHOICES = [
        ('PT', 'Português'),
        ('EN', 'Inglês'),
        ('ES', 'Espanhol'),
        ('FR', 'Francês'),
        ('OUTRO', 'Outro'),
    ]

    MODALIDADE_CHOICES = [
        ('PRESENCIAL', 'Presencial'),
        ('ONLINE', 'Online'),
        ('HIBRIDO', 'Híbrido'),
    ]

    MOEDA_CHOICES = [
        ('AOA', _('Kwanza (AOA)')),
        ('EUR', _('Euro (EUR)')),
        ('USD', _('Dólar (USD)')),
    ]

    DURACAO_CHOICES = [
        ('1_SEMANA', '1 Semana'),
        ('2_SEMANAS', '2 Semanas'),
        ('3_SEMANAS', '3 Semanas'),
        ('1_MES', '1 Mês'),
        ('2_MESES', '2 Meses'),
        ('3_MESES', '3 Meses'),
        ('4_MESES', '4 Meses'),
        ('5_MESES', '5 Meses'),
        ('6_MESES', '6 Meses'),
        ('7_MESES', '7 Meses'),
        ('8_MESES', '8 Meses'),
        ('9_MESES', '9 Meses'),
        ('10_MESES', '10 Meses'),
        ('11_MESES', '11 Meses'),
        ('1_ANO', '1 Ano'),
    ]

    centro = models.ForeignKey('gestoreduka.CentroDeFormacao', on_delete=models.CASCADE, verbose_name=_('Centro de Formação'), related_name='cursos')
    filial = models.ForeignKey('gestoreduka.Filial', on_delete=models.CASCADE, verbose_name=_('Filial'), related_name='cursos', null=True, blank=True)
    titulo = models.CharField(_('Título do Curso'), max_length=200, validators=[MinLengthValidator(3)])
    descricao = models.TextField(_('Descrição Completa'))
    descricao_curta = models.CharField(_('Descrição Curta'), max_length=300, blank=True, help_text="Descrição resumida para cards e listagens")
    nivel = models.CharField(_('Nível'), max_length=1, choices=NIVEL_CHOICES, default='B', db_index=True)
    idioma = models.CharField(_('Idioma do Curso'), max_length=5, choices=IDIOMA_CHOICES, default='PT', db_index=True)
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, related_name='curso')
    certificado = models.BooleanField(_('Fornece Certificado'), default=True)
    instrutores = models.ManyToManyField('Instrutor', related_name='cursos', verbose_name=_('Instrutores'))
    carga_horaria = models.PositiveIntegerField(_('Carga Horária (horas)'))


    is_gratuito = models.BooleanField(
        _('Curso Gratuito'),
        default=False,
        db_index=True,
        help_text='Define se o curso é gratuito ou pago'
    )
    
    moeda = models.CharField(_('Moeda'), max_length=3, choices=MOEDA_CHOICES, default='AOA')
    
    preco = models.DecimalField(
        _('Preço do Curso'),
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        default=0
    )
    preco_inscricao = models.DecimalField(
        _('Taxa de Inscrição'),
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        default=0,
        help_text="Valor da taxa de inscrição (pode ser diferente do preço do curso)"
    )
    preco_promocional = models.DecimalField(
        _('Preço Promocional'),
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="Preço com desconto (opcional)"
    
    )

    data_inicio_promocao = models.DateTimeField(_('Início da Promoção'), null=True, blank=True)
    data_fim_promocao = models.DateTimeField(_('Fim da Promoção'), null=True, blank=True)
    
    vagas_minimas = models.PositiveIntegerField(_('Vagas Mínimas por Turma'), default=1, help_text="Número mínimo de alunos para uma turma acontecer")
    
    data_inicio_inscricoes = models.DateTimeField(_('Início das Inscrições'), default=timezone.now)
    data_fim_inscricoes = models.DateTimeField(_('Fim das Inscrições'), null=True, blank=True)
    
    modalidade = models.CharField(_('Modalidade'), max_length=10, choices=MODALIDADE_CHOICES, default='PRESENCIAL', db_index=True)
    duracao = models.CharField(_('Duração'), max_length=20, choices=DURACAO_CHOICES, blank=True, null=True)
    ativo = models.BooleanField(_('Curso Ativo'), default=True, db_index=True)
    publicado = models.BooleanField(_('Publicado'), default=False, db_index=True)
    imagem = models.ImageField(_('Imagem do Curso'), upload_to='cursos/', null=True, blank=True)
    requisitos = models.TextField(_('Pré-requisitos'), blank=True, null=True)
    objetivo_geral = models.TextField(_('Objetivo Geral'), blank=True)
    
    video_preview_file = models.FileField(
        _('Ficheiro de Vídeo de Prévia'),
        upload_to='cursos/previews/',
        null=True,
        blank=True,
        validators=[validate_video_size],
        help_text='Carregue um vídeo curto de apresentação (Máx: 50MB)'
    )

    video_previa_url = models.URLField(
    _('Vídeo de Prévia do Curso'),
    blank=True,
    null=True,
    help_text='Link do vídeo de apresentação (YouTube, Vimeo, etc.)'
)

    
    destaque = models.BooleanField(_('Curso em Destaque'), default=False, db_index=True)
    permite_parcelamento = models.BooleanField(_('Permite Parcelamento'), default=False)
    max_parcelas = models.PositiveIntegerField(_('Máximo de Parcelas'), default=1)
    slug = models.SlugField(_('Slug'), unique=True, blank=True, help_text="URL amigável (preenchido automaticamente)")
    tags = models.CharField(_('Tags'), max_length=500, blank=True, help_text="Palavras-chave separadas por vírgula")
    
    visualizacoes = models.PositiveIntegerField(_('Visualizações'), default=0, db_index=True)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True, db_index=True)
    data_atualizacao = models.DateTimeField(_('Data de Atualização'), auto_now=True)
    data_inicio = models.DateField(null=True, blank=True, db_index=True)


    def clean(self):
        if self.data_inicio_inscricoes and self.data_fim_inscricoes:
            if self.data_inicio_inscricoes > self.data_fim_inscricoes:
                raise ValidationError(_('A data de início das inscrições deve ser anterior à data de fim'))
        
        if self.preco_promocional and self.preco_promocional >= self.preco:
            raise ValidationError(_('O preço promocional deve ser menor que o preço normal'))

    def __str__(self):
        return f"{self.titulo} - {self.centro.nome}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.titulo}-{self.centro.nome}")
        
        original_slug = self.slug
        counter = 1
        while Curso.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{counter}"
            counter += 1
        
        novo = self.pk is None  
        curso_antigo = None
        if not novo:
            try:
                curso_antigo = Curso.objects.get(pk=self.pk)
            except Curso.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if self.publicado and (novo or (curso_antigo and not curso_antigo.publicado)):
            from .utils import notificar_seguidores  
            notificar_seguidores(self)

    def get_imagem_url(self):
        """Retorna a URL da imagem do curso ou um placeholder se não existir"""
        if self.imagem and hasattr(self.imagem, 'url'):
            try:
                # Verifica se o arquivo existe
                return self.imagem.url
            except (ValueError, AttributeError):
                pass
        # Retorna uma imagem placeholder usando um serviço de placeholder
        return f"https://via.placeholder.com/400x300/4A90E2/FFFFFF?text={self.titulo[:20]}"

            

    def atualizar_vagas_globais(self):
        for turma in self.turmas.all():
            turma.atualizar_vagas_turma()

    def redistribuir_alunos_turmas(self):
        if not self.turmas_abertas.exists():
            return False
        
        alunos_sem_turma = self.inscricoes.filter(
            status='A',
            turma_escolhida__isnull=True
        )
        
        for inscricao in alunos_sem_turma:
            turma_disponivel = self.turmas_abertas.filter(
                vagas_disponiveis__gt=0
            ).first()
            
            if turma_disponivel:
                inscricao.turma_escolhida = turma_disponivel
                inscricao.save()
                turma_disponivel.atualizar_vagas_turma()
        
        return True

    def verificar_viabilidade_turmas(self):
        turmas_abaixo_minimo = []
        
        for turma in self.turmas_abertas:
            if turma.vagas_ocupadas < self.vagas_minimas:
                turmas_abaixo_minimo.append(turma)
        
        return turmas_abaixo_minimo

    def fechar_turmas_insuficientes(self):
        turmas_insuficientes = self.verificar_viabilidade_turmas()
        
        for turma in turmas_insuficientes:
            turma.status = 'CANCELADA'
            turma.save()
            
            for inscricao in turma.inscricoes_turma.filter(inscricao__status='A'):
                try:
                    inscricao.inscricao.enviar_email_status(
                        f"Turma {turma.nome} foi cancelada por não atingir o número mínimo de alunos."
                    )
                except Exception:
                    pass
        
        return len(turmas_insuficientes)

    @property
    def preco_base_atual(self):
        """Retorna o preço base definido pelo centro, sem aplicação de taxas"""
        agora = timezone.now()
        if (self.preco_promocional and 
            self.data_inicio_promocao and 
            self.data_fim_promocao and
            self.data_inicio_promocao <= agora <= self.data_fim_promocao):
            return self.preco_promocional
        return self.preco

    @property
    def preco_atual(self):
        """Retorna o preço final exibido ao aluno (com Markup se aplicável)"""
        preco_base = self.preco_base_atual
        
        if hasattr(self.centro, 'metodo_precificacao') and self.centro.metodo_precificacao == 'MARKUP':
            from gestoreduka.models import ConfiguracaoPlataforma
            from decimal import Decimal
            try:
                conf = ConfiguracaoPlataforma.load()
                return preco_base * (Decimal('1.00') + (conf.taxa_markup / Decimal('100.00')))
            except Exception:
                pass
        return preco_base

    @property
    def valor_repasse(self):
        """Retorna o valor líquido que o Centro recebe (com Comissão descontada se aplicável)"""
        preco_base = self.preco_base_atual
        
        if hasattr(self.centro, 'metodo_precificacao') and self.centro.metodo_precificacao == 'COMISSAO':
            from gestoreduka.models import ConfiguracaoPlataforma
            from decimal import Decimal
            try:
                conf = ConfiguracaoPlataforma.load()
                return preco_base * (Decimal('1.00') - (conf.taxa_comissao / Decimal('100.00')))
            except Exception:
                pass
        return preco_base

    @property
    def em_promocao(self):
        agora = timezone.now()
        return (self.preco_promocional and 
                self.data_inicio_promocao and 
                self.data_fim_promocao and
                self.data_inicio_promocao <= agora <= self.data_fim_promocao)

    @property
    def percentual_desconto(self):
        if self.em_promocao and self.preco > 0:
            return ((self.preco - self.preco_promocional) / self.preco) * 100
        return 0

    @property
    def inscricoes_abertas(self):
        agora = timezone.now()
        if self.data_fim_inscricoes:
            return self.data_inicio_inscricoes <= agora <= self.data_fim_inscricoes
        return agora >= self.data_inicio_inscricoes

    @property
    def turmas_ativas(self):
        return self.turmas.filter(status__in=['ABERTA', 'EM_ANDAMENTO'])

    @property
    def turmas_abertas(self):
        return self.turmas.filter(status='ABERTA', vagas_disponiveis__gt=0)

    @property
    def total_vagas_totais(self):
        return self.turmas_ativas.aggregate(
            total=models.Sum('vagas_totais')
        )['total'] or 0

    @property
    def vagas_ocupadas(self):
        return self.inscricoes.filter(status='A').count()

    @property
    def total_vagas_disponiveis(self):
        return self.total_vagas_totais - self.vagas_ocupadas

    @property
    def lotado(self):
        return self.total_vagas_disponiveis <= 0

    @property
    def possui_turmas_ativas(self):
        return self.turmas_ativas.exists()

    @property
    def turnos_disponiveis(self):
        return self.turmas_ativas.values_list('turno', flat=True).distinct()

    def get_turmas_por_turno(self, turno):
        return self.turmas_ativas.filter(turno=turno)

    def get_proxima_turma(self):
        return self.turmas_ativas.order_by('data_inicio').first()

    def get_turma_menos_lotada(self):
        return self.turmas_abertas.order_by('-vagas_disponiveis').first()

    def incrementar_visualizacao(self):
        self.visualizacoes += 1
        self.save(update_fields=['visualizacoes'])

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('curso_detalhe', kwargs={'id': self.id})

    @property
    def get_media_avaliacoes(self):
        """Retorna a média das avaliações do curso (apenas comentários principais)"""
        avg = self.comentarios.filter(parent__isnull=True).aggregate(media=Avg('avaliacao'))['media']
        return round(avg, 1) if avg else 0.0

    @property
    def comentarios_principais(self):
        """Retorna apenas os comentários que não são respostas de outros"""
        return self.comentarios.filter(parent__isnull=True).order_by('-data_comentario')

    @property
    def get_distribuicao_avaliacoes(self):
        """Retorna a porcentagem de cada nota (1-5) para as barras de progresso"""
        total = self.comentarios.filter(parent__isnull=True).count()
        if total == 0:
            return {5:0, 4:0, 3:0, 2:0, 1:0}
        
        dist = {}
        for i in range(1, 6):
            contagem = self.comentarios.filter(parent__isnull=True, avaliacao=i).count()
            dist[i] = int((contagem / total) * 100)
        return dist
    
    @property
    def total_inscritos(self):
        """Retorna o total de alunos inscritos no curso"""
        return self.inscricoes.filter(status='A').count()



class TopicoCurso(models.Model):
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='topicos'
    )
    titulo = models.CharField(
        _('Tópico / O que será aprendido'),
        max_length=255
    )
    ordem = models.PositiveIntegerField(
        _('Ordem'),
        default=0
    )

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Tópico do Curso'
        verbose_name_plural = 'Tópicos do Curso'

    def __str__(self):
        return f"{self.ordem}. {self.titulo}"





class Turma(models.Model):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EM_ANDAMENTO', 'Em Andamento'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
    ]

    TURNO_CHOICES = [
        ('MANHA', 'Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE', 'Noite'),
        ('INTEGRAL', 'Integral'),
        ('SABADO', 'Sábado'),
        ('DOMINGO', 'Domingo'),
    ]

    DIAS_SEMANA_CHOICES = [
        ('SEG', 'Segunda'),
        ('TER', 'Terça'),
        ('QUA', 'Quarta'),
        ('QUI', 'Quinta'),
        ('SEX', 'Sexta'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]
    
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='turmas')
    nome = models.CharField(_('Nome da Turma'), max_length=100)
    codigo = models.CharField(_('Código da Turma'), max_length=20, unique=True)
    
    data_inicio = models.DateField(_('Data de Início'))
    data_fim = models.DateField(_('Data de Término'))
    
    turno = models.CharField(_('Turno'), max_length=10, choices=TURNO_CHOICES, default='MANHA')
    horario_inicio = models.TimeField(_('Horário de Início'))
    horario_fim = models.TimeField(_('Horário de Término'))
    dias_semana = models.CharField(_('Dias da Semana'), max_length=100, help_text="Ex: SEG,QUA,SEX ou TER,QUI")
    
    vagas_totais = models.PositiveIntegerField(_('Vagas Totais'))
    vagas_ocupadas = models.PositiveIntegerField(_('Vagas Ocupadas'), default=0)
    vagas_disponiveis = models.PositiveIntegerField(_('Vagas Disponíveis'), default=0)
    
    local = models.CharField(_('Local das Aulas'), max_length=200, blank=True)
    sala = models.CharField(_('Sala'), max_length=50, blank=True)
    
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='ABERTA', db_index=True)
    observacoes = models.TextField(_('Observações'), blank=True)
    
    instrutor_principal = models.ForeignKey(
        'Instrutor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Instrutor Principal')
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Turma')
        verbose_name_plural = _('Turmas')
        ordering = ['data_inicio', 'turno']
        unique_together = ['curso', 'codigo']

    def __str__(self):
        return f"{self.nome} - {self.curso.titulo} ({self.get_turno_display()})"

    def save(self, *args, **kwargs):
        self.vagas_disponiveis = self.vagas_totais - self.vagas_ocupadas
        
        if not self.codigo:
            base_codigo = f"T{self.curso.id}_{self.turno[:3]}_{timezone.now().strftime('%H%M%S')}"
            self.codigo = base_codigo.upper()
        
        super().save(*args, **kwargs)

    def atualizar_vagas_turma(self):
        self.vagas_ocupadas = self.inscricoes_turma.filter(inscricao__status='A').count()
        self.vagas_disponiveis = self.vagas_totais - self.vagas_ocupadas
        self.save(update_fields=['vagas_ocupadas', 'vagas_disponiveis'])

    @property
    def inscricoes_turma(self):
        return self.curso.inscricoes.filter(turma_escolhida=self)

    @property
    def alunos_confirmados(self):
        from usuarios.models import Aluno
        return Aluno.objects.filter(
            inscricoes__turma_escolhida=self,
            inscricoes__status='A'
        ).distinct()

    @property
    def percentual_ocupacao(self):
        if self.vagas_totais == 0:
            return 0
        return (self.vagas_ocupadas / self.vagas_totais) * 100

    @property
    def atingiu_minimo(self):
        return self.vagas_ocupadas >= self.curso.vagas_minimas

    @property
    def dias_semana_list(self):
        return self.dias_semana.split(',')

    @property
    def horario_formatado(self):
        return f"{self.horario_inicio.strftime('%H:%M')} - {self.horario_fim.strftime('%H:%M')}"

    @property
    def duracao_semanas(self):
        if self.data_inicio and self.data_fim:
            dias = (self.data_fim - self.data_inicio).days
            return max(1, dias // 7)
        return 0

    def pode_ser_excluida(self):
        return self.vagas_ocupadas == 0 and self.status == 'ABERTA'

    def fechar_inscricoes(self):
        if self.status == 'ABERTA':
            self.status = 'EM_ANDAMENTO'
            self.save()

    def reabrir_inscricoes(self):
        if self.status == 'EM_ANDAMENTO' and self.vagas_disponiveis > 0:
            self.status = 'ABERTA'
            self.save()

class Inscricao(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('A', 'Aceita'),
        ('N', 'Negada'),
        ('C', 'Cancelada'),
    ]

    TIPO_INSCRICAO_CHOICES = [
        ('ONLINE', 'Online'),
        ('PRESENCIAL', 'Presencial'),
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('TRANSFERENCIA', 'Transferência'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('DEPOSITO', 'Depósito'),
        ('SIMULADO', 'Pagamento Simulado'),  # Adicionado para simulação
        ('OUTRO', 'Outro'),
    ]

    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='inscricoes')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='inscricoes')
    turma_escolhida = models.ForeignKey(
        Turma,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Turma Escolhida'),
        related_name='inscricoes_turma'
    )
    
    data_inscricao = models.DateTimeField(_('Data de Inscrição'), default=timezone.now, db_index=True)
    status = models.CharField(_('Status'), max_length=1, choices=STATUS_CHOICES, default='P', db_index=True)
    tipo_inscricao = models.CharField(_('Tipo de Inscrição'), max_length=10, choices=TIPO_INSCRICAO_CHOICES, default='ONLINE', db_index=True)
    
    forma_pagamento = models.CharField(_('Forma de Pagamento'), max_length=20, choices=FORMA_PAGAMENTO_CHOICES, blank=True)
    valor_pago = models.DecimalField(_('Valor Pago'), max_digits=10, decimal_places=3, validators=[MinValueValidator(0)], null=True, blank=True)
    data_pagamento = models.DateTimeField(_('Data de Pagamento'), null=True, blank=True)
    comprovante_pagamento = models.FileField(_('Comprovante de Pagamento'), upload_to='comprovantes/', null=True, blank=True)
    
    # Campos para simulação de pagamento
    pagamento_simulado = models.BooleanField(_('Pagamento Simulado'), default=False)
    codigo_simulacao = models.CharField(_('Código da Simulação'), max_length=50, blank=True, null=True)
    data_simulacao = models.DateTimeField(_('Data da Simulação'), null=True, blank=True)
    
    observacoes = models.TextField(_('Observações'), blank=True)
    data_confirmacao = models.DateTimeField(_('Data de Confirmação'), null=True, blank=True)
    data_cancelamento = models.DateTimeField(_('Data de Cancelamento'), null=True, blank=True)

    def __str__(self):
        return f"{self.aluno.nome} → {self.curso.titulo} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        
        if not is_new:
            try:
                old_instance = Inscricao.objects.get(pk=self.pk)
                old_status = old_instance.status
            except Inscricao.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Sincronizar vagas se o status mudar para 'A' (Ativo) ou sair de 'A'
        if (self.status == 'A' and (is_new or old_status != 'A')) or \
           (old_status == 'A' and self.status != 'A'):
            self.curso.atualizar_vagas_globais()
            
            if self.turma_escolhida:
                self.turma_escolhida.atualizar_vagas_turma()
        
        # Registrar datas de status automaticamente
        if self.status == 'A' and not self.data_confirmacao:
            # Usar update para evitar chamar save() e causar recursão ou loops
            Inscricao.objects.filter(pk=self.pk).update(data_confirmacao=timezone.now())
        elif self.status == 'C' and not self.data_cancelamento:
            Inscricao.objects.filter(pk=self.pk).update(data_cancelamento=timezone.now())


    @property
    def em_turma_especifica(self):
        return self.turma_escolhida is not None

    @property
    def turma_atual(self):
        return self.turma_escolhida or self.curso.get_proxima_turma()

    @property
    def valor_devido(self):
        if self.valor_pago:
            return self.curso.preco_atual - self.valor_pago
        return self.curso.preco_atual

    @property
    def pagamento_completo(self):
        return self.valor_pago and self.valor_pago >= self.curso.preco_atual

    @property
    def pagamento_simulado_info(self):
        """Retorna informações sobre o pagamento simulado"""
        if self.pagamento_simulado:
            return {
                'simulado': True,
                'codigo': self.codigo_simulacao,
                'data': self.data_simulacao,
                'valor': self.valor_pago,
            }
        return {'simulado': False}

    def enviar_email_confirmacao(self, link_curso=None):
        from .utils import enviar_email_inscricao
        enviar_email_inscricao(self, tipo='pendente', link_curso=link_curso)

    def enviar_email_status(self, link_curso=None):
        from .utils import enviar_email_inscricao
        enviar_email_inscricao(self, tipo='status', link_curso=link_curso)

    class Meta:
        verbose_name = _('Inscrição')
        verbose_name_plural = _('Inscrições')
        unique_together = ('aluno', 'curso')
        
class Favorito(models.Model):
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='favoritos')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='favoritado_por')
    data_adicao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together = ('aluno', 'curso')  
        ordering = ['-data_adicao']

    def __str__(self):
        return f"{self.aluno.nome} - {self.curso.titulo}"



class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    titulo = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)
    descricao = models.TextField(blank=True)

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'

    def __str__(self):
        return f"{self.ordem}. {self.titulo}"
    
    
class Video(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='videos')
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    url = models.URLField(max_length=200, blank=True)
    arquivo = models.FileField(upload_to='cursos/videos/', blank=True, null=True)
    duracao = models.DurationField(blank=True, null=True)
    ordem = models.PositiveIntegerField(default=0)
    liberado = models.BooleanField(default=False)

    class Meta:
        ordering = ['ordem']  
        verbose_name = 'Vídeo'
        verbose_name_plural = 'Vídeos'

    def __str__(self):
        return self.titulo

    @property
    def fonte_video(self):
        return self.url if self.url else self.arquivo.url if self.arquivo else None
    
class MaterialApoio(models.Model):
    TIPO_CHOICES = [
        ('PDF', 'Documento PDF'),
        ('SLIDE', 'Apresentação de Slides'),
        ('PLANILHA', 'Planilha'),
        ('CODIGO', 'Código-fonte'),
        ('OUTRO', 'Outro'),
    ]

    curso = models.ForeignKey(
        Curso, 
        on_delete=models.CASCADE, 
        related_name='materiais_apoio'
    )
    titulo = models.CharField(max_length=100)
    arquivo = models.FileField(upload_to='cursos/materiais/')
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        default='PDF'
    )
    data_adicao = models.DateTimeField(default=timezone.now)
    disponivel = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Material de Apoio'
        verbose_name_plural = 'Materiais de Apoio'
        ordering = ['-data_adicao']

    def __str__(self):
        return f"{self.titulo} ({self.get_tipo_display()})"


class PreRequisitoCurso(models.Model):
    curso = models.ForeignKey(
        Curso, 
        on_delete=models.CASCADE, 
        related_name='pre_requisitos'
    )
    texto = models.CharField(_('Pré-requisito'), max_length=255)
    ordem = models.PositiveIntegerField(_('Ordem'), default=0)

    class Meta:
        ordering = ['ordem']
        verbose_name = 'Pré-requisito do Curso'
        verbose_name_plural = 'Pré-requisitos do Curso'

    def __str__(self):
        return self.texto


import uuid

class CertificadoCurso(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.OneToOneField('Inscricao', on_delete=models.CASCADE, related_name='certificado_emitido')
    data_emissao = models.DateTimeField(_('Data de Emissão'), auto_now_add=True)
    codigo_verificacao = models.CharField(_('Código de Verificação'), max_length=20, unique=True, blank=True)
    
    class Meta:
        verbose_name = _('Certificado de Curso')
        verbose_name_plural = _('Certificados de Cursos')
        
    def save(self, *args, **kwargs):
        if not self.codigo_verificacao:
            self.codigo_verificacao = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificado - {self.inscricao.aluno.nome} - {self.inscricao.curso.titulo}"
