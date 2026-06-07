import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from cursos_app.models import Curso

# Encontrar cursos clonados (aqueles que pertencem a uma filial diretamente no modelo antigo)
cursos_clonados = Curso.objects.filter(filial__isnull=False)
count = cursos_clonados.count()

print(f"Encontrados {count} cursos clonados. A apagar...")
cursos_clonados.delete()
print("Cursos clonados apagados com sucesso!")
