from decimal import Decimal
from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from core.notification_events import queue_notification_event


def gerar_referencia_pedido():
    return f"EVT-{uuid4().hex[:14].upper()}"


class OrganizadorEvento(models.Model):
    TIPO_CHOICES = [
        ("COMUNIDADE", "Comunidade / Grupo"),
        ("EMPRESA", "Empresa"),
        ("INSTITUICAO", "Instituição"),
        ("OUTRO", "Outro"),
    ]

    nome = models.CharField("Nome público", max_length=160)
    slug = models.SlugField(unique=True, blank=True)
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES, default="COMUNIDADE")
    descricao = models.TextField(blank=True)
    email = models.EmailField("Email de contacto")
    telefone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    logotipo = models.ImageField(upload_to="eventos/organizadores/", blank=True)
    verificado = models.BooleanField("Verificado pela Edukangola", default=False)
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Organizador de evento"
        verbose_name_plural = "Organizadores de eventos"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class EventoMarketplace(models.Model):
    STATUS_CHOICES = [
        ("RASCUNHO", "Rascunho"),
        ("PENDENTE", "Pendente de aprovação"),
        ("PUBLICADO", "Publicado"),
        ("ESGOTADO", "Esgotado"),
        ("ENCERRADO", "Encerrado"),
        ("CANCELADO", "Cancelado"),
    ]
    MODALIDADE_CHOICES = [
        ("PRESENCIAL", "Presencial"),
        ("ONLINE", "Online"),
        ("HIBRIDO", "Híbrido"),
    ]

    organizador = models.ForeignKey(OrganizadorEvento, on_delete=models.PROTECT, related_name="eventos")
    titulo = models.CharField("Título", max_length=220)
    slug = models.SlugField(unique=True, blank=True)
    resumo = models.CharField(max_length=320, blank=True)
    descricao = models.TextField()
    imagem_capa = models.ImageField(upload_to="eventos/capas/", blank=True)
    categoria = models.CharField(max_length=100, default="Tecnologia")
    modalidade = models.CharField(max_length=12, choices=MODALIDADE_CHOICES, default="PRESENCIAL")
    data_inicio = models.DateTimeField(db_index=True)
    data_fim = models.DateTimeField(null=True, blank=True)
    local = models.CharField(max_length=220, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    url_online = models.URLField(blank=True)
    status = models.CharField(max_length=14, choices=STATUS_CHOICES, default="RASCUNHO", db_index=True)
    destaque = models.BooleanField(default=False, db_index=True)
    comissao_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("15.00"), validators=[MinValueValidator(0)])
    criado_em = models.DateTimeField(auto_now_add=True)
    actualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-destaque", "data_inicio"]
        verbose_name = "Evento do marketplace"
        verbose_name_plural = "Eventos do marketplace"
        indexes = [models.Index(fields=["status", "data_inicio"])]

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = type(self).objects.filter(pk=self.pk).values_list('status', flat=True).first()
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
        if self.status == 'PUBLICADO' and previous_status != 'PUBLICADO':
            queue_notification_event(
                'event.published',
                f'event.published:{self.pk}',
                {'event_id': self.pk, 'title': self.titulo, 'category': self.categoria, 'link': f'/eventos/{self.slug}'},
                occurred_at=self.actualizado_em,
            )

    @property
    def publicado(self):
        return self.status == "PUBLICADO"

    def __str__(self):
        return self.titulo


class LoteBilhete(models.Model):
    evento = models.ForeignKey(EventoMarketplace, on_delete=models.CASCADE, related_name="lotes")
    nome = models.CharField("Nome do lote", max_length=120)
    descricao = models.CharField(max_length=240, blank=True)
    texto_ingresso = models.CharField("Texto do ingresso", max_length=180, blank=True, help_text="Texto curto apresentado no ingresso digital.")
    beneficios = models.TextField("Benefícios", blank=True, help_text="Um benefício por linha.")
    regras = models.TextField("Regras", blank=True, help_text="Regras específicas deste lote, um item por linha.")
    cor_primaria = models.CharField("Cor principal", max_length=7, default="#0F6B8A", help_text="Azul Edukangola em hexadecimal, por exemplo #0F6B8A.")
    cor_secundaria = models.CharField("Cor secundária", max_length=7, default="#EAF8FA", help_text="Fundo azul claro em hexadecimal, por exemplo #EAF8FA.")
    imagem_ingresso = models.ImageField("Imagem do ingresso", upload_to="eventos/ingressos/", blank=True)
    preco = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    moeda = models.CharField(max_length=3, default="AOA")
    quantidade_total = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    quantidade_vendida = models.PositiveIntegerField(default=0)
    inicio_vendas = models.DateTimeField(null=True, blank=True)
    fim_vendas = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True, db_index=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "preco"]
        verbose_name = "Lote de bilhetes"
        verbose_name_plural = "Lotes de bilhetes"

    @property
    def lugares_disponiveis(self):
        return max(self.quantidade_total - self.quantidade_vendida, 0)

    @property
    def disponivel_para_venda(self):
        agora = timezone.now()
        return self.activo and self.lugares_disponiveis > 0 and (not self.inicio_vendas or agora >= self.inicio_vendas) and (not self.fim_vendas or agora <= self.fim_vendas)

    def __str__(self):
        return f"{self.evento.titulo} — {self.nome}"


class PedidoBilhete(models.Model):
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("PAGO", "Pago"),
        ("CANCELADO", "Cancelado"),
        ("EXPIRADO", "Expirado"),
        ("REEMBOLSADO", "Reembolsado"),
    ]

    referencia = models.CharField(max_length=80, unique=True, default=gerar_referencia_pedido)
    evento = models.ForeignKey(EventoMarketplace, on_delete=models.PROTECT, related_name="pedidos")
    lote = models.ForeignKey(LoteBilhete, on_delete=models.PROTECT, related_name="pedidos")
    utilizador = models.ForeignKey("usuarios.Usuario", on_delete=models.PROTECT, null=True, blank=True, related_name="pedidos_bilhetes")
    nome_comprador = models.CharField(max_length=160)
    email_comprador = models.EmailField()
    telefone_comprador = models.CharField(max_length=30, blank=True)
    quantidade = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    valor_bruto = models.DecimalField(max_digits=12, decimal_places=2)
    valor_comissao = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_organizador = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    moeda = models.CharField(max_length=3, default="AOA")
    status = models.CharField(max_length=14, choices=STATUS_CHOICES, default="PENDENTE", db_index=True)
    referencia_pagamento = models.CharField(max_length=100, blank=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    pago_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Pedido de bilhete"
        verbose_name_plural = "Pedidos de bilhetes"

    def calcular_comissao(self):
        percentual = self.evento.comissao_percentual / Decimal("100")
        self.valor_comissao = (self.valor_bruto * percentual).quantize(Decimal("0.01"))
        self.valor_organizador = self.valor_bruto - self.valor_comissao

    def __str__(self):
        return self.referencia


class Bilhete(models.Model):
    STATUS_CHOICES = [
        ("VALIDO", "Válido"),
        ("UTILIZADO", "Utilizado"),
        ("CANCELADO", "Cancelado"),
    ]

    pedido = models.ForeignKey(PedidoBilhete, on_delete=models.CASCADE, related_name="bilhetes")
    lote = models.ForeignKey(LoteBilhete, on_delete=models.PROTECT, related_name="bilhetes")
    codigo = models.UUIDField(default=uuid4, unique=True, editable=False)
    nome_participante = models.CharField(max_length=160)
    email_participante = models.EmailField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="VALIDO", db_index=True)
    emitido_em = models.DateTimeField(auto_now_add=True)
    utilizado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-emitido_em"]
        verbose_name = "Bilhete"
        verbose_name_plural = "Bilhetes"

    def __str__(self):
        return f"{self.pedido.evento.titulo} — {self.codigo}"
