from decimal import Decimal
from django.utils import timezone
from cursos_app.models import Curso, Categoria, Instrutor
from gestoreduka.models import CentroDeFormacao

COURSES = [
    ("Análise de Dados com Excel Avançado", "Tecnologia e Dados", 2, "PRESENCIAL", "demo-catalogo-01.jpg", "I", 42, Decimal("18500")),
    ("Introdução à Programação Web", "Tecnologia e Dados", 3, "HIBRIDO", "demo-catalogo-02.jpg", "B", 48, Decimal("22000")),
    ("Liderança e Gestão de Equipas", "Gestão e Negócios", 4, "PRESENCIAL", "demo-catalogo-03.jpg", "I", 36, Decimal("16500")),
    ("Empreendedorismo para Pequenos Negócios", "Gestão e Negócios", 2, "HIBRIDO", "demo-catalogo-04.jpg", "B", 30, Decimal("14000")),
    ("Inglês para Entrevistas de Emprego", "Idiomas e Comunicação", 3, "PRESENCIAL", "demo-catalogo-05.jpg", "I", 32, Decimal("12000")),
    ("Espanhol Essencial para Atendimento", "Idiomas e Comunicação", 4, "ONLINE", "demo-catalogo-06.jpg", "B", 28, Decimal("10500")),
    ("Design de Marca para Pequenos Negócios", "Design e Criatividade", 5, "PRESENCIAL", "demo-catalogo-07.jpg", "I", 36, Decimal("16000")),
    ("Fotografia para Conteúdo Digital", "Design e Criatividade", 2, "HIBRIDO", "demo-catalogo-08.jpg", "B", 30, Decimal("15000")),
    ("Nutrição e Hábitos Saudáveis", "Saúde e Bem-estar", 6, "PRESENCIAL", "demo-catalogo-09.jpg", "B", 24, Decimal("11500")),
    ("Gestão do Stress e Produtividade", "Saúde e Bem-estar", 6, "ONLINE", "demo-catalogo-10.jpg", "I", 20, Decimal("9000")),
]

instrutor = Instrutor.objects.order_by("id").first()
if not instrutor:
    raise RuntimeError("Não existe instrutor para associar aos cursos")

now = timezone.now()
created = []
for title, category_name, centre_id, modality, image_name, level, hours, price in COURSES:
    category = Categoria.objects.filter(nome=category_name).order_by("id").first()
    if not category:
        raise RuntimeError(f"Categoria não encontrada: {category_name}")
    centre = CentroDeFormacao.objects.get(pk=centre_id)
    course, was_created = Curso.objects.get_or_create(
        titulo=title,
        defaults={
            "centro": centre,
            "descricao": f"Formação prática de {title.lower()}, com exemplos aplicados ao contexto profissional e apoio ao desenvolvimento de competências.",
            "descricao_curta": f"Aprenda {title.lower()} com uma abordagem prática e orientada para resultados.",
            "nivel": level,
            "idioma": "PT",
            "categoria": category,
            "certificado": True,
            "carga_horaria": hours,
            "is_gratuito": False,
            "moeda": "AOA",
            "preco": price,
            "preco_inscricao": Decimal("0"),
            "preco_promocional": None,
            "mensalidade": Decimal("0"),
            "tipo_cobranca_inscricao": "APENAS_TAXA",
            "vagas_minimas": 1,
            "data_inicio_inscricoes": now,
            "modalidade": modality,
            "duracao": "1_MES",
            "ativo": True,
            "publicado": True,
            "imagem": f"cursos/{image_name}",
            "requisitos": "Interesse em aprender e disponibilidade para acompanhar as actividades.",
            "objetivo_geral": f"Desenvolver competências aplicáveis em {title.lower()}.",
            "destaque": False,
        },
    )
    course.instrutores.add(instrutor)
    created.append((course.id, was_created, course.titulo))

print("COURSES_CREATED_OR_FOUND", created)
print("TOTAL", Curso.objects.filter(ativo=True, publicado=True).count())
