"""Publicação de eventos para o serviço separado de notificações.

A função é deliberadamente pequena para poder ser chamada por sinais, serviços de
negócio ou uma futura fila de saída transaccional. O segredo e a URL existem
apenas no ambiente do processo Django.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from datetime import datetime, timezone
from typing import Any

import requests
from django.utils import timezone as django_timezone

from .models import EventoNotificacaoOutbox


class NotificationEventPublishError(RuntimeError):
    """Indica que o serviço separado não aceitou o evento."""


def queue_notification_event(event_type: str, event_id: str, payload: dict[str, Any], *, occurred_at: datetime | None = None) -> EventoNotificacaoOutbox:
    """Regista o evento no outbox para publicação eventual e idempotente."""
    moment = occurred_at or django_timezone.now()
    event, _ = EventoNotificacaoOutbox.objects.get_or_create(
        event_id=event_id,
        defaults={
            "event_type": event_type,
            "payload": payload,
            "occurred_at": moment,
        },
    )
    return event


def _signature(body: bytes, secret: str, timestamp: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        f"{timestamp}.".encode("utf-8") + body,
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={digest}"


def publish_notification_event(
    event_type: str,
    event_id: str,
    payload: dict[str, Any],
    *,
    occurred_at: datetime | None = None,
    timeout: float = 4.0,
) -> dict[str, Any]:
    """Publica um evento assinado e devolve a confirmação do gateway.

    Em desenvolvimento, se a URL ou o segredo não estiverem configurados, a
    publicação é ignorada explicitamente. Em produção, a ausência de ambos é
    erro para impedir uma falsa sensação de entrega.
    """
    service_url = os.getenv("NOTIFICATION_SERVICE_URL", "").rstrip("/")
    secret = os.getenv("NOTIFICATION_SERVICE_SHARED_SECRET", "")
    if not service_url and not secret:
        return {"accepted": False, "disabled": True, "event_id": event_id}
    if not service_url or not secret:
        raise NotificationEventPublishError("URL e segredo do serviço de notificações são obrigatórios")
    moment = occurred_at or datetime.now(timezone.utc)
    body = json.dumps(
        {
            "event_id": event_id,
            "event_type": event_type,
            "occurred_at": moment.isoformat(),
            "source": "edukangola-django",
            "schema_version": 1,
            "payload": payload,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    timestamp = str(int(time.time()))
    try:
        response = requests.post(
            f"{service_url}/v1/events",
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Edukangola-Event-Signature": _signature(body, secret, timestamp),
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as exc:
        raise NotificationEventPublishError(f"Falha ao publicar o evento {event_id}") from exc
