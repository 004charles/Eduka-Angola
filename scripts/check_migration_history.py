from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT app, name FROM django_migrations WHERE app IN ('usuarios', 'blog', 'cursos_app') ORDER BY app, name")
    for row in cursor.fetchall():
        print(row)
