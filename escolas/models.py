from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

class CategoriaEscola(models.Model):
    """Categorias globais para Escolas (ex: Ensino Geral, Ensino Técnico, PUNIV)"""
    nome = models.CharField(_('Nome'), max_length=100, unique=True)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)
    icone = models.CharField(_('Ícone (FontAwesome/Feather)'), max_length=50, blank=True, help_text="Ex: feather-book")
    descricao = models.TextField(_('Descrição'), blank=True)
    ativa = models.BooleanField(_('Ativa'), default=True)

    class Meta:
        verbose_name = _('Categoria de Escola')
        verbose_name_plural = _('Categorias de Escolas')
        ordering = ['nome']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Escola(models.Model):
    """Modelo principal de uma Escola do Ensino Geral/Médio."""
    TIPO_REDE = [
        ('PUBLICA', 'Pública / Estatal'),
        ('PRIVADA', 'Privada'),
        ('COMPARTICIPADA', 'Comparticipada'),
    ]

    nome = models.CharField(_('Nome da Escola'), max_length=200)
    tipo_rede = models.CharField(_('Tipo de Rede'), max_length=20, choices=TIPO_REDE, default='PUBLICA')
    
    provincia = models.CharField(_('Província'), max_length=100)
    municipio = models.CharField(_('Município'), max_length=100)
    endereco = models.CharField(_('Endereço Completo'), max_length=255, blank=True)
    
    categorias = models.ManyToManyField(CategoriaEscola, related_name='escolas', blank=True)
    
    telefone = models.CharField(_('Telefone'), max_length=50, blank=True)
    email = models.EmailField(_('E-mail'), blank=True, null=True)
    site = models.URLField(_('Site'), blank=True, null=True)
    
    mensalidade_base = models.DecimalField(_('Mensalidade Base (Kz)'), max_digits=12, decimal_places=2, default=0, help_text="0 para escolas públicas")
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Escola')
        verbose_name_plural = _('Escolas')

    def __str__(self):
        return f"{self.nome} ({self.provincia})"


class PerfilEscola(models.Model):
    """Informações estendidas e de branding da Escola."""
    escola = models.OneToOneField(Escola, on_delete=models.CASCADE, related_name='perfil')
    
    logo = models.ImageField(_('Logotipo'), upload_to='escolas/logos/', null=True, blank=True)
    banner = models.ImageField(_('Banner/Capa'), upload_to='escolas/banners/', null=True, blank=True)
    
    descricao = models.TextField(_('Descrição / História'), blank=True)
    missao = models.TextField(_('Missão'), blank=True)
    visao = models.TextField(_('Visão'), blank=True)
    
    ano_fundacao = models.PositiveIntegerField(_('Ano de Fundação'), null=True, blank=True)
    diretor = models.CharField(_('Diretor(a)'), max_length=150, blank=True)
    
    facebook = models.URLField(_('Facebook'), blank=True)
    instagram = models.URLField(_('Instagram'), blank=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True)
    whatsapp = models.CharField(_('WhatsApp'), max_length=50, blank=True)
    
    verificada = models.BooleanField(_('Escola Verificada'), default=False)
    
    def __str__(self):
        return f"Perfil de {self.escola.nome}"


class AreaFormacao(models.Model):
    """Área de formação do curso (ex: Informática, Mecânica, Saúde)"""
    nome = models.CharField(_('Nome da Área'), max_length=150, unique=True)
    descricao = models.TextField(_('Descrição'), blank=True)
    
    class Meta:
        verbose_name = _('Área de Formação')
        verbose_name_plural = _('Áreas de Formação')
        ordering = ['nome']

    def __str__(self):
        return self.nome


class CursoEnsinoMedio(models.Model):
    """Cursos lecionados na Escola (Ex: Ciências Físicas e Biológicas, Enfermagem)"""
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name='cursos')
    area_formacao = models.ForeignKey(AreaFormacao, on_delete=models.SET_NULL, null=True, blank=True, related_name='cursos')
    nome = models.CharField(_('Nome do Curso'), max_length=150)
    descricao = models.TextField(_('Descrição do Curso'), blank=True)
    duracao_anos = models.PositiveIntegerField(_('Duração (Anos)'), default=3)
    periodos = models.CharField(_('Períodos (Manhã, Tarde, Noite)'), max_length=100, blank=True)
    vagas_anuais = models.PositiveIntegerField(_('Vagas Anuais Estimadas'), null=True, blank=True)

    class Meta:
        verbose_name = _('Curso do Ensino Médio')
        verbose_name_plural = _('Cursos do Ensino Médio')
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.escola.nome}"


class GaleriaEscola(models.Model):
    """Galeria de imagens da Escola"""
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE, related_name='galeria')
    imagem = models.ImageField(_('Imagem'), upload_to='escolas/galeria/')
    legenda = models.CharField(_('Legenda'), max_length=200, blank=True)
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Imagem da Galeria (Escola)')
        verbose_name_plural = _('Galeria de Imagens (Escola)')

    def __str__(self):
        return f"Imagem de {self.escola.nome}"
