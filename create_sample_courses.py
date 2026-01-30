#!/usr/bin/env python
"""
Script para criar cursos de exemplo no sistema EdukAngola
Execute: python manage.py shell < create_sample_courses.py
"""

from usuarios.models import Usuario
from gestoreduka.models import CentroDeFormacao
from cursos_app.models import Curso, CategoriaCurso, Instrutor

# Buscar o centro de teste
try:
    centro = CentroDeFormacao.objects.get(email='gestor@teste.com')
    print(f"✓ Centro encontrado: {centro.nome}")
except CentroDeFormacao.DoesNotExist:
    print("✗ Centro não encontrado. Execute create_test_users.py primeiro.")
    exit(1)

# Criar categorias
print("\nCriando categorias...")
categorias_data = [
    {'nome': 'Programação', 'slug': 'programacao'},
    {'nome': 'Design', 'slug': 'design'},
    {'nome': 'Negócios', 'slug': 'negocios'},
    {'nome': 'Idiomas', 'slug': 'idiomas'},
]

categorias = {}
for cat_data in categorias_data:
    cat, created = CategoriaCurso.objects.get_or_create(
        slug=cat_data['slug'],
        defaults={'nome': cat_data['nome']}
    )
    categorias[cat_data['slug']] = cat
    status = "criada" if created else "já existe"
    print(f"  • {cat.nome}: {status}")

# Criar instrutor
print("\nCriando instrutor...")
instrutor, created = Instrutor.objects.get_or_create(
    centro=centro,
    nome='Prof. Carlos Mendes',
    defaults={
        'email': 'carlos@teste.com',
        'especialidade': 'Tecnologia e Programação',
        'biografia': 'Professor com 10 anos de experiência em desenvolvimento de software.',
        'ativo': True
    }
)
status = "criado" if created else "já existe"
print(f"  • {instrutor.nome}: {status}")

# Criar cursos
print("\nCriando cursos...")
cursos_data = [
    {
        'titulo': 'Python para Iniciantes',
        'descricao': 'Aprenda Python do zero com exemplos práticos e projetos reais.',
        'categoria': 'programacao',
        'preco': 15000,
        'duracao_horas': 40,
        'nivel': 'iniciante',
    },
    {
        'titulo': 'Design Gráfico com Photoshop',
        'descricao': 'Domine as ferramentas do Photoshop para criar designs profissionais.',
        'categoria': 'design',
        'preco': 20000,
        'duracao_horas': 30,
        'nivel': 'intermediario',
    },
    {
        'titulo': 'Inglês Básico',
        'descricao': 'Curso completo de inglês para iniciantes com foco em conversação.',
        'categoria': 'idiomas',
        'preco': 12000,
        'duracao_horas': 60,
        'nivel': 'iniciante',
    },
    {
        'titulo': 'Empreendedorismo Digital',
        'descricao': 'Aprenda a criar e gerenciar seu negócio online.',
        'categoria': 'negocios',
        'preco': 18000,
        'duracao_horas': 25,
        'nivel': 'intermediario',
    },
]

for curso_data in cursos_data:
    categoria_slug = curso_data.pop('categoria')
    curso, created = Curso.objects.get_or_create(
        titulo=curso_data['titulo'],
        centro=centro,
        defaults={
            **curso_data,
            'categoria': categorias[categoria_slug],
            'publicado': True,
            'ativo': True,
            'destaque': True,
        }
    )
    
    if created:
        curso.instrutores.add(instrutor)
        print(f"  ✓ {curso.titulo}")
    else:
        print(f"  • {curso.titulo} (já existe)")

print("\n" + "="*50)
print("CURSOS CRIADOS COM SUCESSO!")
print("="*50)
print(f"Total de cursos: {Curso.objects.count()}")
print(f"Acesse: http://127.0.0.1:8000/cursos/home_cursos/")
print("="*50)
