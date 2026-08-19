"""Valida a ligação e inventaria a base configurada sem inserir, alterar ou apagar dados."""

import os
import sys
from pathlib import Path

import django


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
django.setup()

from biblioteca.models import Livro
from cursos_app.models import Curso, Turma
from cursovideoapp.models import Aula, Curso_video, TurmaVideo
from gestoreduka.models import CentroDeFormacao


def main():
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL não está configurada; a validação de produção não será executada.")

    print("VALIDACAO_PRODUCAO_INICIO")
    print(f"centros={CentroDeFormacao.objects.count()}")
    print(f"cursos_presenciais={Curso.objects.count()}")
    print(f"cursos_publicados={Curso.objects.filter(ativo=True, publicado=True).count()}")
    print(f"turmas={Turma.objects.count()}")
    print(f"cursos_video={Curso_video.objects.count()}")
    print(f"aulas_video={Aula.objects.count()}")
    print(f"turmas_video={TurmaVideo.objects.count()}")
    print(f"livros={Livro.objects.count()}")
    print("VALIDACAO_PRODUCAO_FIM")


if __name__ == "__main__":
    main()
