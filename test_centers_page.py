import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
import django
django.setup()

from django.test import Client

client = Client()
response = client.get('/cursos/instituicoes/')
assert response.status_code == 200, response.status_code
html = response.content.decode('utf-8')
assert '1 centros,' not in html
assert '4.8' not in html
assert '142' not in html
assert 'Parceiro Oficial' not in html

for query in (
    {'sort': 'avaliados'},
    {'modalidade': 'Online'},
    {'verificado': '1'},
    {'parcelamento': '1'},
    {'tipo': 'Centro de formação'},
):
    filtered = client.get('/cursos/instituicoes/', query)
    assert filtered.status_code == 200, (query, filtered.status_code)

print('PASS: listagem de centros renderiza')
print('PASS: números e avaliações fixas removidos')
print('PASS: ordenação e filtros funcionam sem erro')
