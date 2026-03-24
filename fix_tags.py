import re

file_path = r"c:\Users\IT - Carlos - OX4\Documents\Eduka-Angola\cursos_app\templates\curso_detalhe.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

def consolidate_match(match):
    full_match = match.group(0)
    new_match = re.sub(r'\s+', ' ', full_match)
    return new_match

new_content = re.sub(r'\{%[^%]+%\}', consolidate_match, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Normalização concluída com sucesso.")
