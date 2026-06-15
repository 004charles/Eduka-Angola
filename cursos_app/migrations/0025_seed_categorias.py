from django.db import migrations

CATEGORIAS = [
    {
        "nome": "Tecnologia e Informática",
        "slug": "tecnologia",
        "descricao": "Programação, redes, cibersegurança, inteligência artificial e muito mais.",
        "icone": "feather-monitor",
    },
    {
        "nome": "Gestão e Negócios",
        "slug": "gestao-negocios-e-administracao",
        "descricao": "Empreendedorismo, administração, liderança e estratégia empresarial.",
        "icone": "feather-briefcase",
    },
    {
        "nome": "Saúde e Bem-Estar",
        "slug": "saude-e-bem-estar",
        "descricao": "Medicina, enfermagem, nutrição, psicologia e saúde pública.",
        "icone": "feather-heart",
    },
    {
        "nome": "Arte e Design",
        "slug": "arte-e-design",
        "descricao": "Design gráfico, fotografia, artes visuais e criatividade.",
        "icone": "feather-pen-tool",
    },
    {
        "nome": "Educação e Pedagogia",
        "slug": "educacao-e-pedagogia",
        "descricao": "Métodos de ensino, didática, gestão escolar e formação de professores.",
        "icone": "feather-book-open",
    },
    {
        "nome": "Engenharia e Construção",
        "slug": "engenharia-e-construcao",
        "descricao": "Engenharia civil, elétrica, mecânica e gestão de obras.",
        "icone": "feather-tool",
    },
    {
        "nome": "Marketing e Comunicação",
        "slug": "marketing-e-comunicacao",
        "descricao": "Marketing digital, publicidade, comunicação e redes sociais.",
        "icone": "feather-trending-up",
    },
    {
        "nome": "Idiomas",
        "slug": "idiomas",
        "descricao": "Inglês, francês, mandarim, português e outros idiomas essenciais.",
        "icone": "feather-globe",
    },
    {
        "nome": "Finanças e Contabilidade",
        "slug": "financas-e-contabilidade",
        "descricao": "Contabilidade, finanças pessoais, investimentos e economia.",
        "icone": "feather-dollar-sign",
    },
    {
        "nome": "Artes, Ofícios e Formação Profissional",
        "slug": "artes-oficios-e-formacao-profissional",
        "descricao": "Habilidades práticas, formação técnica e profissionalização.",
        "icone": "feather-scissors",
    },
]


def seed_categorias(apps, schema_editor):
    Categoria = apps.get_model("cursos_app", "Categoria")
    for cat in CATEGORIAS:
        Categoria.objects.get_or_create(
            slug=cat["slug"],
            defaults={
                "nome": cat["nome"],
                "descricao": cat["descricao"],
            },
        )


def unseed_categorias(apps, schema_editor):
    Categoria = apps.get_model("cursos_app", "Categoria")
    slugs = [c["slug"] for c in CATEGORIAS]
    Categoria.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("cursos_app", "0019_remove_curso_filial_curso_filiais_turma_filial"),
    ]

    operations = [
        migrations.RunPython(seed_categorias, reverse_code=unseed_categorias),
    ]
