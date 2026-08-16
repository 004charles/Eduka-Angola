from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SHOW COLUMNS FROM cursos_app_turma")
    print('TURMA_COLUMNS')
    for row in cursor.fetchall():
        print(row[0], row[1], row[3], row[4], row[5])
    cursor.execute("SELECT app, name FROM django_migrations WHERE app = 'cursos_app' ORDER BY name")
    print('CURSOS_MIGRATIONS')
    for row in cursor.fetchall():
        print(row)
