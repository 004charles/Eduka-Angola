import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from .contracts import EventAccepted, NotificationEvent
from .security import InvalidEventSignature, verify_event_signature
from .store import EventStore
from .processor import NotificationProcessor


app = FastAPI(title="Edukangola Notification Service", version="0.1.0")
store = EventStore(os.getenv("NOTIFICATION_DATABASE_PATH", "./data/notifications.sqlite3"))
processor = NotificationProcessor(store)


@app.get("/health")
def health():
    return {"ok": True, "service": "notification-service", "accepted_events": store.count_events()}


@app.post("/v1/process-pending")
def process_pending(request: Request):
    expected = os.getenv('NOTIFICATION_WORKER_SECRET', '')
    presented = request.headers.get('X-Notification-Worker-Key', '')
    if not expected or presented != expected:
        raise HTTPException(status_code=401, detail='Não autorizado')
    return processor.process_pending(limit=50)


@app.post("/v1/events", response_model=EventAccepted, status_code=202)
async def ingest_event(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Edukangola-Event-Signature", "")
    try:
        verify_event_signature(
            raw_body,
            signature,
            os.getenv("NOTIFICATION_SERVICE_SHARED_SECRET", ""),
        )
    except InvalidEventSignature as exc:
        raise HTTPException(status_code=401, detail="Evento não autenticado") from exc
    try:
        event = NotificationEvent.model_validate(json.loads(raw_body))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail="Contrato de evento inválido") from exc
    accepted = store.accept_event(event)
    return EventAccepted(event_id=event.event_id, duplicate=not accepted)
