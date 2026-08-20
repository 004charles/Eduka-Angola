"""Normalização de URLs de ficheiros públicos entre Vercel e a API Django."""

from django.conf import settings


def public_media_url(url):
    """Devolve uma URL absoluta para caminhos de média locais em produção.

    O frontend é servido em ``www.edukangola.com`` e os uploads pelo Django em
    ``api.edukangola.com``. Armazenamentos como Cloudinary já devolvem URL
    absoluta e permanecem inalterados.
    """
    if not url:
        return ""
    if url.startswith(("https://", "http://", "//")):
        return url
    origin = getattr(settings, "MEDIA_PUBLIC_ORIGIN", "").strip().rstrip("/")
    if not origin:
        return url
    return f"{origin}/{url.lstrip('/')}"
