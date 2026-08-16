import os
import sys
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
os.environ.pop("DATABASE_URL", None)

import django
from django.utils import timezone

django.setup()

from eventos_marketplace.models import EventoMarketplace, LoteBilhete, OrganizadorEvento


organizador, _ = OrganizadorEvento.objects.update_or_create(
    slug="gdg-luanda",
    defaults={
        "nome": "GDG Luanda",
        "tipo": "COMUNIDADE",
        "descricao": "Organizador de comunidade tecnológica. Registo de demonstração para validar o marketplace de bilhetes da Edukangola.",
        "email": "eventos@gdg-luanda.example",
        "website": "https://developers.google.com/community/gdg",
        "verificado": False,
        "ativo": True,
    },
)

inicio = timezone.now() + timedelta(days=55)
fim = inicio + timedelta(hours=8)
evento, _ = EventoMarketplace.objects.update_or_create(
    slug="gdg-luanda-tech-community-meetup-demo",
    defaults={
        "organizador": organizador,
        "titulo": "GDG Luanda Tech Community Meetup 2026",
        "resumo": "Um encontro de demonstração para testar a compra de bilhetes de eventos tecnológicos na Edukangola.",
        "descricao": "Evento de demonstração do marketplace de bilhetes da Edukangola. Inclui palestras, networking e sessões práticas sobre desenvolvimento de software, cloud e inteligência artificial. Este registo serve apenas para validar o fluxo técnico e não representa uma publicação oficial da Google.",
        "categoria": "Tecnologia e Comunidade",
        "modalidade": "PRESENCIAL",
        "data_inicio": inicio,
        "data_fim": fim,
        "local": "Centro de Conferências de Talatona",
        "cidade": "Luanda",
        "provincia": "Luanda",
        "status": "PUBLICADO",
        "destaque": True,
        "comissao_percentual": Decimal("15.00"),
    },
)

lotes = [
    ("Early Bird", Decimal("5000.00"), 120, 1, "Entrada antecipada", "Acesso geral\nNetworking", "Bilhete pessoal e intransmissível", "#6D28D9", "#EEF2FF"),
    ("Bilhete Regular", Decimal("7500.00"), 250, 2, "Entrada geral", "Acesso geral\nNetworking\nCertificado de participação", "Apresente o QR no acesso", "#0F766E", "#ECFDF5"),
]
for nome, preco, quantidade, ordem, texto_ingresso, beneficios, regras, cor_primaria, cor_secundaria in lotes:
    LoteBilhete.objects.update_or_create(
        evento=evento,
        nome=nome,
        defaults={
            "descricao": "Bilhete digital com entrada no evento e acesso às sessões gerais.",
            "texto_ingresso": texto_ingresso,
            "beneficios": beneficios,
            "regras": regras,
            "cor_primaria": cor_primaria,
            "cor_secundaria": cor_secundaria,
            "preco": preco,
            "moeda": "AOA",
            "quantidade_total": quantidade,
            "activo": True,
            "ordem": ordem,
        },
    )

print({
    "organizador_id": organizador.id,
    "evento_id": evento.id,
    "evento_slug": evento.slug,
    "lotes": list(evento.lotes.values("id", "nome", "preco", "quantidade_total", "quantidade_vendida")),
})
