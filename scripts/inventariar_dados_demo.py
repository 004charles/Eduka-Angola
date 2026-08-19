"""Inventário somente de leitura dos dados locais candidatos à migração."""

import os
import sys
from pathlib import Path

import django


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
django.setup()

from biblioteca.models import Livro
from cursos_app.models import Categoria, Curso, Turma
from cursovideoapp.models import Aula, Curso_video, TurmaVideo
from gestoreduka.models import CentroDeFormacao


def resumo(nome, queryset):
    print(f"{nome}={queryset.count()}")


def main():
    print("INVENTARIO_DEMO_INICIO")
    resumo("categorias", Categoria.objects.all())
    resumo("centros_total", CentroDeFormacao.objects.all())
    resumo("centros_ativos", CentroDeFormacao.objects.filter(ativo=True))
    resumo("cursos_presenciais_total", Curso.objects.all())
    resumo("cursos_presenciais_publicados", Curso.objects.filter(ativo=True, publicado=True))
    resumo("turmas_total", Turma.objects.all())
    resumo("turmas_abertas", Turma.objects.filter(status="ABERTA"))
    resumo("cursos_video_total", Curso_video.objects.all())
    resumo("aulas_video_total", Aula.objects.all())
    resumo("turmas_video_total", TurmaVideo.objects.all())
    resumo("livros_total", Livro.objects.all())
    resumo("livros_publicados", Livro.objects.filter(estado=Livro.ESTADO_PUBLICADO))
    print(f"capas_cursos={Curso.objects.exclude(imagem='').count()}")
    print(f"capas_video={Curso_video.objects.exclude(capa='').count()}")
    print(f"capas_livros={Livro.objects.exclude(capa='').count()}")
    print("CENTROS_ATIVOS")
    for centro in CentroDeFormacao.objects.filter(ativo=True).order_by("nome").values_list("nome", "email", "cidade", "provincia"):
        print(" | ".join(valor or "" for valor in centro))
    print("CURSOS_VIDEO")
    for titulo in Curso_video.objects.order_by("titulo").values_list("titulo", flat=True):
        print(titulo)
    print("LIVROS")
    for titulo in Livro.objects.order_by("titulo").values_list("titulo", flat=True):
        print(titulo)
    print("INVENTARIO_DEMO_FIM")


if __name__ == "__main__":
    main()
