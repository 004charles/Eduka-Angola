from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.upload_validators import validate_image_file
from django.conf import settings
import uuid


from django.core.exceptions import ImproperlyConfigured
try:
    from django.contrib.gis.db import models as gis_models
    from django.contrib.gis.geos import Point
    HAS_GEODJANGO = True
except (OSError, ImportError, ImproperlyConfigured) as e:
    print(f"GeoDjango não disponível, usando modelos regulares: {e}")
    from django.db import models as gis_models
    HAS_GEODJANGO = False

from django.utils.translation import gettext_lazy as _





from django.utils.text import slugify
from django.contrib.auth.hashers import make_password, check_password

class ConfiguracaoPlataforma(models.Model):
    """
    Configurações globais da plataforma, como taxas e comissões.
    Implementado como Singleton (apenas um registo ativo).
    Permite alterar dinamicamente a comissão no Painel de Administração.
    """
    taxa_comissao = models.DecimalField(
        _('Comissão Padrão de Inscrição em Cursos (%)'), 
        max_digits=5, 
        decimal_places=2, 
        default=15.00,
        help_text=_('Percentagem retida pelo EdukAngola nas inscrições de cursos presenciais/centros. Ex: 15.00, 8.00 ou 5.00.')
    )
    taxa_comissao_ead = models.DecimalField(
        _('Comissão em Cursos Online EAD (%)'), 
        max_digits=5, 
        decimal_places=2, 
        default=20.00,
        help_text=_('Percentagem da plataforma em vendas de vídeo-cursos gravados.')
    )
    taxa_gestao_bolsas = models.DecimalField(
        _('Taxa de Gestão do Fundo de Bolsas (%)'), 
        max_digits=5, 
        decimal_places=2, 
        default=10.00,
        help_text=_('Taxa retida na alocação de fundos de patrocínio corporativo.')
    )
    taxa_markup = models.DecimalField(_('Taxa de Markup Padrão (%)'), max_digits=5, decimal_places=2, default=20.00)
    data_atualizacao = models.DateTimeField(_('Última Atualização'), auto_now=True)

    class Meta:
        verbose_name = _('Configuração de Taxas e Comissões')
        verbose_name_plural = _('Configurações de Taxas e Comissões')

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'taxa_comissao': 15.00,
                'taxa_comissao_ead': 20.00,
                'taxa_gestao_bolsas': 10.00,
                'taxa_markup': 20.00
            }
        )
        return obj

    def __str__(self):
        return f"Configuração Global (Comissão Atual: {self.taxa_comissao}%)"


class ModuloPublico(models.Model):
    """Funcionalidade React que a equipa Edukangola pode mostrar ou ocultar no menu público."""

    BOLSAS = 'BOLSAS'
    ESCOLAS = 'ESCOLAS'
    ESTAGIOS = 'ESTAGIOS'
    CHAVE_CHOICES = [
        (BOLSAS, _('Bolsas de estudo')),
        (ESCOLAS, _('Escolas')),
        (ESTAGIOS, _('Estágios')),
    ]
    CATALOGO_REACT = {
        BOLSAS: {
            'titulo': 'Bolsas',
            'descricao': 'Candidaturas a bolsas e apoios de formação.',
            'rota': '/bolsas',
            'menu': 'Bolsas',
        },
        ESCOLAS: {
            'titulo': 'Escolas',
            'descricao': 'Descubra escolas e cursos do ensino geral e técnico.',
            'rota': '/escolas',
            'menu': 'Escolas',
        },
        ESTAGIOS: {
            'titulo': 'Estágios',
            'descricao': 'Encontre vagas de estágio e candidate-se pela Edukangola.',
            'rota': '/estagios',
            'menu': 'Estágios',
        },
    }

    chave = models.CharField(_('Módulo'), max_length=40, choices=CHAVE_CHOICES, unique=True)
    ativo = models.BooleanField(_('Visível e disponível no site'), default=False, db_index=True)
    ordem = models.PositiveSmallIntegerField(_('Ordem no menu'), default=100)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Módulo público')
        verbose_name_plural = _('Módulos públicos')
        ordering = ('ordem', 'chave')

    @property
    def metadados_react(self):
        return self.CATALOGO_REACT.get(self.chave, {})

    @classmethod
    def activos_para_react(cls):
        itens = []
        for modulo in cls.objects.filter(ativo=True).order_by('ordem', 'chave'):
            metadados = modulo.CATALOGO_REACT.get(modulo.chave)
            if metadados:
                itens.append({'chave': modulo.chave, **metadados})
        return itens

    def __str__(self):
        return self.get_chave_display()

class CategoriaCentro(models.Model):
    """Categorias globais para centros de formação (Tecnologia, Línguas, etc.)"""
    nome = models.CharField(_('Nome'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    icone = models.CharField(_('Ícone (FontAwesome/Feather)'), max_length=50, blank=True, help_text="Ex: feather-monitor")
    descricao = models.TextField(_('Descrição'), blank=True)
    ativa = models.BooleanField(_('Ativa'), default=True)

    class Meta:
        verbose_name = _('Categoria de Centro')
        verbose_name_plural = _('Categorias de Centros')
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class CentroDeFormacao(gis_models.Model):
    """
    Modelo principal para um Centro de Formação Profissional.
    Lida com endereço físico, coordenadas GIS e informações básicas de contato.
    Integrado com a autenticação centralizada do Usuario.
    """
    PAIS_CHOICES = [
        ('AO', _('Angola')),
        ('PT', _('Portugal')),
        ('BR', _('Brasil')),
        ('CV', _('Cabo Verde')),
        ('MZ', _('Moçambique')),
        ('ST', _('São Tomé e Príncipe')),
        ('GW', _('Guiné-Bissau')),
        ('TL', _('Timor-Leste')),
    ]

    usuario = models.OneToOneField('usuarios.Usuario', on_delete=models.CASCADE, related_name='centro_profile', null=True, blank=True)
    nome = models.CharField(_('Nome do Centro'), max_length=100, blank=True, null=True)
    nif = models.CharField(_('NIF'), max_length=18, unique=True, blank=True, null=True)
    pais = models.CharField(_('País'), max_length=2, choices=PAIS_CHOICES, default='AO')
    endereco = models.CharField(_('Endereço'), max_length=255, blank=True, null=True)
    cidade = models.CharField(_('Cidade'), max_length=100, blank=True, null=True)
    provincia = models.CharField(_('Província'), max_length=100, blank=True, null=True, help_text="Província (Angola) ou Distrito/Região (Portugal)")
    fuso_horario = models.CharField(_('Fuso Horário'), max_length=50, default='Africa/Luanda')
    
    # Novas Categorias
    categorias = models.ManyToManyField(CategoriaCentro, related_name='centros_principais', blank=True)
    
    METODO_PRECIFICACAO_CHOICES = [
        ('MARKUP', 'Markup (Acréscimo no valor do curso)'),
        ('COMISSAO', 'Comissão (Desconto no repasse)')
    ]
    metodo_precificacao = models.CharField(
        _('Método de Precificação'), 
        max_length=10, 
        choices=METODO_PRECIFICACAO_CHOICES, 
        default='MARKUP'
    )
    
    # Dados Bancários (Repasse)
    banco_nome = models.CharField(_('Nome do Banco'), max_length=100, blank=True, null=True, help_text="Ex: BAI, BFA, BIC...")
    banco_iban = models.CharField(_('IBAN'), max_length=50, blank=True, null=True, help_text="AO06.0000.0000...")
    banco_titular = models.CharField(_('Titular da Conta'), max_length=150, blank=True, null=True)
    
    # Só utiliza PointField se o GIS estiver nos INSTALLED_APPS e o banco de dados suportar (não for sqlite e for postgis)
    if (HAS_GEODJANGO and 
        'django.contrib.gis' in settings.INSTALLED_APPS and 
        'gis' in settings.DATABASES['default']['ENGINE']):
        
        localizacao = gis_models.PointField(
            _('Localização Geográfica'),
            geography=True,
            blank=True,
            null=True,
            srid=4326
        )
    else:
        # Fallback para SQLite/Não-GIS: Armazena como string ou ignora funcionalidade espacial
        localizacao = models.CharField(
            _('Localização (Fallback)'),
            max_length=100,
            blank=True,
            null=True,
            help_text="Usado como fallback quando PostGIS não está disponível"
        )
    
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('E-mail'), unique=True)
    site = models.URLField(_('Site'), blank=True, null=True)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True, db_index=True)
    ativo = models.BooleanField(_('Ativo'), default=True, db_index=True)
    # senha_hash is removed in favor of centralized auth

    def __str__(self):
        return self.nome or self.email

    @property
    def latitude(self):
        """Retorna a latitude de forma resiliente, suportando formato Point ou string."""
        if not self.localizacao:
            return None
        
        # Caso o dado seja uma string (fallback ou legado)
        if isinstance(self.localizacao, str):
            if ',' in self.localizacao:
                try:
                    return float(self.localizacao.split(',')[0])
                except (ValueError, IndexError):
                    return None
            return None
            
        # Caso o dado seja um objeto geográfico (GeoDjango)
        try:
            return self.localizacao.y
        except AttributeError:
            # Caso HAS_GEODJANGO seja True mas o objeto não tenha .y (raro)
            return None

    @property
    def longitude(self):
        """Retorna a longitude de forma resiliente, suportando formato Point ou string."""
        if not self.localizacao:
            return None
            
        # Caso o dado seja uma string
        if isinstance(self.localizacao, str):
            if ',' in self.localizacao:
                try:
                    return float(self.localizacao.split(',')[1])
                except (ValueError, IndexError):
                    return None
            return None
            
        # Caso o dado seja um objeto geográfico (GeoDjango)
        try:
            return self.localizacao.x
        except AttributeError:
            return None

    def set_localizacao(self, lat, lng):
        if HAS_GEODJANGO:
            from django.contrib.gis.geos import Point
            self.localizacao = Point(lng, lat, srid=4326)
        else:
            self.localizacao = f"{lat},{lng}"


    def get_endereco_completo(self):
        parts = [part for part in [self.endereco, self.cidade, self.provincia] if part]
        return ", ".join(parts) if parts else "Endereço não informado"

    # set_senha and verificar_senha are removed as they are now handled by Usuario

    class Meta:
        verbose_name = _('Centro de Formação')
        verbose_name_plural = _('Centros de Formação')


class ConfiguracaoFinanceiraCentro(models.Model):
    """Define a moeda comercial do centro sem activar cobrança sem validação Edukangola."""

    MOEDA_CHOICES = [
        ('AOA', _('Kwanza (AOA)')),
        ('EUR', _('Euro (EUR)')),
        ('USD', _('Dólar norte-americano (USD)')),
        ('MZN', _('Metical moçambicano (MZN)')),
        ('XOF', _('Franco CFA da África Ocidental (XOF)')),
        ('CVE', _('Escudo cabo-verdiano (CVE)')),
        ('BRL', _('Real brasileiro (BRL)')),
        ('STN', _('Dobra são-tomense (STN)')),
    ]
    GATEWAY_CHOICES = [
        ('PRONTU', _('Prontu')),
        ('PENDENTE', _('A definir pela Edukangola')),
    ]
    STATUS_CHOICES = [
        ('PENDENTE_VALIDACAO', _('A aguardar validação da Edukangola')),
        ('ACTIVA', _('Activa para cobrança')),
        ('SUSPENSA', _('Suspensa')),
    ]
    MOEDA_POR_PAIS = {
        'AO': 'AOA', 'PT': 'EUR', 'BR': 'BRL', 'CV': 'CVE',
        'MZ': 'MZN', 'ST': 'STN', 'GW': 'XOF', 'TL': 'USD',
    }

    centro = models.OneToOneField(CentroDeFormacao, on_delete=models.CASCADE, related_name='configuracao_financeira')
    moeda_apresentacao = models.CharField(_('Moeda apresentada ao aluno'), max_length=3, choices=MOEDA_CHOICES)
    moeda_cobranca = models.CharField(_('Moeda efectiva de cobrança'), max_length=3, choices=MOEDA_CHOICES)
    gateway = models.CharField(_('Gateway de cobrança'), max_length=20, choices=GATEWAY_CHOICES, default='PENDENTE')
    estado = models.CharField(_('Estado de activação'), max_length=24, choices=STATUS_CHOICES, default='PENDENTE_VALIDACAO', db_index=True)
    validado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='configuracoes_financeiras_validadas')
    validado_em = models.DateTimeField(null=True, blank=True)
    observacao_validacao = models.CharField(_('Observação da Edukangola'), max_length=300, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Configuração financeira do centro')
        verbose_name_plural = _('Configurações financeiras dos centros')

    @classmethod
    def moeda_padrao_para_pais(cls, pais):
        return cls.MOEDA_POR_PAIS.get(pais, 'AOA')

    @property
    def conta_de_liquidacao_configurada(self):
        return bool(self.centro.banco_nome and self.centro.banco_iban and self.centro.banco_titular)

    @property
    def esta_activa_para_cobranca(self):
        return self.estado == 'ACTIVA' and self.gateway != 'PENDENTE' and self.conta_de_liquidacao_configurada

    def clean(self):
        esperada = self.moeda_padrao_para_pais(self.centro.pais)
        if self.moeda_apresentacao != esperada or self.moeda_cobranca != esperada:
            raise ValidationError({'moeda_cobranca': _('A moeda seleccionada deve corresponder ao país de operação do centro.')})
        if self.estado == 'ACTIVA' and not self.conta_de_liquidacao_configurada:
            raise ValidationError(_('A conta de liquidação do centro deve estar completa antes da activação.'))
        if self.estado == 'ACTIVA' and self.gateway == 'PENDENTE':
            raise ValidationError({'gateway': _('Seleccione um gateway validado antes de activar a cobrança.')})
        if self.estado == 'ACTIVA' and self.centro.pais != 'AO':
            raise ValidationError(_('Ainda não existe um gateway internacional validado para este mercado.'))

    def __str__(self):
        return f'{self.centro.nome} — {self.moeda_cobranca} ({self.get_estado_display()})'


class CentroSeguimento(models.Model):
    """
    Relational model to track students following specific training centers.
    """
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='centros_seguidos', verbose_name=_('Aluno'))
    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, related_name='seguidores', verbose_name=_('Centro de Formação'))
    data_seguimento = models.DateTimeField(_('Data do Seguimento'), default=timezone.now)

    class Meta:
        unique_together = ('aluno', 'centro')
        verbose_name = _('Seguimento de Centro')
        verbose_name_plural = _('Seguimentos de Centros')

    def __str__(self):
        return f"{self.aluno.nome} segue {self.centro.nome}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            from gestoreduka.models import NotificacaoGestor
            NotificacaoGestor.objects.create(
                centro=self.centro,
                titulo=f"Novo Seguidor: {self.aluno.nome}",
                mensagem=f"O aluno {self.aluno.nome} começou a seguir o seu centro.",
                link="/gestoreduka/inscricoes/", # Pode ser o link para listar seguidores no futuro
                tipo='SEGUIMENTO'
            )


class ConviteCentro(models.Model):
    """
    Sistema de convites para registrar novos centros de formação.
    Gera um token único para conclusão segura do cadastro pelo gestor.
    """
    centro = models.OneToOneField(CentroDeFormacao, on_delete=models.CASCADE, related_name="convite")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    criado_em = models.DateTimeField(default=timezone.now)
    usado = models.BooleanField(default=False)

    def __str__(self):
        return f"Convite para {self.centro.email}"


class CandidaturaCentro(models.Model):
    """Pedido público de adesão de um centro antes da criação da conta de gestor."""
    STATUS_CHOICES = [
        ('PENDENTE', _('Pendente')),
        ('VERIFICADA', _('Email verificado')),
        ('CONCLUIDA', _('Cadastro concluído')),
        ('EXPIRADA', _('Expirada')),
        ('CANCELADA', _('Cancelada')),
    ]

    email = models.EmailField(_('E-mail'), db_index=True)
    nif = models.CharField(_('NIF'), max_length=18, db_index=True)
    codigo_hash = models.CharField(_('Código de verificação'), max_length=128)
    link_token = models.UUIDField(_('Token do link'), default=uuid.uuid4, unique=True, editable=False)
    link_criado_em = models.DateTimeField(_('Link criado em'), default=timezone.now)
    link_expira_em = models.DateTimeField(_('Link expira em'), default=timezone.now)
    link_usado = models.BooleanField(_('Link usado'), default=False)
    codigo_criado_em = models.DateTimeField(_('Código criado em'), default=timezone.now)
    codigo_expira_em = models.DateTimeField(_('Código expira em'))
    tentativas = models.PositiveSmallIntegerField(_('Tentativas'), default=0)
    verificado_em = models.DateTimeField(_('Verificado em'), null=True, blank=True)
    status = models.CharField(_('Estado'), max_length=12, choices=STATUS_CHOICES, default='PENDENTE', db_index=True)
    centro = models.OneToOneField(CentroDeFormacao, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidatura_publica')
    data_criacao = models.DateTimeField(_('Data de criação'), auto_now_add=True)
    data_atualizacao = models.DateTimeField(_('Data de atualização'), auto_now=True)

    class Meta:
        verbose_name = _('Candidatura de Centro')
        verbose_name_plural = _('Candidaturas de Centros')
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['email', 'nif', 'status']),
        ]

    def __str__(self):
        return f"{self.email} · {self.nif} · {self.get_status_display()}"


class Certificacao(models.Model):
    """
    Modelo para gerenciar certificações oferecidas por um centro de formação.
    """
    centro = models.ForeignKey(
        CentroDeFormacao, 
        on_delete=models.CASCADE,
        related_name='certificacoes'
    )
    nome = models.CharField(_('Nome da Certificação'), max_length=100)
    orgao_emissor = models.CharField(_('Órgão Emissor'), max_length=100)
    descricao = models.TextField(_('Descrição'), blank=True)
    logo = models.ImageField(_('Logo'), upload_to='certificacoes/', blank=True)

    class Meta:
        verbose_name = _('Certificação')
        verbose_name_plural = _('Certificações')

    def __str__(self):
        return f"{self.nome} ({self.orgao_emissor})"

class Diferencial(models.Model):
    """
    Modelo para destacar diferenciais e pontos fortes de um centro de formação.
    """
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='diferenciais'
    )
    titulo = models.CharField(_('Título'), max_length=100)
    descricao = models.TextField(_('Descrição'))
    icone = models.CharField(_('Ícone'), max_length=50, help_text="Ex: feather-check")

    class Meta:
        verbose_name = _('Diferencial')
        verbose_name_plural = _('Diferenciais')

    def __str__(self):
        return self.titulo

class AreaFormacao(models.Model):
    """
    Modelo para categorizar as áreas de formação profissional oferecidas por um centro.
    """
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='areas_formacao'
    )
    nome = models.CharField(_('Nome da Área'), max_length=100)
    descricao = models.TextField(_('Descrição'), blank=True)
    icone = models.CharField(_('Ícone'), max_length=50, blank=True)
    ordem = models.PositiveIntegerField(_('Ordem de Exibição'), default=0)

    class Meta:
        ordering = ['ordem']
        verbose_name = _('Área de Formação')
        verbose_name_plural = _('Áreas de Formação')

    def __str__(self):
        return self.nome

class Equipe(models.Model):
    """
    Modelo para gerenciar os membros da equipe de um centro de formação.
    """
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='equipe'
    )
    nome = models.CharField(_('Nome'), max_length=100)
    cargo = models.CharField(_('Cargo'), max_length=100)
    foto = models.ImageField(_('Foto'), upload_to='equipe/', blank=True)
    biografia = models.TextField(_('Biografia'))
    formacao = models.TextField(_('Formação Acadêmica'))
    experiencia = models.TextField(_('Experiência Profissional'))
    linkedin = models.URLField(_('LinkedIn'), blank=True)
    email = models.EmailField(_('E-mail'), blank=True)
    ordem = models.PositiveIntegerField(_('Ordem de Exibição'), default=0)

    class Meta:
        ordering = ['ordem']
        verbose_name = _('Membro da Equipe')
        verbose_name_plural = _('Membros da Equipe')

    def __str__(self):
        return f"{self.nome} ({self.cargo})"

class Recurso(models.Model):
    """
    Modelo para listar recursos e infraestrutura disponíveis em um centro de formação.
    """
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='recursos'
    )
    nome = models.CharField(_('Nome'), max_length=100)
    descricao = models.TextField(_('Descrição'))
    icone = models.CharField(_('Ícone'), max_length=50, blank=True)

    class Meta:
        verbose_name = _('Recurso')
        verbose_name_plural = _('Recursos')

    def __str__(self):
        return self.nome

class Depoimento(models.Model):
    """
    Modelo para armazenar depoimentos de alunos sobre o centro de formação ou sobre a plataforma.
    """
    TIPO_CHOICES = [
        ('PLATAFORMA', _('Sobre a Plataforma')),
        ('CENTRO', _('Sobre o Centro de Formação')),
    ]
    ORIGEM_CHOICES = [
        ('GESTOR', _('Adicionado por gestor')),
        ('ALUNO', _('Submetido por aluno')),
    ]

    tipo = models.CharField(_('Tipo'), max_length=20, choices=TIPO_CHOICES, default='PLATAFORMA')
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='depoimentos',
        null=True,
        blank=True
    )
    aluno = models.ForeignKey(
        'usuarios.Aluno',
        on_delete=models.SET_NULL,
        related_name='meus_depoimentos',
        null=True,
        blank=True
    )
    nome = models.CharField(_('Nome'), max_length=100)
    foto = models.ImageField(_('Foto'), upload_to='depoimentos/', blank=True)
    cargo = models.CharField(_('Cargo/Curso'), max_length=100, blank=True)
    texto = models.TextField(_('Depoimento'))
    nota = models.PositiveIntegerField(_('Nota (1-5)'), default=5)
    data = models.DateField(_('Data'), auto_now_add=True)
    origem = models.CharField(_('Origem'), max_length=12, choices=ORIGEM_CHOICES, default='GESTOR')
    consentimento_publico = models.BooleanField(_('Consentimento para publicação'), default=False)
    publicar_nome = models.BooleanField(_('Mostrar nome completo publicamente'), default=False)
    aprovado = models.BooleanField(_('Aprovado?'), default=False)

    class Meta:
        verbose_name = _('Depoimento')
        verbose_name_plural = _('Depoimentos')

    def __str__(self):
        return f"Depoimento de {self.nome}"

class Estatistica(models.Model):
    """
    Modelo para exibir estatísticas e métricas importantes de um centro de formação.
    """
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='estatisticas'
    )
    titulo = models.CharField(_('Título'), max_length=100)
    valor = models.CharField(_('Valor'), max_length=50)
    icone = models.CharField(_('Ícone'), max_length=50, help_text="Ex: feather-users")
    ordem = models.PositiveIntegerField(_('Ordem de Exibição'), default=0)

    class Meta:
        ordering = ['ordem']
        verbose_name = _('Estatística')
        verbose_name_plural = _('Estatísticas')

    def __str__(self):
        return f"{self.titulo}: {self.valor}"
    
class PerfilCentroDeFormacao(models.Model):
    """
    Informações de perfil estendidas para um Centro de Formação.
    Inclui branding, redes sociais, missão/visão e métricas.
    """
    centro = models.OneToOneField(CentroDeFormacao, on_delete=models.CASCADE, related_name='perfil')
    dono = models.CharField(max_length=100, null=True, blank=True, verbose_name='Dono do Centro')
    imagem = models.ImageField(
        _('Imagem ou Logo'), upload_to='centros/', null=True, blank=True,
        validators=[validate_image_file]
    )
    banner = models.ImageField(
        _('Imagem de Capa'), upload_to='centros/banners/', null=True, blank=True,
        validators=[validate_image_file]
    )
    video_apresentacao = models.FileField(_('Vídeo de Apresentação'), upload_to='centros_videos/', null=True, blank=True)
    descricao = models.TextField(_('Descrição'), null=True, blank=True)
    
    # Novos campos adicionados
    missao = models.TextField(_('Missão'), null=True, blank=True)
    visao = models.TextField(_('Visão'), null=True, blank=True)
    valores = models.TextField(_('Valores'), null=True, blank=True)
    ano_fundacao = models.PositiveIntegerField(_('Ano de Fundação'), null=True, blank=True)
    horario_funcionamento = models.TextField(_('Horário de Funcionamento'), null=True, blank=True)
    
    tipo = models.CharField(_('Tipo de Centro'), max_length=50, null=True, blank=True)
    modalidade = models.CharField(_('Modalidade'), max_length=20, choices=[
        ('Presencial', 'Presencial'), 
        ('Online', 'Online'), 
        ('Híbrido', 'Híbrido')
    ], default='Presencial')
    
    # Redes sociais
    facebook = models.URLField(_('Facebook'), blank=True, null=True)
    instagram = models.URLField(_('Instagram'), blank=True, null=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True, null=True)
    youtube = models.URLField(_('YouTube'), blank=True, null=True)
    tiktok = models.URLField(_('TikTok'), blank=True, null=True)
    whatsapp = models.CharField(_('WhatsApp'), max_length=20, blank=True, null=True)
    
    # Configurações
    destaque = models.BooleanField(_('Centro em Destaque'), default=False, db_index=True)
    verificado = models.BooleanField(_('Centro Verificado'), default=False, db_index=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    # Métricas (calculadas)
    total_seguidores = models.PositiveIntegerField(default=0)
    total_visualizacoes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Perfil de {self.centro.nome}"

    def atualizar_metricas(self):
        """Atualiza métricas automaticamente"""
        self.total_seguidores = self.centro.seguidores.count()
        self.total_visualizacoes = self.centro.visualizacoes.count()
        self.save(update_fields=['total_seguidores', 'total_visualizacoes'])

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('cursos_por_centro', kwargs={'centro_id': self.centro.id})


class Parceria(models.Model):
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='parcerias'
    )
    nome_empresa = models.CharField(_('Nome da Empresa/Instituição'), max_length=100)
    logo = models.ImageField(_('Logo'), upload_to='parcerias/', blank=True)
    website = models.URLField(_('Website'), blank=True)
    tipo_parceria = models.CharField(_('Tipo de Parceria'), max_length=100)
    descricao = models.TextField(_('Descrição'), blank=True)
    localizacao = models.CharField(_('Localização'), max_length=200, blank=True)
    contacto = models.CharField(_('Contacto'), max_length=50, blank=True)
    parceiro_externo = models.BooleanField(_('Parceiro Externo'), default=False, db_index=True)
    aceita_candidaturas = models.BooleanField(_('Aceita Candidaturas'), default=False)
    total_candidatos = models.PositiveIntegerField(_('Total de Candidatos'), default=0)
    ativa = models.BooleanField(_('Ativa'), default=True)

    class Meta:
        verbose_name = _('Parceria')
        verbose_name_plural = _('Parcerias')

    def __str__(self):
        return f"{self.nome_empresa} - {self.centro.nome}"


class CandidaturaExterna(models.Model):
    STATUS_CHOICES = [
        ('P', 'Pendente'),
        ('A', 'Aprovada'),
        ('R', 'Rejeitada'),
        ('C', 'Cancelada'),
    ]

    parceria = models.ForeignKey(
        Parceria,
        on_delete=models.CASCADE,
        related_name='candidaturas',
        verbose_name=_('Parceria')
    )
    aluno = models.ForeignKey(
        'usuarios.Aluno',
        on_delete=models.CASCADE,
        related_name='candidaturas_externas',
        verbose_name=_('Aluno')
    )
    curso = models.ForeignKey(
        'cursos_app.Curso',
        on_delete=models.CASCADE,
        related_name='candidaturas_externas',
        verbose_name=_('Curso')
    )
    nome_completo = models.CharField(_('Nome Completo'), max_length=150)
    email = models.EmailField(_('Email'))
    telefone = models.CharField(_('Telefone'), max_length=20)
    bi = models.CharField(_('BI/Nº Identificação'), max_length=30, blank=True)
    documento_inscricao = models.FileField(
        _('Documento de Inscrição'),
        upload_to='candidaturas/documentos/',
        blank=True, null=True
    )
    comprovativo_pagamento = models.FileField(
        _('Comprovativo de Pagamento'),
        upload_to='candidaturas/comprovantes/',
        blank=True, null=True
    )
    status = models.CharField(
        _('Status'),
        max_length=1,
        choices=STATUS_CHOICES,
        default='P',
        db_index=True
    )
    observacoes = models.TextField(_('Observações'), blank=True)
    resposta_admin = models.TextField(_('Resposta do Admin'), blank=True)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True, db_index=True)
    data_atualizacao = models.DateTimeField(_('Data de Atualização'), auto_now=True)

    class Meta:
        verbose_name = _('Candidatura Externa')
        verbose_name_plural = _('Candidaturas Externas')
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.nome_completo} → {self.curso.titulo} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.parceria.total_candidatos += 1
            self.parceria.save(update_fields=['total_candidatos'])

class Evento(models.Model):
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    titulo = models.CharField(_('Título'), max_length=200)
    descricao = models.TextField(_('Descrição'))
    data_inicio = models.DateTimeField(_('Data de Início'), db_index=True)
    data_fim = models.DateTimeField(_('Data de Fim'), blank=True, null=True)
    local = models.CharField(_('Local'), max_length=200)
    tipo = models.CharField(_('Tipo'), max_length=50, choices=[
        ('WORKSHOP', 'Workshop'),
        ('PALESTRA', 'Palestra'),
        ('FEIRA', 'Feira de Carreiras'),
        ('AULA_ABERTA', 'Aula Aberta'),
        ('OUTRO', 'Outro')
    ], db_index=True)
    link_inscricao = models.URLField(_('Link de Inscrição'), blank=True)
    imagem = models.ImageField(_('Imagem'), upload_to='eventos/', blank=True)
    destaque = models.BooleanField(_('Evento em Destaque'), default=False, db_index=True)

    class Meta:
        ordering = ['-data_inicio']
        verbose_name = _('Evento')
        verbose_name_plural = _('Eventos')

    def __str__(self):
        return self.titulo

class GaleriaImagem(models.Model):
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='galeria_imagens'  # MUDADO: de 'galeria' para 'galeria_imagens'
    )
    titulo = models.CharField(_('Título'), max_length=100, blank=True)
    descricao = models.TextField(_('Descrição'), blank=True, null=True)
    imagem = models.ImageField(_('Imagem'), upload_to='galeria/')
    categoria = models.CharField(_('Categoria'), max_length=50, choices=[
        ('SALAS', 'Salas de Aula'),
        ('LABS', 'Laboratórios'),
        ('EVENTOS', 'Eventos'),
        ('OUTRO', 'Outro')
    ], default='OUTRO')
    ordem = models.PositiveIntegerField(_('Ordem'), default=0)
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordem', '-data_upload']
        verbose_name = _('Imagem da Galeria')
        verbose_name_plural = _('Galeria de Imagens')

    def __str__(self):
        return self.titulo or f"Imagem {self.id}"

class VisualizacaoPerfil(models.Model):
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='visualizacoes'
    )
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    data_visualizacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Visualização de Perfil')
        verbose_name_plural = _('Visualizações de Perfil')

    def __str__(self):
        return f"Visualização de {self.centro.nome}"




class Filial(models.Model):
    centro_principal = models.ForeignKey(
        'CentroDeFormacao', 
        on_delete=models.CASCADE, 
        related_name='filiais',
        verbose_name=_('Centro Principal')
    )
    usuario = models.OneToOneField('usuarios.Usuario', on_delete=models.CASCADE, related_name='filial_profile', null=True, blank=True)
    nome = models.CharField(_('Nome da Filial'), max_length=100)
    endereco = models.CharField(_('Endereço'), max_length=255)
    telefone = models.CharField(_('Telefone'), max_length=20)
    email = models.EmailField(_('E-mail'), unique=True)
    whatsapp = models.CharField(_('WhatsApp'), max_length=20, blank=True, null=True)
    
    # Geolocalização
    latitude = models.DecimalField(_('Latitude'), max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(_('Longitude'), max_digits=22, decimal_places=16, blank=True, null=True)
    
    ativo = models.BooleanField(_('Ativa'), default=True)
    data_exclusao = models.DateTimeField(_('Data de Exclusão'), null=True, blank=True)
    categorias = models.ManyToManyField('CategoriaCentro', related_name='filiais_centros', blank=True, verbose_name=_('Categorias'))
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)

    class Meta:
        verbose_name = _('Filial')
        verbose_name_plural = _('Filiais')

    def __str__(self):
        return f"{self.nome} - Filial de {self.centro_principal.nome}"



class Conversa(models.Model):
    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, related_name='conversas')
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, related_name='conversas')
    data_criacao = models.DateTimeField(default=timezone.now)
    ultima_mensagem = models.DateTimeField(default=timezone.now)
    ativa = models.BooleanField(default=True)

    class Meta:
        unique_together = ['centro', 'aluno']
        ordering = ['-ultima_mensagem']

    def __str__(self):
        return f"Conversa: {self.centro.nome} - {self.aluno.nome}"

class Mensagem(models.Model):
    TIPO_CHOICES = [
        ('TEXTO', 'Texto'),
        ('ARQUIVO', 'Arquivo'),
        ('IMAGEM', 'Imagem'),
    ]

    conversa = models.ForeignKey(Conversa, on_delete=models.CASCADE, related_name='mensagens')
    remetente_aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, null=True, blank=True)
    remetente_centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, null=True, blank=True)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='TEXTO')
    arquivo = models.FileField(upload_to='chat/arquivos/', null=True, blank=True)
    data_envio = models.DateTimeField(default=timezone.now)
    lida = models.BooleanField(default=False)
    digitando = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and not self.digitando:
            # Atualizar timestamp da conversa
            self.conversa.ultima_mensagem = timezone.now()
            self.conversa.save(update_fields=['ultima_mensagem'])
            
            if self.remetente_centro:
                # Notificar o aluno se a mensagem for do centro
                from usuarios.models import NotificacaoAluno
                NotificacaoAluno.objects.create(
                    aluno=self.conversa.aluno,
                    titulo=f"Nova mensagem de {self.remetente_centro.nome}",
                    mensagem=self.mensagem[:100] + ("..." if len(self.mensagem) > 100 else ""),
                    link=f"/aluno/mensagens/?conversa={self.conversa_id}",
                    tipo='CHAT'
                )
            elif self.remetente_aluno:
                # Notificar o Gestor se a mensagem for do aluno
                from gestoreduka.models import NotificacaoGestor
                NotificacaoGestor.objects.create(
                    centro=self.conversa.centro,
                    titulo=f"Nova mensagem de {self.remetente_aluno.nome}",
                    mensagem=self.mensagem[:100] + ("..." if len(self.mensagem) > 100 else ""),
                    link=f"/gestoreduka/mensagens/?conversa={self.conversa_id}",
                    tipo='MENSAGEM'
                )

    def __str__(self):
        return f"Mensagem de {self.remetente} - {self.mensagem[:20]}"

    @property
    def remetente(self):
        if self.remetente_aluno:
            return self.remetente_aluno
        return self.remetente_centro

    def is_centro(self):
        return self.remetente_centro is not None


class AnuncioCentro(models.Model):
    """
    Anúncios/Novidades publicados pelos centros na sua dashboard para os seguidores.
    """
    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, related_name='anuncios')
    titulo = models.CharField(_('Título'), max_length=200)
    conteudo = models.TextField(_('Conteúdo'))
    imagem = models.ImageField(_('Imagem'), upload_to='anuncios/', null=True, blank=True)
    data_publicacao = models.DateTimeField(_('Data de Publicação'), auto_now_add=True)
    importante = models.BooleanField(_('Anúncio Urgente/Importante'), default=False)
    ativo = models.BooleanField(_('Ativo'), default=True)
    
    class Meta:
        ordering = ['-data_publicacao']
        verbose_name = _('Anúncio do Centro')
        verbose_name_plural = _('Anúncios dos Centros')

    def __str__(self):
        return f"{self.titulo} - {self.centro.nome}"


class NotificacaoGestor(models.Model):
    """Notificações destinadas aos gestores dos centros de formação"""
    TIPO_CHOICES = [
        ('COMENTARIO', _('Novo Comentário/Dúvida')),
        ('INSCRICAO', _('Nova Inscrição')),
        ('PAGAMENTO', _('Confirmação de Pagamento')),
        ('SISTEMA', _('Mensagem do Sistema')),
        ('MENSAGEM', _('Nova Mensagem')),
        ('SEGUIMENTO', _('Novo Seguidor')),
    ]

    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, related_name='notificacoes_gestor')
    titulo = models.CharField(_('Título'), max_length=150)
    mensagem = models.TextField(_('Mensagem'))
    link = models.CharField(_('Link (opcional)'), max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='SISTEMA')
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Notificação do Gestor'
        verbose_name_plural = 'Notificações dos Gestores'

    def __str__(self):
        return f"{self.titulo} - {self.centro.nome}"


class EventoIntegracao(models.Model):
    """Evento recebido de uma plataforma externa, com controlo de processamento."""
    STATUS_CHOICES = [
        ('RECEBIDO', _('Recebido')),
        ('PROCESSADO', _('Processado')),
        ('ERRO', _('Erro')),
    ]

    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.PROTECT, related_name='eventos_integracao')
    external_id = models.CharField(_('ID Externo'), max_length=120)
    tipo = models.CharField(_('Tipo de Evento'), max_length=60, default='INSCRICAO')
    payload = models.JSONField(_('Dados Recebidos'), default=dict)
    status = models.CharField(_('Estado'), max_length=12, choices=STATUS_CHOICES, default='RECEBIDO', db_index=True)
    erro = models.TextField(_('Erro'), blank=True)
    recebido_em = models.DateTimeField(_('Recebido em'), auto_now_add=True)
    processado_em = models.DateTimeField(_('Processado em'), null=True, blank=True)

    class Meta:
        verbose_name = _('Evento de Integração')
        verbose_name_plural = _('Eventos de Integração')
        constraints = [models.UniqueConstraint(fields=['centro', 'external_id', 'tipo'], name='unique_centro_external_event')]
        ordering = ['-recebido_em']


class MembroCentro(models.Model):
    FUNCAO_CHOICES = [
        ('GESTOR', _('Gestor')),
        ('SECRETARIA', _('Secretaria')),
        ('CAIXA', _('Caixa')),
        ('COORDENACAO', _('Coordenação pedagógica')),
        ('CONSULTA', _('Consulta')),
    ]
    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, related_name='membros_operacionais')
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='funcoes_centro')
    funcao = models.CharField(_('Função'), max_length=16, choices=FUNCAO_CHOICES, default='SECRETARIA')
    ativo = models.BooleanField(_('Ativo'), default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Membro Operacional do Centro')
        verbose_name_plural = _('Membros Operacionais do Centro')
        constraints = [models.UniqueConstraint(fields=['centro', 'usuario'], name='unique_membro_operacional_centro')]

    def __str__(self):
        return f"{self.usuario.nome} - {self.centro.nome} ({self.get_funcao_display()})"


class AuditoriaCentro(models.Model):
    acao = models.CharField(_('Ação'), max_length=80)
    entidade = models.CharField(_('Entidade'), max_length=80)
    objeto_id = models.CharField(_('ID do Objeto'), max_length=80, blank=True)
    centro = models.ForeignKey(CentroDeFormacao, on_delete=models.CASCADE, related_name='auditorias')
    utilizador = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias_centro')
    dados = models.JSONField(_('Dados'), default=dict, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('Auditoria do Centro')
        verbose_name_plural = _('Auditorias do Centro')
        ordering = ['-criado_em']
        indexes = [models.Index(fields=['centro', 'entidade', 'criado_em'])]

    def __str__(self):
        return f"{self.acao} - {self.entidade} - {self.criado_em:%d/%m/%Y %H:%M}"
