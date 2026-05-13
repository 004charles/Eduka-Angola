import psycopg2
import os

DATABASE_URL = "postgresql://edukadb_user:pYlhU6XTChvZafEgqKQ5PJq8cv63g0tM@dpg-d821i79kh4rs73bpinmg-a.oregon-postgres.render.com/edukadb"
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cur = conn.cursor()
try:
    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    print("PostGIS ativado com sucesso!")
except Exception as e:
    print(f"Erro ao ativar PostGIS: {e}")
finally:
    cur.close()
    conn.close()
