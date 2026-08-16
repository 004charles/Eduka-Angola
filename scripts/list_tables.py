from django.db import connection
print('\n'.join(connection.introspection.table_names()))
