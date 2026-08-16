from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SHOW COLUMNS FROM cursos_app_curso")
    print('CURSO_COLUMNS')
    for row in cursor.fetchall():
        print(row[0], row[1], row[3], row[4], row[5])
