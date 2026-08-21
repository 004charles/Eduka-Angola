"""Corrige as vagas disponíveis da turma demonstrativa em bases já migradas."""

from django.db import migrations
from django.db.models import F


def correct_test_class_capacity(apps, schema_editor):
    Turma = apps.get_model("cursos_app", "Turma")
    Turma.objects.filter(codigo="EDKZANGO01").update(
        vagas_disponiveis=F("vagas_totais") - F("vagas_ocupadas")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("cursos_app", "0036_seed_filial_teste_zango"),
    ]

    operations = [
        migrations.RunPython(correct_test_class_capacity, migrations.RunPython.noop),
    ]
