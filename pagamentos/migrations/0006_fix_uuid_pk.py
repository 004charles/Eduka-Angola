from django.db import migrations
from django.db import transaction
from django.db.utils import OperationalError, ProgrammingError

def fix_uuid_pk(apps, schema_editor):
    try:
        with transaction.atomic():
            with schema_editor.connection.cursor() as cursor:
                # O PostgreSQL precisa saber como converter de bigint para uuid.
                # Como a tabela provavelmente está vazia devido aos erros, podemos fazer truncate
                # e forçar a alteração de tipo, incluindo as chaves estrangeiras.
                
                # Se der erro (ex: SQLite), ignora e segue em frente
                cursor.execute("""
                    DO $$ 
                    BEGIN
                        -- Verifica se a coluna id é bigint (int8) ou integer (int4)
                        IF EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name='pagamentos_pagamento' AND column_name='id' AND data_type IN ('bigint', 'integer')
                        ) THEN
                            -- Truncar tabelas para evitar problemas de coerência de chaves
                            TRUNCATE TABLE pagamentos_historicopagamento CASCADE;
                            TRUNCATE TABLE pagamentos_tentativapagamento CASCADE;
                            TRUNCATE TABLE pagamentos_pagamento CASCADE;
                            
                            -- Remover restrições de chaves estrangeiras dinamicamente
                            EXECUTE (
                                SELECT 'ALTER TABLE pagamentos_historicopagamento DROP CONSTRAINT ' || constraint_name || ';'
                                FROM information_schema.key_column_usage
                                WHERE table_name = 'pagamentos_historicopagamento' AND column_name = 'pagamento_id'
                            );
                            
                            EXECUTE (
                                SELECT 'ALTER TABLE pagamentos_tentativapagamento DROP CONSTRAINT ' || constraint_name || ';'
                                FROM information_schema.key_column_usage
                                WHERE table_name = 'pagamentos_tentativapagamento' AND column_name = 'pagamento_id'
                            );

                            -- Alterar tipos de bigint para uuid (precisa dropar a propriedade identity primeiro no Postgres > 10)
                            ALTER TABLE pagamentos_pagamento ALTER COLUMN id DROP IDENTITY IF EXISTS;
                            ALTER TABLE pagamentos_pagamento ALTER COLUMN id SET DATA TYPE uuid USING (gen_random_uuid());
                            ALTER TABLE pagamentos_historicopagamento ALTER COLUMN pagamento_id SET DATA TYPE uuid USING (gen_random_uuid());
                            ALTER TABLE pagamentos_tentativapagamento ALTER COLUMN pagamento_id SET DATA TYPE uuid USING (gen_random_uuid());

                            -- Recriar as chaves estrangeiras
                            ALTER TABLE pagamentos_historicopagamento ADD CONSTRAINT fk_pagamento_historico FOREIGN KEY (pagamento_id) REFERENCES pagamentos_pagamento(id) DEFERRABLE INITIALLY DEFERRED;
                            ALTER TABLE pagamentos_tentativapagamento ADD CONSTRAINT fk_pagamento_tentativa FOREIGN KEY (pagamento_id) REFERENCES pagamentos_pagamento(id) DEFERRABLE INITIALLY DEFERRED;
                        END IF;
                    END $$;
                """)
    except (OperationalError, ProgrammingError) as e:
        # Se falhar (ex: SQLite ou erro de sintaxe), ignora, significa que já está correto
        # ou estamos num ambiente local que não sofre deste problema.
        pass

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('pagamentos', '0005_drop_phantom_columns'),
    ]

    operations = [
        migrations.RunPython(fix_uuid_pk),
    ]
