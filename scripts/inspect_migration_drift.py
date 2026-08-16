from django.db import connection

with connection.cursor() as cursor:
    tables = connection.introspection.table_names()
    for table in sorted(tables):
        if table in {'usuarios_centroseguimento', 'usuarios_comentario', 'usuarios_empresa', 'usuarios_biblioteca', 'blog_post', 'blog_comentario'}:
            print(table, connection.introspection.get_table_description(cursor, table))
