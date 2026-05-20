from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Plano(models.Model):
    nome = models.CharField(_('Nome do Plano'), max_length=100)
    descricao = models.TextField(_('Descrição'), blank=True)
    preco = models.DecimalField(_('Preço Mensal'), max_digits=10, decimal_places=2)
    
    limite_cursos = models.PositiveIntegerField(_('Limite de Cursos'), default=5)
    alcance_km = models.PositiveIntegerField(_('Alcance Geográfico (km)'), default=10)
    
    selo_verificacao = models.BooleanField(_('Selo de Verificação'), default=False)
    prioridade_busca = models.PositiveIntegerField(_('Prioridade na Busca'), default=0)
    destaque_home = models.BooleanField(_('Destaque na Página Principal'), default=False)
    acesso_relatorios = models.BooleanField(_('Acesso a Relatórios'), default=False)
    
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Plano')
        verbose_name_plural = _('Planos')
        ordering = ['preco']

    def __str__(self):
        return f"{self.nome} - {self.preco} KZ"

class AssinaturaMembro(models.Model):
    STATUS_CHOICES = [
        ('ATIVO', _('Ativo')),
        ('EXPIRADO', _('Expirado')),
        ('CANCELADO', _('Cancelado')),
        ('PENDENTE', _('Pendente de Pagamento')),
    ]
    
    centro = models.OneToOneField(
        'gestoreduka.CentroDeFormacao', 
        on_delete=models.CASCADE, 
        related_name='assinatura'
    )
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True)
    
    data_inicio = models.DateTimeField(default=timezone.now)
    data_fim = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    
    renovacao_automatica = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Assinatura: {self.centro.nome} - {self.plano.nome if self.plano else 'Sem Plano'}"

    @property
    def esta_ativa(self):
        return self.status == 'ATIVO' and (self.data_fim is None or self.data_fim > timezone.now())

    class Meta:
        verbose_name = _('Assinatura de Membro')
        verbose_name_plural = _('Assinaturas de Membros')

class VoucherPlano(models.Model):
    codigo = models.CharField(_('Código de Ativação'), max_length=20, unique=True)
    plano = models.ForeignKey(Plano, on_delete=models.CASCADE, related_name='vouchers')
    centro = models.ForeignKey('gestoreduka.CentroDeFormacao', on_delete=models.CASCADE, related_name='vouchers')
    usado = models.BooleanField(_('Usado'), default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Voucher de Plano')
        verbose_name_plural = _('Vouchers de Planos')
        ordering = ['-data_criacao']

    def __str__(self):
        return f"{self.codigo} - {self.plano.nome} ({'Usado' if self.usado else 'Livre'})"
