"""Regista cursos de catálogo da Mundo da Tecnologia a partir das capas fornecidas.

Os contactos do centro vêm do site institucional. As condições comerciais são
propositadamente marcadas como "consultar condições" até confirmação directa do
centro, pelo que não são inventados preços oficiais.
"""

import os
import re
import shutil
import sys
from datetime import date, time, timedelta
from pathlib import Path

import django


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
django.setup()

from django.db import transaction
from django.conf import settings

from cursos_app.models import Categoria, Curso, Turma
from gestoreduka.models import CentroDeFormacao


CENTRO = {
    "nome": "Mundo da Tecnologia",
    "email": "geral@mundotec.ao",
    "telefone": "+244 932 407 153 | +244 922 900 498",
    "endereco": "Rangel, Vila Alice, Rua João de Deus; Zango III, Primeira Paragem",
    "cidade": "Luanda",
    "provincia": "Luanda",
    "pais": "AO",
    "site": "https://mundotec.ao/",
    "ativo": True,
}

CATEGORIAS = {
    "tecnologia": ("Tecnologia e Dados", "tecnologia-dados"),
    "gestao": ("Gestão e Negócios", "gestao-negocios"),
    "marketing": ("Marketing e Vendas", "marketing-vendas"),
    "design": ("Design e Criatividade", "design-criatividade"),
    "administracao": ("Administração e Recursos Humanos", "administracao-recursos-humanos"),
    "idiomas": ("Idiomas e Comunicação", "idiomas-comunicacao"),
}

# As capas são associadas por ordem numérica (photo_1 a photo_44).
CURSOS = [
    ("Preparação para o Mundo do Trabalho", "gestao", 16, "1_MES"),
    ("Programação Back-End", "tecnologia", 56, "3_MESES"),
    ("Programação Front-End com React JS", "tecnologia", 56, "3_MESES"),
    ("Python Básico e Avançado", "tecnologia", 60, "3_MESES"),
    ("Design Gráfico e Multimédia", "design", 52, "3_MESES"),
    ("Redes e Computadores", "tecnologia", 48, "2_MESES"),
    ("Power BI Aplicado a Dados", "tecnologia", 42, "2_MESES"),
    ("CCTV e Sistemas de Vigilância", "tecnologia", 36, "2_MESES"),
    ("CCNA: Redes Cisco", "tecnologia", 60, "3_MESES"),
    ("Assistente Administrativo", "administracao", 40, "2_MESES"),
    ("Gestão Empresarial Avançada", "gestao", 48, "2_MESES"),
    ("Empreendedorismo e Inovação", "gestao", 36, "2_MESES"),
    ("Excel Avançado", "tecnologia", 36, "2_MESES"),
    ("Vendas e Técnicas de Negociação", "marketing", 32, "2_MESES"),
    ("Montagem e Reparação de Computadores", "tecnologia", 48, "2_MESES"),
    ("Vendas Online", "marketing", 28, "1_MES"),
    ("Informática na Óptica do Utilizador", "tecnologia", 36, "2_MESES"),
    ("Recursos Humanos", "administracao", 40, "2_MESES"),
    ("Criação de Conteúdo para Redes Sociais", "marketing", 32, "2_MESES"),
    ("Secretariado Informatizado", "administracao", 36, "2_MESES"),
    ("Inglês para Finalidades Específicas", "idiomas", 48, "3_MESES"),
    ("Fiscalidade Angolana", "administracao", 36, "2_MESES"),
    ("Atendimento ao Cliente", "marketing", 28, "1_MES"),
    ("Importação e Exportação", "gestao", 40, "2_MESES"),
    ("Fiscalidade Aplicada à Empresa", "administracao", 36, "2_MESES"),
    ("Fotografia e Iluminação", "design", 32, "2_MESES"),
    ("Contabilidade Geral", "administracao", 48, "3_MESES"),
    ("Gestão de Stock", "gestao", 28, "1_MES"),
    ("Gestão de Redes Sociais", "marketing", 28, "1_MES"),
    ("Windows Server", "tecnologia", 48, "2_MESES"),
    ("Inteligência Artificial Aplicada", "tecnologia", 40, "2_MESES"),
    ("Design Gráfico Essencial", "design", 48, "2_MESES"),
    ("Marketing Digital", "marketing", 40, "2_MESES"),
    ("Secretariado Administrativo", "administracao", 36, "2_MESES"),
    ("Informática Básica", "tecnologia", 32, "2_MESES"),
    ("Edição de Vídeo", "design", 42, "2_MESES"),
    ("Marketing Digital para Negócios", "marketing", 40, "2_MESES"),
    ("Design Gráfico e Multimédia Profissional", "design", 56, "3_MESES"),
    ("Design Gráfico", "design", 48, "2_MESES"),
    ("Fotografia e Edição", "design", 36, "2_MESES"),
    ("Programação Web", "tecnologia", 56, "3_MESES"),
    ("Audiovisual e Multimédia", "design", 48, "2_MESES"),
    ("Recursos Humanos e Gestão de Pessoal", "administracao", 40, "2_MESES"),
    ("Contabilidade e Fiscalidade", "administracao", 48, "3_MESES"),
]


def natural_key(path):
    return [int(item) if item.isdigit() else item.lower() for item in re.split(r"(\d+)", path.name)]


def capa_paths():
    source = PROJECT_ROOT / "static" / "assets" / "images" / "course" / "mundotec"
    paths = sorted(source.glob("*.jpg"), key=natural_key)
    if len(paths) != len(CURSOS):
        raise RuntimeError(f"Foram encontradas {len(paths)} capas para {len(CURSOS)} cursos.")
    destination = Path(settings.MEDIA_ROOT) / "cursos" / "capas" / "mundotec"
    destination.mkdir(parents=True, exist_ok=True)
    for path in paths:
        shutil.copy2(path, destination / path.name)
    return [f"cursos/capas/mundotec/{path.name}" for path in paths]


def descricao(titulo, categoria):
    return (
        f"Formação prática de {titulo.lower()}, integrada na área de {categoria.lower()} da Mundo da Tecnologia. "
        "Consulte o centro para confirmar requisitos, datas de abertura, valores e modalidade disponíveis."
    )


@transaction.atomic
def carregar_catalogo():
    categorias = {}
    for chave, (nome, slug) in CATEGORIAS.items():
        categoria, _ = Categoria.objects.update_or_create(
            slug=slug,
            defaults={"nome": nome, "descricao": f"Formações de {nome.lower()}."},
        )
        categorias[chave] = categoria

    centro, _ = CentroDeFormacao.objects.update_or_create(
        email=CENTRO["email"],
        defaults={**CENTRO, "nif": None, "localizacao": None},
    )

    capas = capa_paths()
    hoje = date.today()
    turnos = [
        ("MANHA", time(8, 30), time(11, 30), "SEG,QUA,SEX"),
        ("TARDE", time(14, 0), time(17, 0), "TER,QUI"),
        ("NOITE", time(18, 0), time(21, 0), "SEG,QUA,SEX"),
        ("SABADO", time(9, 0), time(13, 0), "SAB"),
    ]

    for index, ((titulo, categoria_chave, horas, duracao), capa) in enumerate(zip(CURSOS, capas), start=1):
        categoria = categorias[categoria_chave]
        curso, _ = Curso.objects.update_or_create(
            centro=centro,
            titulo=titulo,
            defaults={
                "descricao": descricao(titulo, categoria.nome),
                "descricao_curta": f"Formação prática em {titulo.lower()}. Confirme as condições junto do centro.",
                "categoria": categoria,
                "nivel": "B" if index % 3 else "I",
                "idioma": "PT",
                "certificado": True,
                "carga_horaria": horas,
                "is_gratuito": False,
                "moeda": "AOA",
                "preco": 0,
                "preco_inscricao": 0,
                "mensalidade": 0,
                "tipo_cobranca_inscricao": "SEM_PAGAMENTO",
                "modalidade": "PRESENCIAL",
                "duracao": duracao,
                "ativo": True,
                "publicado": False,
                "destaque": index <= 12,
                "requisitos": "Consulte os requisitos e a disponibilidade directamente com o centro.",
                "objetivo_geral": f"Desenvolver competências práticas em {titulo.lower()}.",
                "documento_requerido": "NENHUM",
                "permite_parcelamento": False,
                "max_parcelas": 1,
                "tags": f"mundo da tecnologia, {categoria.nome.lower()}, formação profissional",
                "data_inicio": hoje + timedelta(days=7 + index),
            },
        )
        curso.imagem.name = capa
        curso.save(update_fields=["imagem"])
        Curso.objects.filter(pk=curso.pk).update(publicado=True)

        turno, inicio_hora, fim_hora, dias = turnos[(index - 1) % len(turnos)]
        inicio = hoje + timedelta(days=7 + index)
        Turma.objects.update_or_create(
            codigo=f"MTEC{index:02d}",
            defaults={
                "curso": curso,
                "nome": f"Turma {index:02d} — {titulo}",
                "data_inicio": inicio,
                "data_fim": inicio + timedelta(days=56),
                "turno": turno,
                "horario_inicio": inicio_hora,
                "horario_fim": fim_hora,
                "dias_semana": dias,
                "vagas_totais": 25,
                "vagas_ocupadas": 0,
                "local": centro.endereco,
                "sala": f"Sala {1 + ((index - 1) % 5)}",
                "status": "ABERTA",
                "observacoes": "Turma de catálogo criada a partir de capas fornecidas para validação da plataforma.",
            },
        )

    total = Curso.objects.filter(centro=centro, titulo__in=[item[0] for item in CURSOS], publicado=True, ativo=True).count()
    turmas = Turma.objects.filter(codigo__startswith="MTEC", status="ABERTA").count()
    print("MUNDOTEC_CATALOGO=", {
        "centro": centro.nome,
        "cursos_publicados": total,
        "turmas_abertas": turmas,
    })


if __name__ == "__main__":
    carregar_catalogo()
