"""Carga idempotente de vinte programas de demonstração para a biblioteca de cursos em vídeo."""

import os
import shutil
import sys
from datetime import date, time, timedelta
from pathlib import Path

import django


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
django.setup()

from django.conf import settings
from django.db import transaction
from django.utils.text import slugify

from cursos_app.models import Categoria
from cursovideoapp.models import Aula, Curso_video, TurmaVideo
from gestoreduka.models import CentroDeFormacao


COURSE_IMAGES = [
    "course-online-01.jpg", "course-online-02.jpg", "course-online-03.jpg", "course-online-04.jpg",
    "course-elegant-01.jpg", "course-elegant-02.jpg", "course-elegant-03.jpg", "course-elegant-04.jpg",
    "course-list-01.jpg", "course-list-02.jpg", "course-list-03.jpg", "course-list-04.jpg",
    "art-course-01.png", "art-course-02.png", "art-course-03.png", "art-course-05.png",
    "medical-course-01.jpg", "medical-course-02.jpg", "medical-course-03.jpg", "coach-course-01.jpg",
]

CATEGORIES = {
    "Tecnologia e Dados": "tecnologia-dados",
    "Gestão e Negócios": "gestao-negocios",
    "Idiomas e Comunicação": "idiomas-comunicacao",
    "Design e Criatividade": "design-criatividade",
    "Saúde e Bem-estar": "saude-bem-estar",
}

PROGRAMMES = [
    ("Tecnologia e Dados", "Excel para Análise de Dados", "Transforme dados do dia a dia em tabelas, fórmulas e relatórios claros.", 18000, True, 0),
    ("Tecnologia e Dados", "Introdução a Python", "Aprenda os fundamentos da programação e automatize tarefas simples.", 24000, True, 1),
    ("Tecnologia e Dados", "Power BI para Indicadores", "Construa painéis visuais para apoiar decisões de negócio.", 28000, False, 2),
    ("Tecnologia e Dados", "Cibersegurança no Dia a Dia", "Proteja as suas contas, dispositivos e informação profissional.", 0, True, 3),
    ("Gestão e Negócios", "Gestão Financeira para Pequenos Negócios", "Organize receitas, custos e metas para tomar decisões mais seguras.", 22000, False, 4),
    ("Gestão e Negócios", "Vendas Consultivas", "Desenvolva uma abordagem de vendas centrada nas necessidades do cliente.", 19000, False, 5),
    ("Gestão e Negócios", "Empreender em Angola", "Da ideia ao plano de acção: bases práticas para iniciar um negócio.", 0, True, 6),
    ("Gestão e Negócios", "Liderança de Equipas", "Comunique melhor, delegue com clareza e acompanhe resultados.", 21000, False, 7),
    ("Idiomas e Comunicação", "Inglês para Entrevistas de Trabalho", "Prepare respostas, vocabulário e confiança para entrevistas em inglês.", 17000, True, 8),
    ("Idiomas e Comunicação", "Comunicação e Apresentações", "Estruture ideias e apresente com clareza em contextos profissionais.", 15000, False, 9),
    ("Idiomas e Comunicação", "Escrita Profissional", "Escreva e-mails, relatórios e propostas com objectividade.", 0, True, 10),
    ("Idiomas e Comunicação", "Francês Prático para Viagens", "Aprenda expressões essenciais para deslocações e situações do quotidiano.", 14000, False, 11),
    ("Design e Criatividade", "Canva para Marcas", "Crie peças visuais consistentes para a presença digital da sua marca.", 16000, True, 12),
    ("Design e Criatividade", "Design de Conteúdo para Redes", "Planeie formatos e composições que tornam os conteúdos mais claros.", 20000, False, 13),
    ("Design e Criatividade", "Fotografia com Smartphone", "Domine luz, enquadramento e edição para imagens mais profissionais.", 0, True, 14),
    ("Design e Criatividade", "UX UI Essencial", "Conheça pesquisa, fluxos e princípios de interface para produtos digitais.", 26000, False, 15),
    ("Saúde e Bem-estar", "Primeiros Socorros em Casa e no Trabalho", "Saiba como agir nos primeiros minutos de uma situação de emergência.", 18000, False, 16),
    ("Saúde e Bem-estar", "Saúde Mental no Trabalho", "Identifique rotinas que protegem o bem-estar e a colaboração diária.", 0, True, 17),
    ("Saúde e Bem-estar", "Higiene e Segurança Alimentar", "Aplique boas práticas na preparação, conservação e serviço de alimentos.", 12000, False, 18),
    ("Saúde e Bem-estar", "Cuidados ao Idoso", "Desenvolva práticas seguras, humanas e organizadas de acompanhamento.", 23000, False, 19),
]


def prepare_cover(image_index):
    source = PROJECT_ROOT / "static" / "assets" / "images" / "course" / COURSE_IMAGES[image_index]
    target_dir = Path(settings.MEDIA_ROOT) / "cursos" / "capas"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_name = f"biblioteca-video-{image_index + 1:02d}{source.suffix}"
    shutil.copyfile(source, target_dir / target_name)
    return f"cursos/capas/{target_name}"


def lesson_outline(title, position):
    return [
        ("Boas-vindas e objectivos", 420, f"Conheça o percurso do programa {title} e prepare o seu plano de estudo."),
        ("Conceitos fundamentais", 780, "Aprenda a base necessária para aplicar o tema com segurança."),
        ("Aplicação prática", 960, "Acompanhe um exemplo orientado, passo a passo."),
        ("Projecto de consolidação", 840 + position * 15, "Reúna os conhecimentos num exercício final para continuar a praticar."),
    ]


@transaction.atomic
def load_programmes():
    categories = {}
    for name, slug in CATEGORIES.items():
        category, _ = Categoria.objects.update_or_create(
            slug=slug,
            defaults={"nome": name, "descricao": f"Cursos em vídeo de {name.lower()}."},
        )
        categories[name] = category

    centres = list(CentroDeFormacao.objects.filter(email__in=[
        "atlas.demo@edukangola.test", "horizonte.demo@edukangola.test", "kwanza.demo@edukangola.test",
        "criativa.demo@edukangola.test", "vida.demo@edukangola.test",
    ]).order_by("email"))
    if not centres:
        raise RuntimeError("Não foram encontrados centros de demonstração. Execute primeiro seed_demo_catalog.py.")

    today = date.today()
    created = 0
    updated = 0
    for position, (category_name, title, summary, price, original, image_index) in enumerate(PROGRAMMES, start=1):
        centre = None if original else centres[(position - 1) % len(centres)]
        course, was_created = Curso_video.objects.update_or_create(
            titulo=title,
            defaults={
                "descricao": summary + " Este é um programa demonstrativo publicado para explorar a experiência de aprendizagem da Edukangola.",
                "categoria": categories[category_name],
                "centro": centre,
                "is_pago": price > 0,
                "preco": price,
                "is_original_edukangola": original,
                "destaque": position <= 6,
                "slug": slugify(title),
            },
        )
        course.capa.name = prepare_cover(image_index)
        course.save(update_fields=["capa"])
        created += int(was_created)
        updated += int(not was_created)

        for order, (lesson_title, duration, lesson_description) in enumerate(lesson_outline(title, position), start=1):
            Aula.objects.update_or_create(
                curso=course,
                ordem=order,
                defaults={"titulo": lesson_title, "duracao_segundos": duration, "descricao": lesson_description},
            )

        if centre:
            start = today + timedelta(days=10 + position)
            TurmaVideo.objects.update_or_create(
                codigo=f"VIDLIB{position:02d}",
                defaults={
                    "curso": course,
                    "nome": "Acompanhamento online",
                    "data_inicio": start,
                    "data_fim": start + timedelta(days=28),
                    "turno": "NOITE",
                    "horario_inicio": time(18, 30),
                    "horario_fim": time(20, 0),
                    "dias_semana": "TER,QUI",
                    "vagas_totais": 30,
                    "vagas_ocupadas": position % 9,
                    "status": "ABERTA",
                    "observacoes": "Acompanhamento demonstrativo para a biblioteca de cursos em vídeo.",
                },
            )

    total = Curso_video.objects.filter(titulo__in=[item[1] for item in PROGRAMMES]).count()
    paid = Curso_video.objects.filter(titulo__in=[item[1] for item in PROGRAMMES], is_pago=True).count()
    print({"programas_esperados": len(PROGRAMMES), "programas_no_catalogo": total, "criados": created, "actualizados": updated, "pagos": paid, "gratuitos": total - paid})


if __name__ == "__main__":
    load_programmes()
