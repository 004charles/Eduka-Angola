import json
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import Bilhete, EventoMarketplace, LoteBilhete, OrganizadorEvento, PedidoBilhete
from pagamentos.services import PagamentoException, get_payment_service


def _frontend_return_url(request, kind, pedido):
    query = f"tipo=bilhete&pedido={pedido}"
    origin = (request.headers.get("Origin") or "").rstrip("/")
    configured = getattr(settings, "FRONTEND_RETURN_URL" if kind == "sucesso" else "FRONTEND_CANCEL_URL", "")
    candidates = [origin, configured, getattr(settings, "SITE_DOMAIN", "")]
    for base in candidates:
        base = (base or "").strip().rstrip("/")
        if not base.startswith(("http://", "https://")):
            continue
        if "localhost" in base or "127.0.0.1" in base:
            continue
        if "/pagamento/" not in base:
            base = f"{base}/pagamento/{kind}"
        return f"{base}?{query}"
    return request.build_absolute_uri(f"/pagamento/{kind}/?{query}")


def _media_url(field):
    try:
        return field.url if field else ""
    except (ValueError, AttributeError):
        return ""


def _evento_data(evento):
    lotes = [lote for lote in evento.lotes.all() if lote.disponivel_para_venda]
    return {
        "id": evento.id,
        "titulo": evento.titulo,
        "slug": evento.slug,
        "resumo": evento.resumo,
        "descricao": evento.descricao,
        "imagem_url": _media_url(evento.imagem_capa),
        "categoria": evento.categoria,
        "modalidade": evento.get_modalidade_display(),
        "data_inicio": evento.data_inicio.isoformat(),
        "data_inicio_formatada": timezone.localtime(evento.data_inicio).strftime("%d/%m/%Y · %H:%M"),
        "data_fim": evento.data_fim.isoformat() if evento.data_fim else "",
        "local": evento.local,
        "cidade": evento.cidade,
        "provincia": evento.provincia,
        "url_online": evento.url_online,
        "organizador": {
            "nome": evento.organizador.nome,
            "slug": evento.organizador.slug,
            "verificado": evento.organizador.verificado,
            "logotipo_url": _media_url(evento.organizador.logotipo),
        },
        "lotes": [{
            "id": lote.id,
            "nome": lote.nome,
            "descricao": lote.descricao,
            "texto_ingresso": lote.texto_ingresso,
            "beneficios": [item.strip() for item in lote.beneficios.splitlines() if item.strip()],
            "regras": [item.strip() for item in lote.regras.splitlines() if item.strip()],
            "cor_primaria": lote.cor_primaria,
            "cor_secundaria": lote.cor_secundaria,
            "imagem_ingresso_url": _media_url(lote.imagem_ingresso),
            "preco": str(lote.preco),
            "moeda": lote.moeda,
            "lugares_disponiveis": lote.lugares_disponiveis,
            "fim_vendas": lote.fim_vendas.isoformat() if lote.fim_vendas else "",
        } for lote in lotes],
        "bilhetes_disponiveis": sum(lote.lugares_disponiveis for lote in lotes),
        "detalhe_url": f"/eventos/{evento.slug}",
    }


@require_GET
def eventos_publicos(request):
    eventos = EventoMarketplace.objects.filter(
        status="PUBLICADO",
        organizador__ativo=True,
        data_inicio__gte=timezone.now(),
    ).select_related("organizador").prefetch_related("lotes")
    return JsonResponse({"eventos": [_evento_data(evento) for evento in eventos]})


@require_GET
def evento_publico_detalhe(request, slug):
    evento = get_object_or_404(
        EventoMarketplace.objects.select_related("organizador").prefetch_related("lotes"),
        slug=slug,
        status="PUBLICADO",
        organizador__ativo=True,
    )
    return JsonResponse(_evento_data(evento))


@login_required
@require_POST
def criar_pedido_bilhete(request):
    try:
        payload = json.loads(request.body or "{}")
        evento_id = int(payload.get("evento_id"))
        lote_id = int(payload.get("lote_id"))
        quantidade = int(payload.get("quantidade", 1))
    except (TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse({"sucesso": False, "erro": "Dados do bilhete inválidos."}, status=400)

    if quantidade < 1 or quantidade > 5:
        return JsonResponse({"sucesso": False, "erro": "Pode comprar entre 1 e 5 bilhetes por pedido."}, status=400)

    evento = get_object_or_404(EventoMarketplace, id=evento_id, status="PUBLICADO", organizador__ativo=True)

    try:
        with transaction.atomic():
            lote = LoteBilhete.objects.select_for_update().get(id=lote_id, evento=evento, activo=True)
            if not lote.disponivel_para_venda or lote.lugares_disponiveis < quantidade:
                return JsonResponse({"sucesso": False, "erro": "Este lote já não tem lugares suficientes."}, status=409)

            valor_bruto = (lote.preco * quantidade).quantize(Decimal("0.01"))
            pedido = PedidoBilhete(
                evento=evento,
                lote=lote,
                utilizador=request.user,
                nome_comprador=getattr(request.user, "nome", "") or request.user.get_username(),
                email_comprador=request.user.email,
                quantidade=quantidade,
                valor_bruto=valor_bruto,
                moeda=lote.moeda,
            )
            pedido.calcular_comissao()
            pedido.save()

            servico = get_payment_service()
            pagamento = servico.criar_pagamento(
                usuario=request.user,
                tipo_pagamento="BILHETE_EVENTO",
                valor=valor_bruto,
                moeda=lote.moeda,
                url_sucesso=_frontend_return_url(request, "sucesso", pedido.referencia),
                url_cancelamento=_frontend_return_url(request, "cancelado", pedido.referencia),
                metadados={
                    "tipo": "bilhete_evento",
                    "pedido_bilhete_id": pedido.id,
                    "pedido_referencia": pedido.referencia,
                    "evento_id": evento.id,
                    "lote_id": lote.id,
                    "quantidade": quantidade,
                },
            )
            pedido.referencia_pagamento = pagamento.referencia_pagamento
            pedido.save(update_fields=["referencia_pagamento"])

        return JsonResponse({
            "sucesso": True,
            "pedido": pedido.referencia,
            "status": pagamento.status,
            "url_pagamento": pagamento.url_pagamento,
            "referencia_pagamento": pagamento.referencia_pagamento,
        }, status=201)
    except LoteBilhete.DoesNotExist:
        return JsonResponse({"sucesso": False, "erro": "Lote de bilhete não encontrado."}, status=404)
    except PagamentoException as error:
        return JsonResponse({"sucesso": False, "erro": str(error)}, status=400)
    except Exception:
        return JsonResponse({"sucesso": False, "erro": "Não foi possível iniciar o pagamento do bilhete."}, status=500)

@require_GET
def meus_bilhetes(request):
    if not request.user.is_authenticated:
        return JsonResponse({'erro': 'Autenticação necessária.'}, status=401)
    pedidos = PedidoBilhete.objects.filter(
        utilizador=request.user,
        status='PAGO',
        bilhetes__isnull=False,
    ).select_related('evento', 'evento__organizador', 'lote').prefetch_related('bilhetes').distinct().order_by('-pago_em', '-criado_em')
    itens = []
    for pedido in pedidos:
        for bilhete in pedido.bilhetes.all():
            evento = pedido.evento
            lote = bilhete.lote
            itens.append({
                'id': bilhete.id,
                'codigo': str(bilhete.codigo),
                'status': bilhete.status,
                'status_label': bilhete.get_status_display(),
                'emitido_em': bilhete.emitido_em.isoformat(),
                'participante': bilhete.nome_participante,
                'email_participante': bilhete.email_participante,
                'referencia_pedido': pedido.referencia,
                'referencia_pagamento': pedido.referencia_pagamento,
                'pago_em': pedido.pago_em.isoformat() if pedido.pago_em else '',
                'evento': {
                    'titulo': evento.titulo,
                    'slug': evento.slug,
                    'imagem_url': _media_url(evento.imagem_capa),
                    'data_inicio': evento.data_inicio.isoformat(),
                    'data_inicio_formatada': timezone.localtime(evento.data_inicio).strftime('%d/%m/%Y · %H:%M'),
                    'data_fim_formatada': timezone.localtime(evento.data_fim).strftime('%d/%m/%Y · %H:%M') if evento.data_fim else '',
                    'local': evento.local,
                    'cidade': evento.cidade,
                    'provincia': evento.provincia,
                    'modalidade': evento.get_modalidade_display(),
                    'organizador': evento.organizador.nome,
                },
                'lote': {
                    'nome': lote.nome,
                    'texto_ingresso': lote.texto_ingresso,
                    'beneficios': [item.strip() for item in lote.beneficios.splitlines() if item.strip()],
                    'regras': [item.strip() for item in lote.regras.splitlines() if item.strip()],
                    'cor_primaria': lote.cor_primaria,
                    'cor_secundaria': lote.cor_secundaria,
                    'imagem_ingresso_url': _media_url(lote.imagem_ingresso),
                },
                'detalhe_url': f'/eventos/{evento.slug}',
            })
    return JsonResponse({'bilhetes': itens})


@require_POST
def validar_bilhete(request):
    """Validar um bilhete pelo código QR para check-in."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'nao_autenticado', 'erro': 'É necessário estar logado.'}, status=401)
    
    try:
        payload = json.loads(request.body or "{}")
        codigo = str(payload.get("codigo", "")).strip()
        if not codigo:
            return JsonResponse({'status': 'codigo_vazio', 'erro': 'Código informado está vazio.'}, status=400)
        
        # Buscar o bilhete pelo código UUID
        bilhete = None
        try:
            from uuid import UUID
            uuid_obj = UUID(codigo)
            bilhete = Bilhete.objects.select_related('pedido', 'pedido__evento', 'pedido__lote').get(codigo=uuid_obj)
        except (ValueError, Bilhete.DoesNotExist):
            # Tentar como string direta se UUID falhar
            bilhete = Bilhete.objects.select_related('pedido', 'pedido__evento', 'pedido__lote').get(codigo__iexact=codigo)
        
        # Verificar status do bilhete
        if bilhete.status == "UTILIZADO":
            return JsonResponse({
                'status': 'ja_utilizado',
                'erro': 'Este bilhete já foi utilizado anteriormente.',
                'data_validacao': bilhete.utilizado_em.isoformat() if bilhete.utilizado_em else '',
                'validado_por': bilhete.pedido.utilizador.get_full_name() or bilhete.pedido.utilizador.get_username() if bilhete.pedido.utilizador else 'Operador'
            })
        
        if bilhete.status != "VALIDO":
            return JsonResponse({
                'status': 'invalido',
                'erro': 'Este bilhete não está em estado válido para uso.',
                'status_atual': bilhete.status
            })
        
        # Marcar como utilizado
        bilhete.status = "UTILIZADO"
        bilhete.utilizado_em = timezone.now()
        # Registrar quem validou (pode ser o próprio usuário ou o operador)
        if request.user.is_authenticated:
            bilhete.pedido.utilizador = request.user
        bilhete.save()
        
        # Atualizar status do pedido se todos os bilhetes foram utilizados
        pedido = bilhete.pedido
        total_utilizados = pedido.bilhetes.filter(status="UTILIZADO").count()
        if total_utilizados >= pedido.quantidade:
            pedido.status = "EXPIRADO"  # ou "CONFIRMADO" dependendo da regra de negócio
            pedido.save()
        
        return JsonResponse({
            'status': 'validado',
            'bilhete': {
                'codigo': str(bilhete.codigo),
                'status': bilhete.get_status_display(),
                'evento': bilhete.pedido.evento.titulo,
                'lote': bilhete.lote.nome,
                'data_validacao': bilhete.utilizado_em.isoformat(),
            },
            'participante': bilhete.nome_participante,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'erro_json', 'erro': 'Dados JSON inválidos.'}, status=400)
    except Exception as error:
        return JsonResponse({'status': 'erro', 'erro': str(error)}, status=500)


# ──────────────────────────────────────────────────────────────────────────────
# MANAGEMENT APIS — Gestão de Eventos (organizador independente / centro)
# ──────────────────────────────────────────────────────────────────────────────

def _get_organizador(request):
    """Resolve o organizador a partir da sessão ou do utilizador autenticado."""
    org_id = request.session.get("organizador_evento_id")
    if org_id:
        try:
            return OrganizadorEvento.objects.get(id=org_id, ativo=True)
        except OrganizadorEvento.DoesNotExist:
            pass
    if request.user.is_authenticated:
        org, _ = OrganizadorEvento.objects.get_or_create(
            slug=f"user-{request.user.id}",
            defaults={
                "nome": getattr(request.user, "nome", "") or request.user.get_username(),
                "email": request.user.email or "",
                "tipo": "OUTRO",
            },
        )
        return org
    return None


def _organizador_evento_check(evento, organizador):
    """Verifica se o evento pertence ao organizador."""
    return evento.organizador_id == organizador.id


def _evento_dashboard_data(evento):
    """Calcula estatísticas do evento."""
    lotes = evento.lotes.all()
    pedidos = evento.pedidos.all()
    bilhetes = Bilhete.objects.filter(pedido__evento=evento)

    total_lotes = lotes.aggregate(
        total=Sum("quantidade_total"),
        vendida=Sum("quantidade_vendida"),
    )
    total_capacidade = total_lotes["total"] or 0
    total_vendidos = total_lotes["vendida"] or 0
    total_disponivel = max(total_capacidade - total_vendidos, 0)

    bilhetes_pagos = bilhetes.filter(pedido__status="PAGO")
    checkins = bilhetes_pagos.filter(status="UTILIZADO")
    receita = pedidos.filter(status="PAGO").aggregate(
        total=Sum("valor_bruto")
    )["total"] or Decimal("0.00")

    ocupacao = round((total_vendidos / total_capacidade * 100), 1) if total_capacidade > 0 else 0

    return {
        "evento": {
            "id": evento.id,
            "titulo": evento.titulo,
            "slug": evento.slug,
            "status": evento.status,
            "data_inicio": evento.data_inicio.isoformat(),
            "data_fim": evento.data_fim.isoformat() if evento.data_fim else "",
            "local": evento.local,
            "cidade": evento.cidade,
            "modalidade": evento.modalidade,
            "imagem_url": _media_url(evento.imagem_capa),
            "descricao": evento.descricao,
            "resumo": evento.resumo,
            "categoria": evento.categoria,
            "comissao_percentual": str(evento.comissao_percentual),
        },
        "stats": {
            "capacidade": total_capacidade,
            "bilhetes_vendidos": total_vendidos,
            "bilhetes_disponiveis": total_disponivel,
            "checkins": checkins.count(),
            "receita": str(receita),
            "moeda": lotes.first().moeda if lotes.exists() else "AOA",
            "ocupacao": ocupacao,
            "total_pedidos": pedidos.count(),
            "pedidos_pagos": pedidos.filter(status="PAGO").count(),
            "pedidos_cancelados": pedidos.filter(status="CANCELADO").count(),
        },
        "lotes": [{
            "id": lote.id,
            "nome": lote.nome,
            "preco": str(lote.preco),
            "moeda": lote.moeda,
            "quantidade_total": lote.quantidade_total,
            "quantidade_vendida": lote.quantidade_vendida,
            "lugares_disponiveis": lote.lugares_disponiveis,
            "activo": lote.activo,
            "percentual_vendido": round(lote.quantidade_vendida / lote.quantidade_total * 100, 1) if lote.quantidade_total > 0 else 0,
        } for lote in lotes],
    }


def _lote_payload(lote):
    return {
        "id": lote.id,
        "nome": lote.nome,
        "descricao": lote.descricao,
        "texto_ingresso": lote.texto_ingresso,
        "beneficios": lote.beneficios,
        "regras": lote.regras,
        "cor_primaria": lote.cor_primaria,
        "cor_secundaria": lote.cor_secundaria,
        "preco": str(lote.preco),
        "moeda": lote.moeda,
        "quantidade_total": lote.quantidade_total,
        "quantidade_vendida": lote.quantidade_vendida,
        "lugares_disponiveis": lote.lugares_disponiveis,
        "activo": lote.activo,
        "inicio_vendas": lote.inicio_vendas.isoformat() if lote.inicio_vendas else "",
        "fim_vendas": lote.fim_vendas.isoformat() if lote.fim_vendas else "",
        "ordem": lote.ordem,
        "percentual_vendido": round(lote.quantidade_vendida / lote.quantidade_total * 100, 1) if lote.quantidade_total > 0 else 0,
    }


def _pedido_payload(pedido):
    return {
        "id": pedido.id,
        "referencia": pedido.referencia,
        "nome_comprador": pedido.nome_comprador,
        "email_comprador": pedido.email_comprador,
        "telefone_comprador": pedido.telefone_comprador,
        "quantidade": pedido.quantidade,
        "valor_bruto": str(pedido.valor_bruto),
        "valor_comissao": str(pedido.valor_comissao),
        "moeda": pedido.moeda,
        "status": pedido.status,
        "lote_nome": pedido.lote.nome,
        "criado_em": pedido.criado_em.isoformat(),
        "pago_em": pedido.pago_em.isoformat() if pedido.pago_em else "",
    }


def _bilhete_payload(bilhete):
    return {
        "id": bilhete.id,
        "codigo": str(bilhete.codigo),
        "nome_participante": bilhete.nome_participante,
        "email_participante": bilhete.email_participante,
        "status": bilhete.status,
        "lote_nome": bilhete.lote.nome,
        "pedido_referencia": bilhete.pedido.referencia,
        "emitido_em": bilhete.emitido_em.isoformat(),
        "utilizado_em": bilhete.utilizado_em.isoformat() if bilhete.utilizado_em else "",
    }


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def gestao_evento_dashboard(request, evento_id):
    """Dashboard/visão geral de um evento específico."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)
    evento = get_object_or_404(EventoMarketplace, id=evento_id)
    if not _organizador_evento_check(evento, organizador):
        return JsonResponse({"detail": "Sem permissão."}, status=403)
    return JsonResponse(_evento_dashboard_data(evento))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def gestao_evento_lotes(request, evento_id):
    """Lista e cria tipos de bilhete (LoteBilhete) de um evento."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)
    evento = get_object_or_404(EventoMarketplace, id=evento_id)
    if not _organizador_evento_check(evento, organizador):
        return JsonResponse({"detail": "Sem permissão."}, status=403)

    if request.method == "GET":
        lotes = evento.lotes.all().order_by("ordem", "preco")
        return JsonResponse({"lotes": [_lote_payload(l) for l in lotes]})

    try:
        payload = json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": "JSON inválido."}, status=400)

    nome = str(payload.get("nome", "")).strip()
    preco = payload.get("preco")
    quantidade = payload.get("quantidade_total")
    if not nome or preco is None or not quantidade:
        return JsonResponse({"detail": "Nome, preço e quantidade são obrigatórios."}, status=400)

    try:
        preco = Decimal(str(preco))
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        return JsonResponse({"detail": "Preço ou quantidade inválidos."}, status=400)

    if quantidade < 1:
        return JsonResponse({"detail": "Quantidade deve ser pelo menos 1."}, status=400)

    lote = LoteBilhete.objects.create(
        evento=evento,
        nome=nome,
        descricao=str(payload.get("descricao", "")).strip(),
        texto_ingresso=str(payload.get("texto_ingresso", "")).strip(),
        beneficios=str(payload.get("beneficios", "")).strip(),
        regras=str(payload.get("regras", "")).strip(),
        cor_primaria=str(payload.get("cor_primaria", "#0F6B8A")),
        cor_secundaria=str(payload.get("cor_secundaria", "#EAF8FA")),
        preco=preco,
        moeda=str(payload.get("moeda", "AOA")),
        quantidade_total=quantidade,
        activo=bool(payload.get("activo", True)),
        inicio_vendas=payload.get("inicio_vendas") or None,
        fim_vendas=payload.get("fim_vendas") or None,
        ordem=payload.get("ordem", 0),
    )
    return JsonResponse({"ok": True, "lote": _lote_payload(lote)}, status=201)


@csrf_exempt
@require_http_methods(["PATCH", "DELETE"])
def gestao_evento_lote_detail(request, evento_id, lote_id):
    """Edita ou remove um tipo de bilhete."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)
    evento = get_object_or_404(EventoMarketplace, id=evento_id)
    if not _organizador_evento_check(evento, organizador):
        return JsonResponse({"detail": "Sem permissão."}, status=403)
    lote = get_object_or_404(LoteBilhete, id=lote_id, evento=evento)

    if request.method == "DELETE":
        if lote.quantidade_vendida > 0:
            return JsonResponse({"detail": "Não é possível remover um lote com bilhetes vendidos."}, status=400)
        lote.delete()
        return JsonResponse({"ok": True})

    try:
        payload = json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": "JSON inválido."}, status=400)

    if "nome" in payload:
        lote.nome = str(payload["nome"]).strip()
    if "descricao" in payload:
        lote.descricao = str(payload["descricao"]).strip()
    if "texto_ingresso" in payload:
        lote.texto_ingresso = str(payload["texto_ingresso"]).strip()
    if "beneficios" in payload:
        lote.beneficios = str(payload["beneficios"]).strip()
    if "regras" in payload:
        lote.regras = str(payload["regras"]).strip()
    if "cor_primaria" in payload:
        lote.cor_primaria = str(payload["cor_primaria"])
    if "cor_secundaria" in payload:
        lote.cor_secundaria = str(payload["cor_secundaria"])
    if "preco" in payload:
        lote.preco = Decimal(str(payload["preco"]))
    if "quantidade_total" in payload:
        nova_qtd = int(payload["quantidade_total"])
        if nova_qtd < lote.quantidade_vendida:
            return JsonResponse({"detail": f"Quantidade não pode ser inferior aos {lote.quantidade_vendida} bilhetes já vendidos."}, status=400)
        lote.quantidade_total = nova_qtd
    if "activo" in payload:
        lote.activo = bool(payload["activo"])
    if "inicio_vendas" in payload:
        lote.inicio_vendas = payload["inicio_vendas"] or None
    if "fim_vendas" in payload:
        lote.fim_vendas = payload["fim_vendas"] or None
    if "ordem" in payload:
        lote.ordem = int(payload["ordem"])
    lote.save()
    return JsonResponse({"ok": True, "lote": _lote_payload(lote)})


@csrf_exempt
@require_http_methods(["GET"])
def gestao_evento_vendas(request, evento_id):
    """Lista pedidos/vendas de um evento."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)
    evento = get_object_or_404(EventoMarketplace, id=evento_id)
    if not _organizador_evento_check(evento, organizador):
        return JsonResponse({"detail": "Sem permissão."}, status=403)

    status_filter = request.GET.get("status", "")
    q = PedidoBilhete.objects.filter(evento=evento).select_related("lote")
    if status_filter:
        q = q.filter(status=status_filter)

    search = request.GET.get("q", "").strip()
    if search:
        q = q.filter(
            Q(nome_comprador__icontains=search) |
            Q(email_comprador__icontains=search) |
            Q(referencia__icontains=search)
        )

    pedidos = q.order_by("-criado_em")
    return JsonResponse({
        "pedidos": [_pedido_payload(p) for p in pedidos],
        "total": pedidos.count(),
    })


@csrf_exempt
@require_http_methods(["GET"])
def gestao_evento_participantes(request, evento_id):
    """Lista participantes (bilhetes) de um evento."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)
    evento = get_object_or_404(EventoMarketplace, id=evento_id)
    if not _organizador_evento_check(evento, organizador):
        return JsonResponse({"detail": "Sem permissão."}, status=403)

    status_filter = request.GET.get("status", "")
    q = Bilhete.objects.filter(pedido__evento=evento).select_related("lote", "pedido")
    if status_filter:
        q = q.filter(status=status_filter)

    search = request.GET.get("q", "").strip()
    if search:
        q = q.filter(
            Q(nome_participante__icontains=search) |
            Q(email_participante__icontains=search) |
            Q(codigo__icontains=search)
        )

    bilhetes = q.order_by("-emitido_em")
    return JsonResponse({
        "participantes": [_bilhete_payload(b) for b in bilhetes],
        "total": bilhetes.count(),
        "checkins": bilhetes.filter(status="UTILIZADO").count(),
    })


@csrf_exempt
@require_http_methods(["POST"])
def gestao_evento_upload_capa(request, evento_id):
    """Upload de imagem de capa do evento."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)
    evento = get_object_or_404(EventoMarketplace, id=evento_id)
    if not _organizador_evento_check(evento, organizador):
        return JsonResponse({"detail": "Sem permissão."}, status=403)

    imagem = request.FILES.get("imagem_capa")
    if not imagem:
        return JsonResponse({"detail": "Nenhuma imagem enviada."}, status=400)

    evento.imagem_capa = imagem
    evento.save(update_fields=["imagem_capa"])
    return JsonResponse({"ok": True, "imagem_url": _media_url(evento.imagem_capa)})


@csrf_exempt
@require_http_methods(["PATCH"])
def gestao_evento_update(request, evento_id):
    """Atualiza informações básicas do evento."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)
    evento = get_object_or_404(EventoMarketplace, id=evento_id)
    if not _organizador_evento_check(evento, organizador):
        return JsonResponse({"detail": "Sem permissão."}, status=403)

    try:
        payload = json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": "JSON inválido."}, status=400)

    updatable = ["titulo", "resumo", "descricao", "categoria", "modalidade", "local", "cidade", "provincia", "url_online", "status"]
    for field in updatable:
        if field in payload:
            setattr(evento, field, payload[field])
    evento.save()
    return JsonResponse({"ok": True, "evento": _evento_dashboard_data(evento)["evento"]})


@csrf_exempt
@require_http_methods(["POST"])
def gestao_evento_criar(request):
    """Cria um novo evento para o organizador."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)

    try:
        payload = json.loads(request.body or "{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": "JSON inválido."}, status=400)

    titulo = str(payload.get("titulo", "")).strip()
    descricao = str(payload.get("descricao", "")).strip()
    data_inicio = payload.get("data_inicio")

    if not titulo or not descricao or not data_inicio:
        return JsonResponse({"detail": "Título, descrição e data de início são obrigatórios."}, status=400)

    try:
        dt_inicio = timezone.datetime.fromisoformat(str(data_inicio).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return JsonResponse({"detail": "Data de início inválida."}, status=400)

    evento = EventoMarketplace.objects.create(
        organizador=organizador,
        titulo=titulo,
        resumo=str(payload.get("resumo", "")).strip(),
        descricao=descricao,
        categoria=str(payload.get("categoria", "Geral")).strip(),
        modalidade=str(payload.get("modalidade", "PRESENCIAL")),
        data_inicio=dt_inicio,
        local=str(payload.get("local", "")).strip(),
        cidade=str(payload.get("cidade", "")).strip(),
        provincia=str(payload.get("provincia", "")).strip(),
        url_online=str(payload.get("url_online", "")).strip(),
        status="RASCUNHO",
    )
    return JsonResponse({"ok": True, "evento": _evento_dashboard_data(evento)["evento"]}, status=201)


@csrf_exempt
@require_http_methods(["GET"])
def gestao_eventos_lista(request):
    """Lista todos os eventos do organizador."""
    organizador = _get_organizador(request)
    if not organizador:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)

    eventos = EventoMarketplace.objects.filter(organizador=organizador).order_by("-data_inicio")
    result = []
    for ev in eventos:
        lotes = ev.lotes.all()
        total_vendidos = sum(l.quantidade_vendida for l in lotes)
        total_capacidade = sum(l.quantidade_total for l in lotes)
        result.append({
            "id": ev.id,
            "titulo": ev.titulo,
            "slug": ev.slug,
            "status": ev.status,
            "data_inicio": ev.data_inicio.isoformat(),
            "data_fim": ev.data_fim.isoformat() if ev.data_fim else "",
            "local": ev.local,
            "cidade": ev.cidade,
            "modalidade": ev.modalidade,
            "imagem_url": _media_url(ev.imagem_capa),
            "bilhetes_vendidos": total_vendidos,
            "capacidade": total_capacidade,
        })
    return JsonResponse({"eventos": result})
