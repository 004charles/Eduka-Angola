import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from django.test import Client

client = Client()

centros = client.get('/cursos/instituicoes/')
assert centros.status_code == 200
centros_html = centros.content.decode('utf-8')
assert '4.8' not in centros_html
assert '1 centros,' not in centros_html

perfil = client.get('/cursos/centro/1/cursos/')
assert perfil.status_code == 200
perfil_html = perfil.content.decode('utf-8')
assert '4.8' not in perfil_html
assert '120 avaliações' not in perfil_html
assert '2008' not in perfil_html
assert 'DGERT' not in perfil_html
assert '87%' not in perfil_html

curso = client.get('/cursos/curso/1/')
assert curso.status_code == 200
curso_html = curso.content.decode('utf-8')
assert 'Centro de Formação Verificado' not in curso_html
assert '${resposta.comentario}' not in curso_html
assert ('Próxima turma' in curso_html) or ('Sem turma aberta neste momento' in curso_html)

print('PASS: lista de centros sem métricas fixas')
print('PASS: perfil do centro sem garantias inventadas')
print('PASS: detalhe do curso renderiza turma/estado e comentários')
