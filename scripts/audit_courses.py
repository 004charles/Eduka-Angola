from cursos_app.models import Curso, Categoria
from gestoreduka.models import CentroDeFormacao
from cursos_app.models import Instrutor

print('COURSES', Curso.objects.count())
print('PUBLISHED', Curso.objects.filter(ativo=True, publicado=True).count())
print('CATEGORIES', list(Categoria.objects.values_list('id', 'nome')))
print('CENTRES', list(CentroDeFormacao.objects.values_list('id', 'nome', 'cidade', 'provincia')))
print('INSTRUCTORS', list(Instrutor.objects.values_list('id', 'nome')[:20]))
print('TITLES', list(Curso.objects.values_list('id', 'titulo', 'modalidade', 'categoria_id', 'centro_id')))
