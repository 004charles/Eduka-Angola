"""Entrega da SPA React compilada pelo mesmo serviço Django em produção."""

import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.urls import Resolver404, resolve
from django.views.decorators.cache import never_cache


def _frontend_dist():
    return Path(getattr(settings, 'REACT_FRONTEND_DIST', Path(settings.BASE_DIR) / 'frontend' / 'dist')).resolve()


def _safe_file(relative_path):
    root = _frontend_dist()
    candidate = (root / relative_path).resolve()
    if root not in candidate.parents or not candidate.is_file():
        raise Http404('Recurso React não encontrado.')
    return candidate


@never_cache
def react_application(request):
    """Devolve o index Vite para que as rotas da SPA sobrevivam a um refresh."""
    index = _safe_file('index.html')
    return FileResponse(index.open('rb'), content_type='text/html; charset=utf-8')


def react_asset(request, asset_path):
    asset = _safe_file(asset_path)
    content_type, _ = mimetypes.guess_type(asset.name)
    response = FileResponse(asset.open('rb'), content_type=content_type or 'application/octet-stream')
    response['Cache-Control'] = 'public, max-age=31536000, immutable' if asset_path.startswith('assets/') else 'no-cache'
    return response


def backend_proxy(request, backend_path):
    """Mantém o prefixo /backend usado pelo React, sem depender do proxy Vite em produção."""
    try:
        match = resolve(f'/{backend_path}')
    except Resolver404 as error:
        raise Http404('Endpoint backend não encontrado.') from error
    return match.func(request, *match.args, **match.kwargs)
