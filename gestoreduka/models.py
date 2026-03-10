from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.utils import timezone
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


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





from django.contrib.auth.hashers import make_password, check_password

# from django.contrib.gis.db import models as gis_models
# from django.contrib.gis.geos import Point
# from django.utils.translation import gettext_lazy as _

class CentroDeFormacao(gis_models.Model):
    """
    Modelo principal para um Centro de Formação Profissional.
    Lida com endereço físico, coordenadas GIS e informações básicas de contato.
    Integrado com a autenticação centralizada do Usuario.
    """
    usuario = models.OneToOneField('usuarios.Usuario', on_delete=models.CASCADE, related_name='centro_profile', null=True, blank=True)
    nome = models.CharField(_('Nome do Centro'), max_length=100, blank=True, null=True)
    nif = models.CharField(_('NIF'), max_length=18, unique=True, blank=True, null=True)
    endereco = models.CharField(_('Endereço'), max_length=255, blank=True, null=True)
    cidade = models.CharField(_('Cidade'), max_length=100, blank=True, null=True)
    provincia = models.CharField(_('Província'), max_length=100, blank=True, null=True)
    
    if HAS_GEODJANGO and not settings.DATABASES['default']['ENGINE'].endswith('sqlite3'):
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
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    ativo = models.BooleanField(_('Ativo'), default=True)
    # senha_hash is removed in favor of centralized auth

    def __str__(self):
        return self.nome or self.email

    @property
    def latitude(self):
        return self.localizacao.y if self.localizacao else None

    @property
    def longitude(self):
        return self.localizacao.x if self.localizacao else None

    def set_localizacao(self, lat, lng):
        self.localizacao = Point(lng, lat, srid=4326)

    def get_endereco_completo(self):
        parts = [part for part in [self.endereco, self.cidade, self.provincia] if part]
        return ", ".join(parts) if parts else "Endereço não informado"

    # set_senha and verificar_senha are removed as they are now handled by Usuario

    class Meta:
        verbose_name = _('Centro de Formação')
        verbose_name_plural = _('Centros de Formação')


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
    Modelo para armazenar depoimentos de alunos sobre o centro de formação.
    """
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='depoimentos'
    )
    nome = models.CharField(_('Nome'), max_length=100)
    foto = models.ImageField(_('Foto'), upload_to='depoimentos/', blank=True)
    cargo = models.CharField(_('Cargo/Curso'), max_length=100, blank=True)
    texto = models.TextField(_('Depoimento'))
    nota = models.PositiveIntegerField(_('Nota (1-5)'))
    data = models.DateField(_('Data'), auto_now_add=True)
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
    imagem = models.ImageField(_('Imagem ou Logo'), upload_to='centros/', null=True, blank=True)
    banner = models.ImageField(_('Imagem de Capa'), upload_to='centros/banners/', null=True, blank=True)
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
    destaque = models.BooleanField(_('Centro em Destaque'), default=False)
    verificado = models.BooleanField(_('Centro Verificado'), default=False)
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



class ReelCentro(models.Model):
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='reels'
    )
    titulo = models.CharField(_('Título'), max_length=200)
    descricao = models.TextField(_('Descrição'), blank=True)
    video = models.FileField(
        _('Vídeo'), 
        upload_to='reels/',
        help_text="Vídeos curtos para engajamento"
    )
    thumbnail = models.ImageField(
        _('Thumbnail'), 
        upload_to='reels/thumbnails/', 
        blank=True,
        help_text="Imagem de capa do vídeo (opcional)"
    )
    duracao = models.PositiveIntegerField(
        _('Duração (segundos)'), 
        default=0,
        help_text="Duração do vídeo em segundos"
    )
    
    # Estatísticas de engajamento
    visualizacoes = models.PositiveIntegerField(_('Visualizações'), default=0)
    curtidas = models.PositiveIntegerField(_('Curtidas'), default=0)
    comentarios = models.PositiveIntegerField(_('Comentários'), default=0)
    compartilhamentos = models.PositiveIntegerField(_('Compartilhamentos'), default=0)
    
    # Configurações
    destaque = models.BooleanField(_('Reel em Destaque'), default=False)
    publico = models.BooleanField(_('Público'), default=True)
    data_publicacao = models.DateTimeField(_('Data de Publicação'), auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-destaque', '-data_publicacao']
        verbose_name = _('Reel')
        verbose_name_plural = _('Reels')
        
    def __str__(self):
        return f"{self.titulo} - {self.centro.nome}"
    
    def incrementar_visualizacao(self):
        """Incrementa contador de visualizações"""
        self.visualizacoes += 1
        self.save(update_fields=['visualizacoes'])
    
    def incrementar_curtida(self):
        """Incrementa contador de curtidas"""
        self.curtidas += 1
        self.save(update_fields=['curtidas'])
    
    def decrementar_curtida(self):
        """Decrementa contador de curtidas"""
        if self.curtidas > 0:
            self.curtidas -= 1
            self.save(update_fields=['curtidas'])

class CurtidaReel(models.Model):
    """Registra curtidas individuais nos reels"""
    reel = models.ForeignKey(ReelCentro, on_delete=models.CASCADE, related_name='curtidas_users')
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE)
    data_curtida = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['reel', 'aluno']
        verbose_name = _('Curtida de Reel')
        verbose_name_plural = _('Curtidas de Reels')

    def __str__(self):
        return f"{self.aluno.nome} curtiu {self.reel.titulo}"

class ComentarioReel(models.Model):
    """Comentários nos reels"""
    reel = models.ForeignKey(ReelCentro, on_delete=models.CASCADE, related_name='comentarios_lista')
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE)
    texto = models.TextField(_('Comentário'), max_length=500)
    data_comentario = models.DateTimeField(auto_now_add=True)
    aprovado = models.BooleanField(_('Aprovado'), default=True)

    class Meta:
        ordering = ['-data_comentario']
        verbose_name = _('Comentário de Reel')
        verbose_name_plural = _('Comentários de Reels')

    def __str__(self):
        return f"Comentário de {self.aluno.nome} em {self.reel.titulo}"


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
    ativa = models.BooleanField(_('Ativa'), default=True)

    class Meta:
        verbose_name = _('Parceria')
        verbose_name_plural = _('Parcerias')

    def __str__(self):
        return f"{self.nome_empresa} - {self.centro.nome}"

class Evento(models.Model):
    centro = models.ForeignKey(
        CentroDeFormacao,
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    titulo = models.CharField(_('Título'), max_length=200)
    descricao = models.TextField(_('Descrição'))
    data_inicio = models.DateTimeField(_('Data de Início'))
    data_fim = models.DateTimeField(_('Data de Fim'), blank=True, null=True)
    local = models.CharField(_('Local'), max_length=200)
    tipo = models.CharField(_('Tipo'), max_length=50, choices=[
        ('WORKSHOP', 'Workshop'),
        ('PALESTRA', 'Palestra'),
        ('FEIRA', 'Feira de Carreiras'),
        ('AULA_ABERTA', 'Aula Aberta'),
        ('OUTRO', 'Outro')
    ])
    link_inscricao = models.URLField(_('Link de Inscrição'), blank=True)
    imagem = models.ImageField(_('Imagem'), upload_to='eventos/', blank=True)
    destaque = models.BooleanField(_('Evento em Destaque'), default=False)

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
    nome = models.CharField(_('Nome da Filial'), max_length=100)
    endereco = models.CharField(_('Endereço'), max_length=255)
    telefone = models.CharField(_('Telefone'), max_length=20)
    email = models.EmailField(_('E-mail'), unique=True)
    whatsapp = models.CharField(_('WhatsApp'), max_length=20, blank=True, null=True)
    ativo = models.BooleanField(_('Ativa'), default=True)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)

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

    class Meta:
        ordering = ['data_envio']

    def __str__(self):
        return f"Mensagem de {self.remetente} - {self.mensagem[:20]}"

    @property
    def remetente(self):
        if self.remetente_aluno:
            return self.remetente_aluno
        return self.remetente_centro

    def is_centro(self):
        return self.remetente_centro is not None
