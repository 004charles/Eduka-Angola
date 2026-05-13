import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from escolas.models import Infraestrutura

infras = [
    ("Laboratório de Informática", "feather-monitor"),
    ("Laboratório de Química/Física", "feather-hexagon"),
    ("Oficinas de Mecânica", "feather-tool"),
    ("Biblioteca", "feather-book-open"),
    ("Quadra Desportiva", "feather-activity"),
    ("Cantina / Refeitório", "feather-coffee"),
    ("Sala de Primeiros Socorros", "feather-heart"),
    ("Wi-Fi para Alunos", "feather-wifi"),
]

for nome, icone in infras:
    Infraestrutura.objects.get_or_create(nome=nome, defaults={"icone": icone})

print("Infraestruturas adicionadas com sucesso!")
