"""Cria uma unidade demonstrativa e uma turma aberta para validar o checkout por filial."""

from datetime import time, timedelta

from django.db import migrations, transaction
from django.utils import timezone


@transaction.atomic
def seed_test_branch_and_class(apps, schema_editor):
    CentroDeFormacao = apps.get_model("gestoreduka", "CentroDeFormacao")
    Filial = apps.get_model("gestoreduka", "Filial")
    Curso = apps.get_model("cursos_app", "Curso")
    Turma = apps.get_model("cursos_app", "Turma")

    centro = CentroDeFormacao.objects.filter(
        email="gestor.teste@edukangola.local"
    ).first()
    if not centro:
        return

    filial, _ = Filial.objects.update_or_create(
        email="unidade.zango.teste@edukangola.local",
        defaults={
            "centro_principal": centro,
            "nome": "Unidade Zango — Teste Edukangola",
            "endereco": "Zango III, Viana, Luanda — unidade de demonstração",
            "telefone": "+244 900 000 001",
            "whatsapp": "+244900000001",
            "latitude": "-8.8999000000000000",
            "longitude": "13.3202000000000000",
            "ativo": True,
        },
    )

    curso = Curso.objects.filter(
        centro=centro,
        titulo="Suporte Técnico e Redes",
    ).first()
    if not curso:
        return

    curso.filiais.add(filial)
    hoje = timezone.localdate()
    Turma.objects.update_or_create(
        codigo="EDKZANGO01",
        defaults={
            "curso": curso,
            "filial": filial,
            "nome": "Turma de teste — Unidade Zango",
            "data_inicio": hoje + timedelta(days=14),
            "data_fim": hoje + timedelta(days=98),
            "turno": "TARDE",
            "horario_inicio": time(14, 0),
            "horario_fim": time(17, 0),
            "dias_semana": "TER,QUI",
            "vagas_totais": 20,
            "vagas_ocupadas": 0,
            "vagas_disponiveis": 20,
            "local": "Unidade Zango — Teste Edukangola",
            "sala": "Sala Z-01",
            "status": "ABERTA",
            "observacoes": (
                "Turma demonstrativa para validar a selecção de filial no checkout. "
                "Não representa uma unidade comercial confirmada."
            ),
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("cursos_app", "0035_preencher_capas_catalogo_publico"),
        ("gestoreduka", "0025_remove_feed_reels"),
    ]

    operations = [
        migrations.RunPython(seed_test_branch_and_class, migrations.RunPython.noop),
    ]
