"""Carga inicial pública da Edukangola, executada uma vez no próximo deploy.

Inclui exclusivamente catálogo, turmas, biblioteca e perfis públicos. Não cria
contas, inscrições, pagamentos, palavras-passe ou outros dados pessoais.
"""

from datetime import time, timedelta
from decimal import Decimal
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations, transaction
from django.utils import timezone
from django.utils.text import slugify


ROOT = Path(settings.BASE_DIR)


def _load_seed(filename, module_name):
    spec = spec_from_file_location(module_name, ROOT / filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _persist_field(instance, field_name):
    field = getattr(instance, field_name)
    if not field or not field.name:
        return
    source = ROOT / "media" / field.name
    if not source.exists():
        return
    with source.open("rb") as handle:
        field.save(source.name, File(handle), save=True)


def _seed_manager_catalog():
    from cursos_app.models import Categoria, Curso, Turma
    from gestoreduka.models import CentroDeFormacao, PerfilCentroDeFormacao

    centro, _ = CentroDeFormacao.objects.update_or_create(
        email="gestor.teste@edukangola.local",
        defaults={
            "nome": "Centro Demonstração GestorEduka",
            "nif": "5417273980",
            "pais": "AO",
            "endereco": "Avenida 4 de Fevereiro, Mutamba",
            "cidade": "Luanda",
            "provincia": "Luanda",
            "telefone": "+244 900 000 000",
            "site": "https://www.edukangola.com/centros",
            "localizacao": "-8.8137,13.2302",
            "ativo": True,
        },
    )
    perfil, _ = PerfilCentroDeFormacao.objects.update_or_create(
        centro=centro,
        defaults={
            "dono": "Edukangola",
            "descricao": "Centro de formação profissional orientado para competências digitais, gestão e empregabilidade.",
            "missao": "Transformar ambição em competências práticas para o mercado de trabalho angolano.",
            "visao": "Ser uma referência nacional na formação aplicada e na ligação entre talento e oportunidades.",
            "valores": "Rigor, inclusão, prática, confiança e inovação.",
            "ano_fundacao": 2021,
            "horario_funcionamento": "Segunda a sábado, 08:00–20:00",
            "tipo": "Centro de formação profissional",
            "modalidade": "Híbrido",
            "whatsapp": "+244900000000",
            "destaque": True,
            "verificado": True,
            "slug": "centro-demonstracao-gestoreduka",
        },
    )
    for field_name, source_name in (("imagem", "centro-demo-logo.jpg"), ("banner", "centro-demo-capa.jpg")):
        source = ROOT / "static" / "assets" / "images" / "centros" / source_name
        if source.exists():
            with source.open("rb") as handle:
                getattr(perfil, field_name).save(source_name, File(handle), save=True)

    categories = {}
    for name, slug in (
        ("Tecnologia e Dados", "tecnologia-dados"),
        ("Gestão e Negócios", "gestao-negocios"),
        ("Idiomas e Comunicação", "idiomas-comunicacao"),
        ("Design e Comunicação", "design-comunicacao"),
    ):
        categories[name], _ = Categoria.objects.update_or_create(
            slug=slug,
            defaults={"nome": name, "descricao": f"Formações em {name.lower()}."},
        )

    specifications = [
        ("Suporte Técnico e Redes", "Prepare-se para instalar, configurar e manter redes e computadores em ambientes profissionais.", "Tecnologia e Dados", 72, "85000", "7500", "18000", "I", "3_MESES", "PRESENCIAL"),
        ("Excel e Power BI para Gestão", "Transforme dados em relatórios claros e úteis para apoiar decisões de negócio.", "Tecnologia e Dados", 60, "68000", "5000", "16000", "I", "2_MESES", "HIBRIDO"),
        ("Marketing Digital para Pequenos Negócios", "Aprenda a planear campanhas, conteúdo e vendas digitais de forma prática.", "Gestão e Negócios", 48, "58000", "4500", "14500", "B", "2_MESES", "PRESENCIAL"),
        ("Inglês Profissional para Atendimento", "Desenvolva vocabulário e confiança para comunicação profissional em inglês.", "Idiomas e Comunicação", 56, "62000", "5000", "15500", "B", "3_MESES", "PRESENCIAL"),
        ("Fundamentos de Cibersegurança", "Conheça boas práticas para proteger dados, contas e operações digitais.", "Tecnologia e Dados", 36, "45000", "3500", "12000", "B", "1_MES", "ONLINE"),
        ("Design de Marca para Empreendedores", "Crie uma identidade visual simples e consistente para pequenos negócios.", "Design e Comunicação", 40, "52000", "4000", "13000", "B", "2_MESES", "HIBRIDO"),
    ]
    today = timezone.localdate()
    for index, (title, summary, category_name, hours, price, fee, monthly, level, duration, modality) in enumerate(specifications, start=1):
        course, _ = Curso.objects.update_or_create(
            centro=centro,
            titulo=title,
            defaults={
                "descricao": f"{summary} Esta formação integra exercícios práticos e preparação para desafios reais do mercado.",
                "descricao_curta": summary,
                "categoria": categories[category_name],
                "nivel": level,
                "idioma": "PT",
                "certificado": True,
                "carga_horaria": hours,
                "is_gratuito": False,
                "moeda": "AOA",
                "preco": Decimal(price),
                "preco_inscricao": Decimal(fee),
                "mensalidade": Decimal(monthly),
                "tipo_cobranca_inscricao": "TAXA_E_MENSALIDADE",
                "modalidade": modality,
                "duracao": duration,
                "ativo": True,
                "publicado": True,
                "destaque": index <= 3,
                "requisitos": "Documento de identificação e disponibilidade para participar nas sessões.",
                "objetivo_geral": "Desenvolver competências aplicadas e valorizadas no mercado de trabalho.",
                "documento_requerido": "BI",
                "permite_parcelamento": True,
                "max_parcelas": 3,
                "tags": "formação, emprego, competências, Luanda",
                "data_inicio": today + timedelta(days=10 + index * 7),
            },
        )
        Turma.objects.update_or_create(
            codigo=f"GEPUB{index:02d}",
            defaults={
                "curso": course,
                "nome": f"Turma pública {index:02d}",
                "data_inicio": today + timedelta(days=10 + index * 7),
                "data_fim": today + timedelta(days=66 + index * 7),
                "turno": "NOITE" if index % 2 else "TARDE",
                "horario_inicio": time(18 if index % 2 else 14, 0),
                "horario_fim": time(21 if index % 2 else 17, 0),
                "dias_semana": "TER,QUI",
                "vagas_totais": 25,
                "vagas_ocupadas": 0,
                "local": centro.endereco,
                "sala": f"Sala {index}",
                "status": "ABERTA",
                "observacoes": "Turma pública de demonstração Edukangola.",
            },
        )


def _seed_extra_courses():
    from cursos_app.models import Categoria, Curso
    from gestoreduka.models import CentroDeFormacao

    centres = list(CentroDeFormacao.objects.filter(email__in=[
        "atlas.demo@edukangola.test", "horizonte.demo@edukangola.test", "kwanza.demo@edukangola.test",
        "criativa.demo@edukangola.test", "vida.demo@edukangola.test",
    ]).order_by("email"))
    by_email = {centre.email: centre for centre in centres}
    order = ["atlas.demo@edukangola.test", "horizonte.demo@edukangola.test", "kwanza.demo@edukangola.test", "criativa.demo@edukangola.test", "vida.demo@edukangola.test"]
    items = [
        ("Análise de Dados com Excel Avançado", "Tecnologia e Dados", 0, "PRESENCIAL", "demo-catalogo-01.jpg", "I", 42, "18500"),
        ("Introdução à Programação Web", "Tecnologia e Dados", 1, "HIBRIDO", "demo-catalogo-02.jpg", "B", 48, "22000"),
        ("Liderança e Gestão de Equipas", "Gestão e Negócios", 2, "PRESENCIAL", "demo-catalogo-03.jpg", "I", 36, "16500"),
        ("Empreendedorismo para Pequenos Negócios", "Gestão e Negócios", 0, "HIBRIDO", "demo-catalogo-04.jpg", "B", 30, "14000"),
        ("Inglês para Entrevistas de Emprego", "Idiomas e Comunicação", 1, "PRESENCIAL", "demo-catalogo-05.jpg", "I", 32, "12000"),
        ("Espanhol Essencial para Atendimento", "Idiomas e Comunicação", 2, "ONLINE", "demo-catalogo-06.jpg", "B", 28, "10500"),
        ("Design de Marca para Pequenos Negócios", "Design e Criatividade", 3, "PRESENCIAL", "demo-catalogo-07.jpg", "I", 36, "16000"),
        ("Fotografia para Conteúdo Digital", "Design e Criatividade", 0, "HIBRIDO", "demo-catalogo-08.jpg", "B", 30, "15000"),
        ("Nutrição e Hábitos Saudáveis", "Saúde e Bem-estar", 4, "PRESENCIAL", "demo-catalogo-09.jpg", "B", 24, "11500"),
        ("Gestão do Stress e Produtividade", "Saúde e Bem-estar", 4, "ONLINE", "demo-catalogo-10.jpg", "I", 20, "9000"),
    ]
    for title, category_name, centre_index, modality, image_name, level, hours, price in items:
        category = Categoria.objects.filter(nome=category_name).order_by("id").first()
        centre = by_email[order[centre_index]]
        course, _ = Curso.objects.update_or_create(
            centro=centre,
            titulo=title,
            defaults={
                "descricao": f"Formação prática de {title.lower()}, com exemplos aplicados ao contexto profissional e apoio ao desenvolvimento de competências.",
                "descricao_curta": f"Aprenda {title.lower()} com uma abordagem prática e orientada para resultados.",
                "categoria": category,
                "nivel": level,
                "idioma": "PT",
                "certificado": True,
                "carga_horaria": hours,
                "is_gratuito": False,
                "moeda": "AOA",
                "preco": Decimal(price),
                "preco_inscricao": Decimal("0"),
                "mensalidade": Decimal("0"),
                "tipo_cobranca_inscricao": "APENAS_TAXA",
                "modalidade": modality,
                "duracao": "1_MES",
                "ativo": True,
                "publicado": True,
                "requisitos": "Interesse em aprender e disponibilidade para acompanhar as actividades.",
                "objetivo_geral": f"Desenvolver competências aplicáveis em {title.lower()}.",
                "documento_requerido": "NENHUM",
                "tags": f"formação, {category_name.lower()}",
            },
        )
        course.imagem.name = f"cursos/{image_name}"
        course.save(update_fields=["imagem"])


def _seed_missing_video_courses():
    from cursos_app.models import Categoria
    from cursovideoapp.models import Aula, Curso_video
    from gestoreduka.models import CentroDeFormacao

    items = [
        ("Comunicação Digital Profissional", "Tecnologia e Dados", None, "0", "Domine ferramentas e práticas para colaborar, comunicar e trabalhar melhor no ambiente digital."),
        ("Empreendedorismo na Prática", "Gestão e Negócios", "gestor.teste@edukangola.local", "15000", "Curso em vídeo para estruturar uma ideia de negócio, validar clientes e organizar vendas."),
        ("Excel aplicado ao trabalho", "Tecnologia e Dados", None, "0", "Aprenda a organizar dados, criar relatórios claros e tomar decisões mais rápidas com ferramentas práticas de Excel."),
        ("Excel para Decisões Rápidas", "Tecnologia e Dados", "gestor.teste@edukangola.local", "18000", "Curso em vídeo com exercícios de Excel e Power BI para gestores e equipas."),
        ("Fundamentos de Excel", "Tecnologia e Dados", None, "0", "Aprenda os fundamentos do Excel para organizar informação e resolver tarefas do dia a dia."),
    ]
    for title, category_name, email, price, description in items:
        category = Categoria.objects.filter(nome=category_name).order_by("id").first()
        centre = CentroDeFormacao.objects.filter(email=email).first() if email else None
        course, _ = Curso_video.objects.update_or_create(
            titulo=title,
            defaults={
                "slug": slugify(title),
                "descricao": description,
                "categoria": category,
                "centro": centre,
                "is_pago": Decimal(price) > 0,
                "preco": Decimal(price),
                "is_original_edukangola": centre is None,
                "destaque": False,
            },
        )
        for order, (lesson_title, seconds) in enumerate((("Introdução e objectivos", 420), ("Aplicação prática", 780), ("Síntese e próximos passos", 600)), start=1):
            Aula.objects.update_or_create(
                curso=course,
                ordem=order,
                defaults={"titulo": lesson_title, "duracao_segundos": seconds, "descricao": "Conteúdo orientado para aplicação prática."},
            )


def _migrate_covers_to_storage():
    from biblioteca.models import Livro
    from cursos_app.models import Curso
    from cursovideoapp.models import Curso_video

    for course in Curso.objects.exclude(imagem=""):
        _persist_field(course, "imagem")
    for course in Curso_video.objects.exclude(capa=""):
        _persist_field(course, "capa")
    for book in Livro.objects.filter(estado="PUBLICADO"):
        source = ROOT / "media" / "biblioteca" / "capas" / f"{slugify(book.titulo)}.jpg"
        if source.exists():
            with source.open("rb") as handle:
                book.capa.save(source.name, File(handle), save=True)


@transaction.atomic
def seed_public_catalog(apps, schema_editor):
    _load_seed("arquivos_scripts/seed_demo_catalog.py", "edukangola_seed_demo_catalog").carregar_catalogo()
    _load_seed("arquivos_scripts/seed_mundotec_catalog.py", "edukangola_seed_mundotec_catalog").carregar_catalogo()
    _load_seed("arquivos_scripts/seed_video_library_20.py", "edukangola_seed_video_library").load_programmes()
    _load_seed("scripts/seed_library_books.py", "edukangola_seed_library_books").run()
    _seed_manager_catalog()
    _seed_extra_courses()
    _seed_missing_video_courses()
    _migrate_covers_to_storage()


class Migration(migrations.Migration):
    dependencies = [
        ("cursos_app", "0033_alter_curso_modalidade"),
        ("gestoreduka", "0025_remove_feed_reels"),
        ("biblioteca", "0003_bibliotecapessoal_pagina_leitura"),
        ("cursovideoapp", "0020_duvidas_resolvidas"),
    ]

    operations = [migrations.RunPython(seed_public_catalog, migrations.RunPython.noop)]
