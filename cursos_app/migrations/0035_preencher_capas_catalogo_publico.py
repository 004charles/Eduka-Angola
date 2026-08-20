from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations


ROOT = Path(settings.BASE_DIR)
COURSE_ASSETS = [
    "course-online-01.jpg",
    "course-online-02.jpg",
    "course-online-03.jpg",
    "course-online-04.jpg",
    "course-elegant-01.jpg",
    "course-elegant-02.jpg",
    "course-elegant-03.jpg",
    "course-elegant-04.jpg",
    "course-list-01.jpg",
    "course-list-02.jpg",
    "course-list-03.jpg",
    "course-list-04.jpg",
    "art-course-01.png",
    "art-course-02.png",
    "art-course-03.png",
    "art-course-05.png",
    "medical-course-01.jpg",
    "medical-course-02.jpg",
    "medical-course-03.jpg",
    "coach-course-01.jpg",
]


def _save_cover(instance, field_name, asset_name, prefix):
    source = ROOT / "static" / "assets" / "images" / "course" / asset_name
    if not source.exists():
        return
    with source.open("rb") as handle:
        getattr(instance, field_name).save(f"{prefix}-{instance.pk}-{asset_name}", File(handle), save=True)


def preencher_capas(apps, schema_editor):
    Curso = apps.get_model("cursos_app", "Curso")
    CursoVideo = apps.get_model("cursovideoapp", "Curso_video")

    for index, course in enumerate(Curso.objects.filter(ativo=True, publicado=True).filter(imagem="").order_by("id")):
        _save_cover(course, "imagem", COURSE_ASSETS[index % len(COURSE_ASSETS)], "catalogo")

    for index, course in enumerate(CursoVideo.objects.filter(capa="").order_by("id")):
        _save_cover(course, "capa", COURSE_ASSETS[(index + 4) % len(COURSE_ASSETS)], "video")


class Migration(migrations.Migration):
    dependencies = [("cursos_app", "0034_seed_catalogo_publico_producao")]

    operations = [migrations.RunPython(preencher_capas, migrations.RunPython.noop)]
