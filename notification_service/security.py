import hashlib
import hmac
import time


class InvalidEventSignature(ValueError):
    pass


def sign_event(raw_body: bytes, secret: str, timestamp: str) -> str:
    message = f"{timestamp}.".encode("utf-8") + raw_body
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def verify_event_signature(raw_body: bytes, signature: str, secret: str, *, now: int | None = None, tolerance_seconds: int = 300) -> None:
    if not secret:
        raise InvalidEventSignature("Segredo de eventos não configurado")
    pairs = dict(part.split("=", 1) for part in signature.split(",") if "=" in part)
    timestamp = pairs.get("t")
    received = pairs.get("v1")
    if not timestamp or not received:
        raise InvalidEventSignature("Assinatura incompleta")
    try:
        timestamp_int = int(timestamp)
    except ValueError as exc:
        raise InvalidEventSignature("Timestamp inválido") from exc
    current = int(time.time()) if now is None else now
    if abs(current - timestamp_int) > tolerance_seconds:
        raise InvalidEventSignature("Evento fora da janela de tolerância")
    expected = sign_event(raw_body, secret, timestamp).split("v1=", 1)[1]
    if not hmac.compare_digest(expected, received):
        raise InvalidEventSignature("Assinatura inválida")
