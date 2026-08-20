import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import BibliotecaPessoal, Livro


def _request_data(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (TypeError, ValueError, UnicodeDecodeError):
        return request.POST


def _image_url(request, field):
    if not field:
        return ""
    try:
        if not field.name or not field.storage.exists(field.name):
            return ""
        return request.build_absolute_uri(field.url)
    except (ValueError, OSError):
        return ""


def _seconds_label(seconds):
    minutes, seconds = divmod(seconds or 0, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes:02d}min"
    return f"{minutes}min {seconds:02d}s" if seconds else "Duração a confirmar"


def _book_data(request, book, include_content=False, library_entry=None):
    audio_chapters = list(book.capitulos_audio.all()) if include_content else []
    data = {
        "id": book.id,
        "titulo": book.titulo,
        "slug": book.slug,
        "subtitulo": book.subtitulo,
        "autor": {"nome": book.autor.nome, "slug": book.autor.slug, "pais": book.autor.pais, "biografia": book.autor.biografia, "foto_url": _image_url(request, book.autor.foto)},
        "editora": book.editora,
        "sinopse": book.sinopse,
        "descricao_curta": book.descricao_curta or book.sinopse[:180],
        "capa_url": _image_url(request, book.capa) or book.capa_url,
        "categoria": book.categoria,
        "temas": [item.strip() for item in book.temas.split(",") if item.strip()],
        "idioma": book.idioma,
        "paginas": book.paginas,
        "ano_publicacao": book.ano_publicacao,
        "formato": book.formato,
        "gratuito": book.gratuito,
        "acesso_label": "Leitura gratuita" if book.gratuito else "Acesso reservado",
        "tem_leitura": book.tem_leitura,
        "tem_audio": book.tem_audio,
        "narrador": book.narrador,
        "excerto": book.excerto,
        "em_destaque": book.em_destaque,
        "selecao_semana": book.selecao_semana,
    }
    if library_entry:
        data["biblioteca_pessoal"] = {"guardado": library_entry.guardado, "progresso_leitura": library_entry.progresso_leitura, "pagina_leitura": library_entry.pagina_leitura, "progresso_audio_segundos": library_entry.progresso_audio_segundos}
    if include_content:
        data["conteudo_leitura"] = book.conteudo_leitura
        data["capitulos_audio"] = [{"id": chapter.id, "titulo": chapter.titulo, "ordem": chapter.ordem, "duracao_segundos": chapter.duracao_segundos, "duracao_label": _seconds_label(chapter.duracao_segundos), "audio_url": _image_url(request, chapter.audio), "descricao": chapter.descricao} for chapter in audio_chapters]
    return data


def _published_books():
    return Livro.objects.filter(estado=Livro.ESTADO_PUBLICADO, direitos_confirmados=True).select_related("autor").prefetch_related("capitulos_audio")


@require_GET
def public_library(request):
    books = list(_published_books())
    featured = next((book for book in books if book.selecao_semana), books[0] if books else None)
    return JsonResponse({
        "destaque": _book_data(request, featured) if featured else None,
        "estante_semana": [_book_data(request, book) for book in books if book != featured][:8],
        "para_ouvir": [_book_data(request, book) for book in books if book.tem_audio][:5],
        "por_carreira": [_book_data(request, book) for book in books if book.categoria in {"Gestão e Negócios", "Tecnologia e Dados", "Idiomas e Comunicação", "Design e Criatividade"}][:8],
        "categorias": sorted({book.categoria for book in books}),
        "total": len(books),
    })


@require_GET
def public_book_detail(request, slug):
    book = get_object_or_404(_published_books(), slug=slug)
    related = _published_books().filter(categoria=book.categoria).exclude(pk=book.pk)[:6]
    return JsonResponse({"livro": _book_data(request, book), "relacionados": [_book_data(request, item) for item in related]})


@login_required
@require_GET
def my_library(request):
    entries = BibliotecaPessoal.objects.filter(usuario=request.user, guardado=True).select_related("livro", "livro__autor").prefetch_related("livro__capitulos_audio")
    return JsonResponse({"livros": [_book_data(request, entry.livro, library_entry=entry) for entry in entries]})


@login_required
@require_POST
def toggle_library_book(request, slug):
    book = get_object_or_404(_published_books(), slug=slug)
    entry, _ = BibliotecaPessoal.objects.get_or_create(usuario=request.user, livro=book)
    entry.guardado = not entry.guardado
    entry.save(update_fields=("guardado", "ultima_atividade"))
    return JsonResponse({"guardado": entry.guardado, "mensagem": "Livro guardado na sua biblioteca." if entry.guardado else "Livro removido da sua biblioteca."})


@login_required
@require_GET
def read_book(request, slug):
    book = get_object_or_404(_published_books(), slug=slug)
    if not book.tem_leitura:
        return JsonResponse({"detail": "Este livro ainda não tem leitura digital disponível."}, status=404)
    entry, _ = BibliotecaPessoal.objects.get_or_create(usuario=request.user, livro=book)
    if not entry.guardado:
        entry.guardado = True
        entry.save(update_fields=("guardado", "ultima_atividade"))
    return JsonResponse({"livro": _book_data(request, book, include_content=True, library_entry=entry)})


@login_required
@require_POST
def update_reading_progress(request, slug):
    book = get_object_or_404(_published_books(), slug=slug)
    entry, _ = BibliotecaPessoal.objects.get_or_create(usuario=request.user, livro=book)
    payload = _request_data(request)
    try:
        progress = max(0, min(100, int(payload.get("progresso", 0))))
        page = max(0, int(payload.get("pagina", 0)))
    except (TypeError, ValueError):
        return JsonResponse({"detail": "Progresso inválido."}, status=400)
    entry.progresso_leitura = progress
    entry.pagina_leitura = page
    entry.save(update_fields=("progresso_leitura", "pagina_leitura", "ultima_atividade"))
    return JsonResponse({"progresso_leitura": entry.progresso_leitura, "pagina_leitura": entry.pagina_leitura})
