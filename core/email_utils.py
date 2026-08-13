"""
Utilitário para envio de emails via Brevo HTTP API.
Usa porta 443 (HTTPS) em vez de 587 (SMTP) — funciona em qualquer servidor cloud.
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def enviar_email_brevo(to_email, subject, html_content, text_content=None, to_name=None):
    """
    Envia email via Brevo REST API (HTTP/443).
    Funciona no Render e qualquer cloud que bloqueie SMTP.
    """
    api_key = getattr(settings, 'BREVO_API_KEY', '')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@edukangola.com')
    from_name = getattr(settings, 'DEFAULT_FROM_NAME', 'EdukAngola')

    if not api_key:
        logger.error("[BREVO] BREVO_API_KEY não configurada!")
        if settings.DEBUG:
            logger.info(f"[BREVO] [DEBUG MODE] Simulação de envio com sucesso para {to_email} (sem API KEY)")
            print(f"\n================ MOCK EMAIL SENT (DEBUG - SEM API KEY) ================")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Body: {text_content or html_content}")
            print(f"=========================================================\n")
            return True
        return False

    payload = {
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "to": [
            {"email": to_email, "name": to_name or to_email}
        ],
        "subject": subject,
        "htmlContent": html_content,
    }

    if text_content:
        payload["textContent"] = text_content

    try:
        logger.info(f"[BREVO] A enviar email para {to_email} via API HTTP...")
        response = requests.post(
            BREVO_API_URL,
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=15
        )

        if response.status_code in (200, 201):
            logger.info(f"[BREVO] ✅ Email enviado com sucesso para {to_email}")
            return True
        else:
            logger.error(f"[BREVO] ❌ Erro {response.status_code}: {response.text}")
            if settings.DEBUG:
                logger.info(f"[BREVO] [DEBUG MODE] Simulação de envio com sucesso para {to_email} (fallback console)")
                print(f"\n================ MOCK EMAIL SENT (DEBUG - ERRO API) ================")
                print(f"To: {to_email}")
                print(f"Subject: {subject}")
                print(f"Body: {text_content or html_content}")
                print(f"=========================================================\n")
                return True
            return False

    except requests.exceptions.Timeout:
        logger.error(f"[BREVO] ❌ Timeout ao enviar para {to_email}")
        if settings.DEBUG:
            logger.info(f"[BREVO] [DEBUG MODE] Simulação de envio com sucesso para {to_email} após timeout")
            print(f"\n================ MOCK EMAIL SENT (DEBUG - TIMEOUT) ================")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"=========================================================\n")
            return True
        return False
    except Exception as e:
        logger.error(f"[BREVO] ❌ Erro inesperado para {to_email}: {type(e).__name__}: {e}")
        if settings.DEBUG:
            logger.info(f"[BREVO] [DEBUG MODE] Simulação de envio com sucesso para {to_email} após erro")
            print(f"\n================ MOCK EMAIL SENT (DEBUG - ERRO INESPERADO) ================")
            print(f"To: {to_email}")
            print(f"Subject: {subject}")
            print(f"=========================================================\n")
            return True
        return False
