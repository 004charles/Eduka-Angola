from django.db import connection

with connection.cursor() as cursor:
    for table in ('cursos_app_curso', 'gestoreduka_centrodeformacao', 'cursos_app_turma'):
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        print(table, cursor.fetchone()[0])
    cursor.execute('SELECT id, titulo, publicado, ativo, categoria_id FROM cursos_app_curso ORDER BY id DESC LIMIT 10')
    print('CURSOS')
    for row in cursor.fetchall():
        print(row)
