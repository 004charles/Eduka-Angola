from django.db import migrations
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError

def drop_phantom_columns(apps, schema_editor):
    try:
        with transaction.atomic():
            with schema_editor.connection.cursor() as cursor:
                # Remove a coluna fantasma que está no Postgres do Render mas já não existe no Django
                cursor.execute("ALTER TABLE pagamentos_configuracaopagamento DROP COLUMN IF EXISTS validar_webhook_signature;")
    except (OperationalError, ProgrammingError):
        # Ignora erros caso esteja no SQLite local que não suporta a mesma sintaxe
        pass

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('pagamentos', '0004_fix_config_pagamento'),
    ]

    operations = [
        migrations.RunPython(drop_phantom_columns),
    ]
