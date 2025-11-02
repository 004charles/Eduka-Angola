from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from django.utils import timezone
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings




from django.contrib.auth.hashers import make_password, check_password

class CentroDeFormacao(models.Model):
    nome = models.CharField(_('Nome do Centro'), max_length=100, blank=True, null=True)  # Permite em branco
    nif = models.CharField(_('CNPJ'), max_length=18, unique=True, blank=True, null=True)  # Permite em branco
    endereco = models.CharField(_('Endereço'), max_length=255, blank=True, null=True)  # Permite em branco
    telefone = models.CharField(_('Telefone'), max_length=20, blank=True, null=True)  # Permite em branco
    email = models.EmailField(_('E-mail'), unique=True)  # Apenas este campo é obrigatório
    site = models.URLField(_('Site'), blank=True, null=True)
    data_criacao = models.DateTimeField(_('Data de Criação'), auto_now_add=True)
    ativo = models.BooleanField(_('Ativo'), default=True)
    
    # Adicionar este campo para armazenar a senha
    senha_hash = models.CharField(_('Senha Hash'), max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome or self.email  # Retorna email se nome estiver em branco

    def set_senha(self, senha):
        """Define a senha com hash"""
        self.senha_hash = make_password(senha)
    
    def verificar_senha(self, senha):
        """Verifica se a senha está correta"""
        if not self.senha_hash:
            return False
        return check_password(senha, self.senha_hash)

class ConviteCentro(models.Model):
    centro = models.OneToOneField(CentroDeFormacao, on_delete=models.CASCADE, related_name="convite")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    criado_em = models.DateTimeField(default=timezone.now)
    usado = models.BooleanField(default=False)

    def __str__(self):
        return f"Convite para {self.centro.email}"


class Certificacao(models.Model):
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
    centro = models.OneToOneField(CentroDeFormacao, on_delete=models.CASCADE, related_name='perfil')
    dono = models.CharField(max_length=100, null=True, blank=True, verbose_name='Dono do Centro')
    imagem = models.ImageField(_('Imagem ou Logo'), upload_to='centros/', null=True, blank=True)
    banner = models.ImageField(_('Imagem de Capa'), upload_to='centros/banners/', null=True, blank=True)
    video_apresentacao = models.FileField(_('Vídeo de Apresentação'), upload_to='centros videos/', null=True, blank=True)
    descricao = models.TextField(_('Descrição'), null=True, blank=True)
    tipo = models.CharField(_('Tipo de Centro'), max_length=50, null=True, blank=True)
    modalidade = models.CharField(_('Modalidade'), max_length=20, choices=[('Presencial', 'Presencial'), ('Online', 'Online'), ('Híbrido', 'Híbrido')], default='Presencial')
    facebook = models.URLField(_('Facebook'), blank=True, null=True)
    instagram = models.URLField(_('Instagram'), blank=True, null=True)
    whatsapp = models.CharField(_('WhatsApp'), max_length=20, blank=True, null=True)
    destaque = models.BooleanField(_('Centro em Destaque'), default=False)
    slug = models.SlugField(unique=True, null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.centro.nome}"


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
