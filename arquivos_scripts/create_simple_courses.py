#!/usr/bin/env python
"""Script ultra-simplificado para criar cursos"""

from gestoreduka.models import CentroDeFormacao
from cursos_app.models import Curso, Instrutor, Categoria

centro = CentroDeFormacao.objects.first()
print(f"Centro: {centro.nome}")

# Instrutor
instrutor, _ = Instrutor.objects.get_or_create(
    email='carlos@teste.com',
    defaults={
        'centro_de_formacao': centro,
        'nome': 'Prof. Carlos',
        'biografia': 'Professor experiente.',
        'area_especializacao': 'TECNOLOGIA_INFORMACAO',
    }
)
print(f"Instrutor: {instrutor.nome}")

# Categoria
cat, _ = Categoria.objects.get_or_create(
    nome='Programação',
    defaults={'slug': 'programacao'}
)

# Cursos
cursos = [
    {'titulo': 'Python Básico', 'descricao': 'Aprenda Python', 'carga_horaria': 40},
    {'titulo': 'JavaScript', 'descricao': 'Aprenda JS', 'carga_horaria': 35},
    {'titulo': 'Django', 'descricao': 'Framework web', 'carga_horaria': 50},
]

for c in cursos:
    curso, created = Curso.objects.get_or_create(
        titulo=c['titulo'],
        centro=centro,
        defaults={
            'descricao': c['descricao'],
            'carga_horaria': c['carga_horaria'],
            'categoria': cat,
            'publicado': True,
            'ativo': True,
            'destaque': True,
        }
    )
    if created:
        curso.instrutores.add(instrutor)
        print(f"✓ {curso.titulo}")

print(f"\nTotal: {Curso.objects.count()} cursos")
