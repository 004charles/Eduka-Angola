from decimal import Decimal
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.text import slugify


def gerar_referencia_pedido_mercado():
    return f"MKT-{uuid4().hex[:14].upper()}"


def gerar_codigo_entrega():
    return uuid4().hex[:6].upper()


def gerar_expiracao_reserva():
    return timezone.now() + timedelta(minutes=30)


class LojaParceira(models.Model):
    nome = models.CharField(max_length=160)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.TextField(blank=True)
    logotipo = models.ImageField(upload_to="mercado/lojas/", blank=True)
    email_operacional = models.EmailField(blank=True)
    telefone_operacional = models.CharField(max_length=30, blank=True)
    endereco_recolha = models.CharField(max_length=220)
    bairro = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, default="Luanda")
    provincia = models.CharField(max_length=100, default="Luanda")
    politica_garantia = models.TextField(blank=True)
    verificada = models.BooleanField(default=False, db_index=True)
    ativa = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Loja parceira"
        verbose_name_plural = "Lojas parceiras"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nome) or "loja"
            slug = base
            counter = 2
            while type(self).objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class CategoriaMercado(models.Model):
    nome = models.CharField(max_length=90, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    descricao = models.CharField(max_length=220, blank=True)
    ordem = models.PositiveIntegerField(default=0)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["ordem", "nome"]
        verbose_name = "Categoria do Mercado"
        verbose_name_plural = "Categorias do Mercado"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome


class ProdutoMercado(models.Model):
    STATUS_CHOICES = [
        ("RASCUNHO", "Rascunho"),
        ("PUBLICADO", "Publicado"),
        ("INDISPONIVEL", "Indisponível"),
        ("ARQUIVADO", "Arquivado"),
    ]
    CONDICAO_CHOICES = [
        ("NOVO", "Novo"),
        ("RECONDICIONADO", "Recondicionado"),
    ]

    loja = models.ForeignKey(LojaParceira, on_delete=models.PROTECT, related_name="produtos")
    categoria = models.ForeignKey(CategoriaMercado, on_delete=models.PROTECT, related_name="produtos")
    titulo = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    resumo = models.CharField(max_length=260)
    descricao = models.TextField()
    imagem_principal = models.ImageField(upload_to="mercado/produtos/", blank=True)
    imagem_url_publica = models.CharField(max_length=500, blank=True, help_text="URL pública de imagem quando o ficheiro não é enviado ao servidor.")
    imagens = models.JSONField(default=list, blank=True, help_text="URLs adicionais de imagens do produto.")
    especificacoes = models.JSONField(default=dict, blank=True, help_text="Características técnicas apresentadas ao comprador.")
    condicao = models.CharField(max_length=20, choices=CONDICAO_CHOICES, default="NOVO")
    garantia = models.CharField(max_length=180, blank=True)
    custo_aquisicao = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    preco = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    moeda = models.CharField(max_length=3, default="AOA")
    quantidade_disponivel = models.PositiveIntegerField(default=0)
    disponibilidade_confirmada_em = models.DateTimeField(null=True, blank=True)
    disponibilidade_confirmada_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="produtos_mercado_confirmados",
    )
    prazo_entrega_dias = models.PositiveSmallIntegerField(default=2)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="RASCUNHO", db_index=True)
    destaque = models.BooleanField(default=False, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-destaque", "-atualizado_em"]
        verbose_name = "Produto do Mercado"
        verbose_name_plural = "Produtos do Mercado"
        indexes = [models.Index(fields=["status", "destaque"])]

    @property
    def disponivel_para_pedido(self):
        return self.status == "PUBLICADO" and self.loja.ativa and self.loja.verificada and self.quantidade_disponivel > 0

    def confirmar_disponibilidade(self, utilizador, quantidade=None):
        if quantidade is not None:
            self.quantidade_disponivel = max(0, quantidade)
        self.disponibilidade_confirmada_em = timezone.now()
        self.disponibilidade_confirmada_por = utilizador
        if self.quantidade_disponivel and self.status == "INDISPONIVEL":
            self.status = "PUBLICADO"
        self.save(update_fields=[
            "quantidade_disponivel", "disponibilidade_confirmada_em",
            "disponibilidade_confirmada_por", "status", "atualizado_em",
        ])

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.titulo) or "produto"
            slug = base
            counter = 2
            while type(self).objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class PedidoMercado(models.Model):
    STATUS_CHOICES = [
        ("A_VALIDAR", "A validar disponibilidade"),
        ("AGUARDA_PAGAMENTO", "A aguardar pagamento"),
        ("PAGO_RECOLHA", "Pago — a recolher"),
        ("PREPARAR_ENTREGA", "Em preparação para entrega"),
        ("EM_ENTREGA", "Em entrega"),
        ("ENTREGUE", "Entregue"),
        ("OCORRENCIA", "Com ocorrência"),
        ("CANCELADO", "Cancelado"),
        ("REEMBOLSO_PENDENTE", "Reembolso pendente"),
        ("REEMBOLSADO", "Reembolsado"),
    ]
    referencia = models.CharField(max_length=80, unique=True, default=gerar_referencia_pedido_mercado)
    utilizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pedidos_mercado")
    nome_comprador = models.CharField(max_length=160)
    email_comprador = models.EmailField()
    telefone_comprador = models.CharField(max_length=30)
    endereco_entrega = models.CharField(max_length=250)
    bairro = models.CharField(max_length=100)
    municipio = models.CharField(max_length=100, default="Luanda")
    provincia = models.CharField(max_length=100, default="Luanda")
    referencia_endereco = models.CharField(max_length=200, blank=True)
    observacao_comprador = models.CharField(max_length=300, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    taxa_entrega = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    moeda = models.CharField(max_length=3, default="AOA")
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default="A_VALIDAR", db_index=True)
    referencia_pagamento = models.CharField(max_length=100, blank=True, db_index=True)
    codigo_entrega = models.CharField(max_length=12, default=gerar_codigo_entrega)
    estafeta_nome = models.CharField(max_length=120, blank=True)
    estafeta_telefone = models.CharField(max_length=30, blank=True)
    previsao_entrega = models.DateTimeField(null=True, blank=True)
    disponibilidade_confirmada_em = models.DateTimeField(null=True, blank=True)
    pagamento_confirmado_em = models.DateTimeField(null=True, blank=True)
    reserva_expira_em = models.DateTimeField(default=gerar_expiracao_reserva, db_index=True, null=True, blank=True)
    reserva_ativa = models.BooleanField(default=False)
    reserva_liberada_em = models.DateTimeField(null=True, blank=True)
    recolhido_em = models.DateTimeField(null=True, blank=True)
    entregue_em = models.DateTimeField(null=True, blank=True)
    comprovativo_recolha = models.FileField(upload_to="mercado/recolhas/", blank=True)
    comprovativo_entrega = models.FileField(upload_to="mercado/entregas/", blank=True)
    notas_admin = models.TextField(blank=True)
    motivo_ocorrencia = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]
        verbose_name = "Pedido do Mercado"
        verbose_name_plural = "Pedidos do Mercado"
        indexes = [models.Index(fields=["status", "criado_em"])]

    def recalcular_totais(self):
        self.subtotal = sum((item.preco_unitario * item.quantidade for item in self.itens.all()), Decimal("0"))
        self.total = self.subtotal + self.taxa_entrega

    def liberar_reserva(self, motivo=""):
        """Devolve unidades reservadas uma única vez, dentro de uma transacção atómica."""
        with transaction.atomic():
            pedido = type(self).objects.select_for_update().get(pk=self.pk)
            if not pedido.reserva_ativa or pedido.reserva_liberada_em or pedido.status not in {"AGUARDA_PAGAMENTO", "CANCELADO"}:
                return False
            for item in pedido.itens.select_related("produto__loja"):
                produto = ProdutoMercado.objects.select_for_update().select_related("loja").get(pk=item.produto_id)
                produto.quantidade_disponivel += item.quantidade
                if produto.loja.ativa and produto.loja.verificada and produto.status == "INDISPONIVEL":
                    produto.status = "PUBLICADO"
                produto.save(update_fields=["quantidade_disponivel", "status", "atualizado_em"])
            pedido.status = "CANCELADO"
            pedido.reserva_ativa = False
            pedido.reserva_liberada_em = timezone.now()
            pedido.reserva_expira_em = None
            if motivo:
                pedido.notas_admin = f"{pedido.notas_admin}\n{motivo}".strip()
            pedido.save(update_fields=["status", "reserva_ativa", "reserva_liberada_em", "reserva_expira_em", "notas_admin", "atualizado_em"])
        return True

    @classmethod
    def liberar_reservas_expiradas(cls):
        referencias = list(cls.objects.filter(
            status="AGUARDA_PAGAMENTO",
            reserva_ativa=True,
            reserva_liberada_em__isnull=True,
            reserva_expira_em__lt=timezone.now(),
        ).values_list("pk", flat=True))
        for pedido_id in referencias:
            try:
                cls.objects.get(pk=pedido_id).liberar_reserva("Reserva expirada sem pagamento.")
            except cls.DoesNotExist:
                continue

    def __str__(self):
        return self.referencia


class ItemPedidoMercado(models.Model):
    pedido = models.ForeignKey(PedidoMercado, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(ProdutoMercado, on_delete=models.PROTECT, related_name="itens_pedidos")
    titulo = models.CharField(max_length=180)
    quantidade = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    custo_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Item do pedido"
        verbose_name_plural = "Itens do pedido"

    def __str__(self):
        return f"{self.quantidade} × {self.titulo}"
