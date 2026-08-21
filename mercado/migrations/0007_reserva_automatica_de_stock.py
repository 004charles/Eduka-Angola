from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("mercado", "0006_corrigir_imagens_estaticas_catalogo_demonstracao"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedidomercado",
            name="reserva_expira_em",
            field=models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name="pedidomercado",
            name="reserva_liberada_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="pedidomercado",
            name="reserva_ativa",
            field=models.BooleanField(default=False),
        ),
    ]
