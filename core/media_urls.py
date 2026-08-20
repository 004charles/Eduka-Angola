"""Normalização de URLs de ficheiros públicos entre Vercel e a API Django."""

from django.conf import settings
from django.templatetags.static import static


MUNDOTEC_CAPA_PREFIX = "cursos/capas/mundotec/"


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


def public_course_cover_url(field, fallback_static_path):
    """Resolve capas locais, incluindo recursos Mundo da Tecnologia versionados.

    As capas da Mundo da Tecnologia são mantidas em ``static`` para continuarem
    acessíveis mesmo quando o filesystem efémero do Render é recriado.
    """
    name = getattr(field, "name", "") or ""
    if name.startswith(MUNDOTEC_CAPA_PREFIX):
        return public_media_url(static(f"assets/images/course/mundotec/{name.rsplit('/', 1)[-1]}"))
    try:
        if field and name and field.storage.exists(name):
            return public_media_url(field.url)
    except Exception:
        pass
    return public_media_url(static(fallback_static_path))
