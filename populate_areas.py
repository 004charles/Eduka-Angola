import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from escolas.models import AreaFormacao

areas = [
    ("Informática", "Cursos focados no desenvolvimento, gestão e manutenção de sistemas informáticos."),
    ("Administração e Serviços", "Cursos voltados à gestão empresarial, contabilidade e finanças."),
    ("Ciências Humanas e Sociais", "Cursos direcionados à compreensão social, história e educação."),
    ("Ciências Exatas e Naturais", "Cursos voltados para as ciências puras como Matemática, Física e Biologia."),
    ("Saúde", "Cursos de apoio técnico à área médica, como Enfermagem e Análises Clínicas."),
    ("Mecânica e Metalurgia", "Cursos de mecânica automóvel, frio, climatização e metalomecânica."),
    ("Eletricidade e Eletrónica", "Cursos voltados para automação, telecomunicações e energia elétrica."),
    ("Construção Civil", "Cursos relacionados à obras, desenho e topografia."),
    ("Agropecuária", "Cursos focados na produção agrícola, pecuária e mecanização."),
    ("Artes e Design", "Cursos de criação artística, artes visuais e design gráfico."),
]

for nome, desc in areas:
    AreaFormacao.objects.get_or_create(nome=nome, defaults={"descricao": desc})

print("Áreas de Formação adicionadas com sucesso!")
