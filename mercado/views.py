import json
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from core.media_urls import public_media_url
from pagamentos.services import PagamentoException, get_payment_service

from .models import PedidoMercado, ProdutoMercado, ItemPedidoMercado


def _media_url(field):
    try:
        return field.url if field else ""
    except (ValueError, AttributeError):
        return ""


def _imagem_produto(produto):
    return public_media_url((produto.imagem_url_publica or _media_url(produto.imagem_principal)).strip())


def _formatar_valor(valor, moeda="AOA"):
    sufixo = "Kz" if moeda == "AOA" else moeda
    return f"{valor:,.0f} {sufixo}".replace(",", " ")


def serializar_produto(produto, detalhe=False):
    payload = {
        "id": produto.id,
        "titulo": produto.titulo,
        "slug": produto.slug,
        "resumo": produto.resumo,
        "imagem_url": _imagem_produto(produto),
        "categoria": produto.categoria.nome,
        "categoria_slug": produto.categoria.slug,
        "preco": float(produto.preco),
        "preco_formatado": _formatar_valor(produto.preco, produto.moeda),
        "moeda": produto.moeda,
        "condicao": produto.get_condicao_display(),
        "garantia": produto.garantia,
        "prazo_entrega_dias": produto.prazo_entrega_dias,
        "disponivel": produto.disponivel_para_pedido,
        "loja": {
            "nome": produto.loja.nome,
            "slug": produto.loja.slug,
            "verificada": produto.loja.verificada,
        },
        "detalhe_url": f"/mercado/produtos/{produto.slug}",
    }
    if detalhe:
        payload.update({
            "descricao": produto.descricao,
            "imagens": [_imagem_produto(produto), *[url for url in produto.imagens if url]],
            "especificacoes": produto.especificacoes or {},
            "loja": {
                **payload["loja"],
                "descricao": produto.loja.descricao,
                "politica_garantia": produto.loja.politica_garantia,
                "origem": f"{produto.loja.municipio}, Luanda",
            },
        })
    return payload


@require_GET
def catalogo_publico(request):
    produtos = ProdutoMercado.objects.filter(
        status="PUBLICADO", loja__ativa=True, loja__verificada=True,
    ).select_related("loja", "categoria")
    categoria = (request.GET.get("categoria") or "").strip()
    if categoria:
        produtos = produtos.filter(categoria__slug=categoria)
    return JsonResponse({
        "produtos": [serializar_produto(item) for item in produtos[:80]],
        "cidade": "Luanda",
        "entrega": "Entrega disponível apenas em Luanda.",
    })


@require_GET
def produto_publico(request, slug):
    produto = get_object_or_404(
        ProdutoMercado.objects.select_related("loja", "categoria"),
        slug=slug,
        status="PUBLICADO",
        loja__ativa=True,
        loja__verificada=True,
    )
    return JsonResponse(serializar_produto(produto, detalhe=True))


def _perfil_telefone(user):
    perfil = getattr(getattr(user, "aluno_profile", None), "perfil", None)
    return (getattr(perfil, "telefone", "") or "").strip()


def _frontend_return_url(request, kind, referencia):
    origin = (request.headers.get("Origin") or "").rstrip("/")
    base = origin if origin.startswith(("https://", "http://")) else getattr(settings, "SITE_DOMAIN", "").rstrip("/")
    return f"{base}/mercado/pedidos?pedido={referencia}&pagamento={kind}"


@login_required
@require_POST
def criar_pedido(request):
    if getattr(request.user, "tipo_usuario", None) != "ALUNO":
        return JsonResponse({"ok": False, "message": "Apenas contas de aluno podem criar pedidos."}, status=403)
    try:
        payload = json.loads(request.body or "{}")
        produto_id = int(payload.get("produto_id"))
        quantidade = int(payload.get("quantidade", 1))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"ok": False, "message": "Dados do produto inválidos."}, status=400)
    if quantidade < 1 or quantidade > 5:
        return JsonResponse({"ok": False, "message": "Pode pedir entre 1 e 5 unidades por produto."}, status=400)
    endereco = (payload.get("endereco_entrega") or "").strip()
    bairro = (payload.get("bairro") or "").strip()
    telefone = (payload.get("telefone") or _perfil_telefone(request.user)).strip()
    if not endereco or not bairro or not telefone:
        return JsonResponse({"ok": False, "message": "Confirme o telefone, o endereço e o bairro para entrega em Luanda."}, status=400)

    produto = get_object_or_404(
        ProdutoMercado.objects.select_related("loja", "categoria"),
        id=produto_id, status="PUBLICADO", loja__ativa=True, loja__verificada=True,
    )
    with transaction.atomic():
        produto = ProdutoMercado.objects.select_for_update().get(pk=produto.pk)
        if produto.quantidade_disponivel < quantidade:
            return JsonResponse({"ok": False, "message": "Este produto já não tem a quantidade solicitada disponível."}, status=409)
        pedido = PedidoMercado.objects.create(
            utilizador=request.user,
            nome_comprador=(request.user.nome or request.user.email).strip(),
            email_comprador=request.user.email,
            telefone_comprador=telefone,
            endereco_entrega=endereco,
            bairro=bairro,
            referencia_endereco=(payload.get("referencia_endereco") or "").strip(),
            observacao_comprador=(payload.get("observacao") or "").strip(),
            municipio="Luanda",
            provincia="Luanda",
            moeda=produto.moeda,
        )
        ItemPedidoMercado.objects.create(
            pedido=pedido,
            produto=produto,
            titulo=produto.titulo,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            custo_unitario=produto.custo_aquisicao,
        )
        pedido.recalcular_totais()
        pedido.save(update_fields=["subtotal", "total", "atualizado_em"])
    return JsonResponse({
        "ok": True,
        "pedido": pedido.referencia,
        "status": pedido.status,
        "message": "Recebemos o pedido. A equipa Edukangola confirmará a disponibilidade antes de abrir o pagamento.",
    }, status=201)


@login_required
@require_GET
def meus_pedidos(request):
    pedidos = PedidoMercado.objects.filter(utilizador=request.user).prefetch_related("itens__produto").order_by("-criado_em")
    return JsonResponse({"pedidos": [
        {
            "referencia": pedido.referencia,
            "status": pedido.status,
            "status_label": pedido.get_status_display(),
            "total": float(pedido.total),
            "total_formatado": _formatar_valor(pedido.total, pedido.moeda),
            "taxa_entrega": float(pedido.taxa_entrega),
            "codigo_entrega": pedido.codigo_entrega if pedido.status in {"EM_ENTREGA", "ENTREGUE"} else "",
            "pode_pagar": pedido.status == "AGUARDA_PAGAMENTO",
            "criado_em": pedido.criado_em.isoformat(),
            "itens": [{
                "titulo": item.titulo,
                "quantidade": item.quantidade,
                "preco_unitario": float(item.preco_unitario),
                "imagem_url": _imagem_produto(item.produto),
                "produto_url": f"/mercado/produtos/{item.produto.slug}",
            } for item in pedido.itens.all()],
        } for pedido in pedidos]})


@login_required
@require_POST
def iniciar_pagamento(request, referencia):
    pedido = get_object_or_404(PedidoMercado.objects.prefetch_related("itens"), referencia=referencia, utilizador=request.user)
    if pedido.status != "AGUARDA_PAGAMENTO":
        return JsonResponse({"ok": False, "message": "Este pedido ainda não está pronto para pagamento."}, status=409)
    if pedido.total <= Decimal("0"):
        return JsonResponse({"ok": False, "message": "O valor do pedido ainda não foi confirmado."}, status=409)
    try:
        pagamento = get_payment_service().criar_pagamento(
            usuario=request.user,
            tipo_pagamento="PEDIDO_MERCADO",
            valor=pedido.total,
            moeda=pedido.moeda,
            url_sucesso=_frontend_return_url(request, "sucesso", pedido.referencia),
            url_cancelamento=_frontend_return_url(request, "cancelado", pedido.referencia),
            metadados={"tipo": "pedido_mercado", "pedido_mercado_id": pedido.id, "pedido_referencia": pedido.referencia},
        )
        pedido.referencia_pagamento = pagamento.referencia_pagamento
        pedido.save(update_fields=["referencia_pagamento", "atualizado_em"])
        return JsonResponse({"ok": True, "url_pagamento": pagamento.url_pagamento, "referencia_pagamento": pagamento.referencia_pagamento})
    except PagamentoException as error:
        return JsonResponse({"ok": False, "message": str(error)}, status=400)
