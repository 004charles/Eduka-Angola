import os

with open('gestoreduka/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('filial.cursos.all()', 'filial.cursos_disponiveis.all()')
content = content.replace('filial.cursos.filter', 'filial.cursos_disponiveis.filter')
content = content.replace('filial.cursos.values_list', 'filial.cursos_disponiveis.values_list')

content = content.replace('curso__filial=filial', 'curso__filiais=filial')
content = content.replace('curso__filial=fil', 'curso__filiais=fil')
content = content.replace('curso__filial__isnull', 'curso__filiais__isnull')
content = content.replace("'curso__filial'", "") # for select_related

with open('gestoreduka/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed views.py!')
