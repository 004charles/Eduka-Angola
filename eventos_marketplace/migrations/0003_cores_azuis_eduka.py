from django.db import migrations, models


OLD_PRIMARY = "#6D28D9"
OLD_SECONDARY = "#EEF2FF"
NEW_PRIMARY = "#0F6B8A"
NEW_SECONDARY = "#EAF8FA"


def aplicar_azul_eduka(apps, schema_editor):
    LoteBilhete = apps.get_model("eventos_marketplace", "LoteBilhete")
    LoteBilhete.objects.filter(cor_primaria__iexact=OLD_PRIMARY).update(cor_primaria=NEW_PRIMARY)
    LoteBilhete.objects.filter(cor_secundaria__iexact=OLD_SECONDARY).update(cor_secundaria=NEW_SECONDARY)


def reverter_azul_eduka(apps, schema_editor):
    LoteBilhete = apps.get_model("eventos_marketplace", "LoteBilhete")
    LoteBilhete.objects.filter(cor_primaria__iexact=NEW_PRIMARY).update(cor_primaria=OLD_PRIMARY)
    LoteBilhete.objects.filter(cor_secundaria__iexact=NEW_SECONDARY).update(cor_secundaria=OLD_SECONDARY)


class Migration(migrations.Migration):
    dependencies = [("eventos_marketplace", "0002_lotebilhete_beneficios_lotebilhete_cor_primaria_and_more")]

    operations = [
        migrations.AlterField(
            model_name="lotebilhete",
            name="cor_primaria",
            field=models.CharField(
                default=NEW_PRIMARY,
                help_text="Azul Edukangola em hexadecimal, por exemplo #0F6B8A.",
                max_length=7,
                verbose_name="Cor principal",
            ),
        ),
        migrations.AlterField(
            model_name="lotebilhete",
            name="cor_secundaria",
            field=models.CharField(
                default=NEW_SECONDARY,
                help_text="Fundo azul claro em hexadecimal, por exemplo #EAF8FA.",
                max_length=7,
                verbose_name="Cor secundária",
            ),
        ),
        migrations.RunPython(aplicar_azul_eduka, reverter_azul_eduka),
    ]
