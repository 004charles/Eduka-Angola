"""Emite um código temporário de cadastro para uma conta pendente específica."""

import os
import secrets
import sys
from pathlib import Path


EMAIL = "muquissizangui@gmail.com"


def main() -> int:
    os.environ.pop("DATABASE_URL", None)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    import django

    django.setup()

    from usuarios.models import CodigoVerificacao, Usuario

    usuario = Usuario.objects.filter(email=EMAIL, tipo_usuario="ALUNO").first()
    if not usuario:
        print("ERRO: conta pendente não encontrada")
        return 1

    codigo = f"{secrets.randbelow(1_000_000):06d}"
    CodigoVerificacao.objects.filter(email=EMAIL, tipo="CADASTRO").delete()
    CodigoVerificacao.objects.create(email=EMAIL, codigo=codigo, tipo="CADASTRO")
    print(codigo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
