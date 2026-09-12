import json
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import EventoMarketplace, LoteBilhete, PedidoBilhete
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
                'data_validacao': bilhete.data_validacao.isoformat() if bilhete.data_validacao else '',
                'validado_por': bilhete.pedido.utilizador.nome if bilhete.pedido.utilizador else 'Operador'
            })
        
        if bilhete.status != "VALIDO":
            return JsonResponse({
                'status': 'invalido',
                'erro': 'Este bilhete não está em estado válido para uso.',
                'status_atual': bilhete.status
            })
        
        # Marcar como utilizado
        from django.utils import timezone
        bilhete.status = "UTILIZADO"
        bilhete.data_validacao = timezone.now()
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
                'data_validacao': bilhete.data_validacao.isoformat(),
            },
            'participante': bilhete.nome_participante,
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'erro_json', 'erro': 'Dados JSON inválidos.'}, status=400)
    except Exception as error:
        return JsonResponse({'status': 'erro', 'erro': str(error)}, status=500)
