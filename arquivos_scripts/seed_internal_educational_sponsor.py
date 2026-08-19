"""Cria um único patrocínio interno de demonstração, sem rede nem destino externo."""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.pop("DATABASE_URL", None)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")

import django

django.setup()

from core.models import Publicidade


def main():
    publicidade, created = Publicidade.objects.update_or_create(
        titulo="Bolsas e oportunidades para avançar",
        posicao="GERAL",
        defaults={
            "subtitulo": "Conheça oportunidades educativas e apoios publicados pela Edukangola para ajudar a planear o seu próximo passo.",
            "tag_label": "Selecção Edukangola",
            "descricao": "Vitrina educativa interna, sem redireccionamentos nem redes publicitárias externas.",
            "url_destino": "/bolsas",
            "texto_botao": "Explorar oportunidades",
            "ativo": True,
        },
    )
    print(f"Patrocínio interno {'criado' if created else 'actualizado'}: {publicidade.id}")


if __name__ == "__main__":
    main()
