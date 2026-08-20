import re
from pathlib import Path

from django.db import migrations
from django.utils.text import slugify


INTERNAL_INSTRUCTOR_EMAIL = 'equipa.formacao@edukangola.com'
BOOK_COVERS = {
    'o-proximo-passo': 'o-proximo-passo.jpg',
    'dados-que-contam-historias': 'dados-que-contam-historias.jpg',
    'palavras-que-abrem-portas': 'palavras-que-abrem-portas.jpg',
    'caderno-de-ideias-visuais': 'caderno-de-ideias-visuais.jpg',
    'ritmo-para-aprender': 'ritmo-para-aprender.jpg',
}


def _unique_slug(CursoVideo, base, current_id):
    candidate = slugify(base)[:50] or f'eduka-video-{current_id}'
    suffix = 2
    while CursoVideo.objects.exclude(pk=current_id).filter(slug=candidate).exists():
        trailer = f'-{suffix}'
        candidate = f'{slugify(base)[:50 - len(trailer)]}{trailer}'
        suffix += 1
    return candidate


def _natural_key(path):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r'(\d+)', path.name)]


def align_platform_catalog(apps, schema_editor):
    Centro = apps.get_model('gestoreduka', 'CentroDeFormacao')
    Curso = apps.get_model('cursos_app', 'Curso')
    Instrutor = apps.get_model('cursos_app', 'Instrutor')
    CursoVideo = apps.get_model('cursovideoapp', 'Curso_video')
    Aula = apps.get_model('cursovideoapp', 'Aula')
    TurmaVideo = apps.get_model('cursovideoapp', 'TurmaVideo')
    Plano = apps.get_model('planos', 'Plano')
    Livro = apps.get_model('biblioteca', 'Livro')

    mundotec = Centro.objects.filter(email='geral@mundotec.ao').first()
    if not mundotec:
        return

    cursos_mundotec = list(Curso.objects.filter(
        centro=mundotec, ativo=True, publicado=True
    ).select_related('categoria').order_by('pk'))
    if not cursos_mundotec:
        return

    project_root = Path(__file__).resolve().parents[2]
    cover_files = sorted(
        (project_root / 'static' / 'assets' / 'images' / 'course' / 'mundotec').glob('*.jpg'),
        key=_natural_key,
    )
    cover_names = [path.name for path in cover_files]
    for index, presencial in enumerate(cursos_mundotec):
        if index < len(cover_names):
            image_name = f'cursos/capas/mundotec/{cover_names[index]}'
            Curso.objects.filter(pk=presencial.pk).update(imagem=image_name)
            presencial.imagem = image_name

    instrutor, _ = Instrutor.objects.get_or_create(
        email=INTERNAL_INSTRUCTOR_EMAIL,
        defaults={
            'nome': 'Equipa Pedagógica Edukangola',
            'titulo': 'Formação digital Edukangola',
            'biografia': 'Equipa interna responsável pela produção e acompanhamento dos cursos em vídeo da Edukangola.',
            'area_especializacao': 'TECNOLOGIA_INFORMACAO',
            'ativo': True,
            'centro_de_formacao_id': None,
            'filial_id': None,
        },
    )
    Instrutor.objects.filter(pk=instrutor.pk).update(centro_de_formacao_id=None, filial_id=None, ativo=True)

    videos = list(CursoVideo.objects.order_by('pk'))
    TurmaVideo.objects.filter(curso_id__in=[video.pk for video in videos]).delete()
    for index, video in enumerate(videos):
        presencial = cursos_mundotec[index % len(cursos_mundotec)]
        video.titulo = presencial.titulo
        video.slug = _unique_slug(CursoVideo, f'eduka-video-{presencial.slug or presencial.titulo}', video.pk)
        video.descricao = presencial.descricao or presencial.descricao_curta or f'Curso em vídeo Edukangola sobre {presencial.titulo}.'
        video.categoria_id = presencial.categoria_id
        video.capa = f'cursos/capas/mundotec/{cover_names[index % len(cover_names)]}' if cover_names else presencial.imagem.name
        video.centro_id = None
        video.instrutor_id = instrutor.pk
        video.is_original_edukangola = True
        video.destaque = index < 8
        video.save(update_fields=['titulo', 'slug', 'descricao', 'categoria', 'capa', 'centro', 'instrutor', 'is_original_edukangola', 'destaque'])
        for lesson_index, lesson in enumerate(Aula.objects.filter(curso_id=video.pk).order_by('ordem', 'pk'), start=1):
            lesson.titulo = [
                f'Introdução a {presencial.titulo}',
                f'Fundamentos de {presencial.titulo}',
                f'Aplicação prática de {presencial.titulo}',
                f'Projecto final de {presencial.titulo}',
            ][min(lesson_index - 1, 3)]
            lesson.save(update_fields=['titulo'])

    Curso.objects.exclude(centro=mundotec).update(publicado=False, ativo=False, destaque=False)
    Centro.objects.exclude(pk=mundotec.pk).update(ativo=False)
    Plano.objects.update(permite_cursos_video=False, limite_cursos_video=0)
    for slug, filename in BOOK_COVERS.items():
        Livro.objects.filter(slug=slug).update(capa_url=f'https://api.edukangola.com/static/assets/images/library/{filename}')


class Migration(migrations.Migration):
    dependencies = [
        ('cursovideoapp', '0020_duvidas_resolvidas'),
        ('cursos_app', '0035_preencher_capas_catalogo_publico'),
        ('biblioteca', '0003_bibliotecapessoal_pagina_leitura'),
        ('planos', '0005_seed_four_center_plans'),
    ]

    operations = [migrations.RunPython(align_platform_catalog, migrations.RunPython.noop)]
