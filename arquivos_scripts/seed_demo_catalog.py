"""Carga idempotente do catálogo demonstrativo da Edukangola.

Cria cinco categorias e vinte cursos publicados, cada um associado a uma turma
futura aberta. Pode ser executado repetidamente sem duplicar registos.
"""

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

from cursos_app.models import Categoria, Curso, Turma
from cursovideoapp.models import Aula, Curso_video, TurmaVideo
from gestoreduka.models import CentroDeFormacao


CATEGORIAS = [
    ("Tecnologia e Dados", "tecnologia-dados"),
    ("Gestão e Negócios", "gestao-negocios"),
    ("Idiomas e Comunicação", "idiomas-comunicacao"),
    ("Design e Criatividade", "design-criatividade"),
    ("Saúde e Bem-estar", "saude-bem-estar"),
]

CENTROS = [
    {"nome": "Centro Atlas Digital", "email": "atlas.demo@edukangola.test", "nif": "541001001", "cidade": "Luanda", "provincia": "Luanda", "endereco": "Mutamba, Luanda", "telefone": "+244 923 000 101"},
    {"nome": "Centro Horizonte Profissional", "email": "horizonte.demo@edukangola.test", "nif": "541001002", "cidade": "Benguela", "provincia": "Benguela", "endereco": "Rua do Comércio, Benguela", "telefone": "+244 923 000 102"},
    {"nome": "Instituto Kwanza Formação", "email": "kwanza.demo@edukangola.test", "nif": "541001003", "cidade": "Huambo", "provincia": "Huambo", "endereco": "Cidade Alta, Huambo", "telefone": "+244 923 000 103"},
    {"nome": "Escola Criativa do Lobito", "email": "criativa.demo@edukangola.test", "nif": "541001004", "cidade": "Lobito", "provincia": "Benguela", "endereco": "Restinga, Lobito", "telefone": "+244 923 000 104"},
    {"nome": "Academia Vida & Cuidado", "email": "vida.demo@edukangola.test", "nif": "541001005", "cidade": "Luanda", "provincia": "Luanda", "endereco": "Talatona, Luanda", "telefone": "+244 923 000 105"},
]

CURSOS = [
    {"categoria": "Tecnologia e Dados", "centro": 0, "titulo": "Fundamentos de Informática", "curta": "Aprenda a utilizar o computador, a internet e ferramentas de produtividade com segurança.", "descricao": "Formação prática para quem quer ganhar autonomia no computador, criar documentos, organizar ficheiros e comunicar online com confiança.", "horas": 36, "nivel": "B", "idioma": "PT", "modalidade": "PRESENCIAL", "duracao": "2_MESES", "preco": 30000, "taxa": 2500, "mensalidade": 7500, "cobranca": "APENAS_TAXA", "tags": "informática, computador, produtividade"},
    {"categoria": "Tecnologia e Dados", "centro": 0, "titulo": "Python Aplicado a Dados", "curta": "Use Python para organizar, analisar e visualizar dados de forma prática.", "descricao": "Curso introdutório de programação com foco em análise de dados, automatização de tarefas e criação de relatórios simples.", "horas": 48, "nivel": "I", "idioma": "PT", "modalidade": "HIBRIDO", "duracao": "3_MESES", "preco": 60000, "taxa": 5000, "mensalidade": 15000, "cobranca": "TAXA_E_MENSALIDADE", "tags": "python, dados, programação"},
    {"categoria": "Tecnologia e Dados", "centro": 1, "titulo": "Excel e Power BI para Gestão", "curta": "Transforme folhas de cálculo em relatórios claros para apoiar decisões.", "descricao": "Aprenda Excel intermédio, tabelas dinâmicas, fórmulas e introdução ao Power BI para análise de indicadores de negócio.", "horas": 42, "nivel": "I", "idioma": "PT", "modalidade": "ONLINE", "duracao": "2_MESES", "preco": 45000, "taxa": 0, "mensalidade": 0, "cobranca": "CURSO_COMPLETO", "tags": "excel, power bi, gestão, relatórios"},
    {"categoria": "Tecnologia e Dados", "centro": 2, "titulo": "Segurança Digital para Equipas", "curta": "Proteja contas, documentos e comunicações da sua organização.", "descricao": "Formação essencial sobre palavras-passe, phishing, cópias de segurança e boas práticas de segurança digital no trabalho.", "horas": 20, "nivel": "B", "idioma": "PT", "modalidade": "ONLINE", "duracao": "1_MES", "preco": 0, "taxa": 0, "mensalidade": 0, "cobranca": "SEM_PAGAMENTO", "tags": "segurança digital, cibersegurança, equipas", "gratuito": True},
    {"categoria": "Gestão e Negócios", "centro": 1, "titulo": "Gestão de Pequenos Negócios", "curta": "Planeie, organize e acompanhe um pequeno negócio com mais clareza.", "descricao": "Curso para empreendedores que precisam de estruturar vendas, custos, atendimento e objetivos mensais do seu negócio.", "horas": 40, "nivel": "B", "idioma": "PT", "modalidade": "PRESENCIAL", "duracao": "2_MESES", "preco": 38000, "taxa": 3000, "mensalidade": 9000, "cobranca": "APENAS_TAXA", "tags": "empreendedorismo, gestão, pequeno negócio"},
    {"categoria": "Gestão e Negócios", "centro": 0, "titulo": "Marketing Digital e Redes Sociais", "curta": "Construa uma presença digital consistente para promover produtos e serviços.", "descricao": "Aprenda a definir público, criar calendário editorial, produzir conteúdos e acompanhar resultados nas principais redes sociais.", "horas": 36, "nivel": "B", "idioma": "PT", "modalidade": "HIBRIDO", "duracao": "2_MESES", "preco": 42000, "taxa": 3500, "mensalidade": 10500, "cobranca": "TAXA_E_MENSALIDADE", "tags": "marketing digital, redes sociais, conteúdo"},
    {"categoria": "Gestão e Negócios", "centro": 2, "titulo": "Atendimento ao Cliente de Excelência", "curta": "Desenvolva comunicação, escuta ativa e resolução de problemas no atendimento.", "descricao": "Formação prática para profissionais que atendem presencialmente ou por canais digitais e querem melhorar a experiência do cliente.", "horas": 24, "nivel": "B", "idioma": "PT", "modalidade": "PRESENCIAL", "duracao": "1_MES", "preco": 26000, "taxa": 2000, "mensalidade": 0, "cobranca": "APENAS_TAXA", "tags": "atendimento, vendas, comunicação"},
    {"categoria": "Gestão e Negócios", "centro": 1, "titulo": "Finanças Pessoais e Empresariais", "curta": "Organize receitas, despesas e metas financeiras com ferramentas simples.", "descricao": "Curso para quem quer controlar o orçamento pessoal ou do negócio, definir prioridades e tomar decisões financeiras informadas.", "horas": 28, "nivel": "B", "idioma": "PT", "modalidade": "ONLINE", "duracao": "1_MES", "preco": 0, "taxa": 0, "mensalidade": 0, "cobranca": "SEM_PAGAMENTO", "tags": "finanças, orçamento, negócio", "gratuito": True},
    {"categoria": "Idiomas e Comunicação", "centro": 0, "titulo": "Inglês para o Trabalho", "curta": "Comunique com segurança em contextos profissionais de língua inglesa.", "descricao": "Desenvolva vocabulário, compreensão e expressões para reuniões, e-mails, apresentações e atendimento profissional.", "horas": 60, "nivel": "B", "idioma": "EN", "modalidade": "HIBRIDO", "duracao": "3_MESES", "preco": 54000, "taxa": 4000, "mensalidade": 12500, "cobranca": "TAXA_E_MENSALIDADE", "tags": "inglês, trabalho, comunicação"},
    {"categoria": "Idiomas e Comunicação", "centro": 1, "titulo": "Inglês para Atendimento e Turismo", "curta": "Pratique expressões de inglês úteis para receber, orientar e apoiar clientes.", "descricao": "Curso aplicado ao atendimento, hotelaria, restauração e turismo, com foco em situações reais do dia a dia.", "horas": 48, "nivel": "B", "idioma": "EN", "modalidade": "PRESENCIAL", "duracao": "2_MESES", "preco": 45000, "taxa": 3000, "mensalidade": 11000, "cobranca": "APENAS_TAXA", "tags": "inglês, turismo, atendimento"},
    {"categoria": "Idiomas e Comunicação", "centro": 2, "titulo": "Comunicação Profissional em Português", "curta": "Escreva e comunique com clareza no contexto de trabalho.", "descricao": "Aperfeiçoe e-mails, relatórios, apresentações e comunicação oral para uma presença profissional mais segura.", "horas": 24, "nivel": "B", "idioma": "PT", "modalidade": "ONLINE", "duracao": "1_MES", "preco": 22000, "taxa": 0, "mensalidade": 0, "cobranca": "CURSO_COMPLETO", "tags": "português, comunicação, escrita"},
    {"categoria": "Idiomas e Comunicação", "centro": 3, "titulo": "Francês Prático para Iniciantes", "curta": "Dê os primeiros passos em francês para situações pessoais e profissionais.", "descricao": "Formação introdutória com pronúncia, vocabulário, compreensão e diálogos práticos para iniciantes.", "horas": 44, "nivel": "B", "idioma": "FR", "modalidade": "PRESENCIAL", "duracao": "2_MESES", "preco": 40000, "taxa": 3000, "mensalidade": 9500, "cobranca": "APENAS_TAXA", "tags": "francês, idiomas, comunicação"},
    {"categoria": "Design e Criatividade", "centro": 3, "titulo": "Design Gráfico com Canva", "curta": "Crie peças visuais para redes sociais, apresentações e comunicação de marcas.", "descricao": "Aprenda princípios de composição, cor, tipografia e utilização prática do Canva para materiais digitais profissionais.", "horas": 30, "nivel": "B", "idioma": "PT", "modalidade": "ONLINE", "duracao": "1_MES", "preco": 28000, "taxa": 2000, "mensalidade": 0, "cobranca": "APENAS_TAXA", "tags": "canva, design gráfico, criatividade"},
    {"categoria": "Design e Criatividade", "centro": 3, "titulo": "Adobe Photoshop Essencial", "curta": "Edite imagens e prepare conteúdos visuais para projetos criativos.", "descricao": "Curso prático de Photoshop para tratamento de imagem, recortes, composição e exportação para meios digitais.", "horas": 46, "nivel": "I", "idioma": "PT", "modalidade": "PRESENCIAL", "duracao": "2_MESES", "preco": 52000, "taxa": 4500, "mensalidade": 12000, "cobranca": "TAXA_E_MENSALIDADE", "tags": "photoshop, imagem, design"},
    {"categoria": "Design e Criatividade", "centro": 0, "titulo": "Criação de Conteúdo para Redes", "curta": "Planeie e produza conteúdo relevante para uma audiência digital.", "descricao": "Desenvolva ideias, formatos, calendário de publicação e boas práticas de escrita e imagem para redes sociais.", "horas": 26, "nivel": "B", "idioma": "PT", "modalidade": "HIBRIDO", "duracao": "1_MES", "preco": 25000, "taxa": 0, "mensalidade": 0, "cobranca": "SEM_PAGAMENTO", "tags": "conteúdo, redes sociais, criatividade"},
    {"categoria": "Design e Criatividade", "centro": 1, "titulo": "UX UI para Produtos Digitais", "curta": "Entenda como desenhar experiências digitais úteis, claras e acessíveis.", "descricao": "Curso introdutório de pesquisa, fluxos, prototipagem e princípios de interface para produtos digitais.", "horas": 52, "nivel": "I", "idioma": "PT", "modalidade": "ONLINE", "duracao": "3_MESES", "preco": 58000, "taxa": 5000, "mensalidade": 14000, "cobranca": "TAXA_E_MENSALIDADE", "tags": "ux, ui, produto digital, design"},
    {"categoria": "Saúde e Bem-estar", "centro": 4, "titulo": "Primeiros Socorros e Suporte Básico de Vida", "curta": "Aprenda procedimentos iniciais de resposta segura em situações de emergência.", "descricao": "Formação prática sobre avaliação inicial, suporte básico de vida, cuidados imediatos e acionamento responsável dos serviços de emergência.", "horas": 20, "nivel": "B", "idioma": "PT", "modalidade": "PRESENCIAL", "duracao": "1_MES", "preco": 32000, "taxa": 2500, "mensalidade": 0, "cobranca": "APENAS_TAXA", "tags": "primeiros socorros, saúde, emergência"},
    {"categoria": "Saúde e Bem-estar", "centro": 4, "titulo": "Cuidados ao Idoso", "curta": "Desenvolva competências humanas e práticas para apoiar pessoas idosas.", "descricao": "Curso sobre rotinas de cuidado, segurança, comunicação, mobilidade e bem-estar no acompanhamento de pessoas idosas.", "horas": 40, "nivel": "B", "idioma": "PT", "modalidade": "HIBRIDO", "duracao": "2_MESES", "preco": 46000, "taxa": 3500, "mensalidade": 11000, "cobranca": "TAXA_E_MENSALIDADE", "tags": "idoso, cuidados, saúde"},
    {"categoria": "Saúde e Bem-estar", "centro": 4, "titulo": "Higiene e Segurança Alimentar", "curta": "Aplique boas práticas de higiene na manipulação e conservação de alimentos.", "descricao": "Formação para profissionais de restauração e pequenos negócios alimentares, com foco em prevenção e qualidade.", "horas": 24, "nivel": "B", "idioma": "PT", "modalidade": "ONLINE", "duracao": "1_MES", "preco": 0, "taxa": 0, "mensalidade": 0, "cobranca": "SEM_PAGAMENTO", "tags": "higiene, alimentos, segurança", "gratuito": True},
    {"categoria": "Saúde e Bem-estar", "centro": 4, "titulo": "Bem-estar e Saúde Mental no Trabalho", "curta": "Promova rotinas saudáveis, comunicação e prevenção no ambiente profissional.", "descricao": "Curso de sensibilização para reconhecer sinais de desgaste, reforçar bem-estar e criar práticas de apoio no trabalho.", "horas": 18, "nivel": "B", "idioma": "PT", "modalidade": "ONLINE", "duracao": "1_MES", "preco": 18000, "taxa": 0, "mensalidade": 0, "cobranca": "CURSO_COMPLETO", "tags": "saúde mental, bem-estar, trabalho"},
]

IMAGENS = [
    "course-online-01.jpg", "course-online-02.jpg", "course-online-03.jpg", "course-online-04.jpg",
    "course-elegant-01.jpg", "course-elegant-02.jpg", "course-elegant-03.jpg", "course-elegant-04.jpg",
    "course-list-01.jpg", "course-list-02.jpg", "course-list-03.jpg", "course-list-04.jpg",
    "art-course-01.png", "art-course-02.png", "art-course-03.png", "art-course-05.png",
    "medical-course-01.jpg", "medical-course-02.jpg", "medical-course-03.jpg", "coach-course-01.jpg",
]

VIDEO_CURSOS = [
    {
        "titulo": "Excel para o Dia a Dia", "categoria": "Tecnologia e Dados", "centro": None,
        "descricao": "Vídeo-curso original da Edukangola para dominar fórmulas, tabelas e relatórios simples no Excel.",
        "preco": 15000, "original": True, "imagem": 2,
        "aulas": [
            ("Boas-vindas e preparação do ficheiro", 420, "Conheça o percurso do curso e prepare o seu primeiro ficheiro de trabalho."),
            ("Fórmulas essenciais para cálculos", 840, "Use somas, médias, percentagens e referências de células."),
            ("Organização com tabelas e filtros", 690, "Estruture informação para encontrar e analisar dados rapidamente."),
            ("Relatório final com gráficos", 960, "Transforme a sua tabela num relatório visual claro."),
        ],
    },
    {
        "titulo": "Marketing Digital com Mentoria", "categoria": "Gestão e Negócios", "centro": 0,
        "descricao": "Vídeo-curso de um centro de formação, complementado por turmas de acompanhamento e discussão prática.",
        "preco": 22000, "original": False, "imagem": 6,
        "aulas": [
            ("Definir o público e os objetivos", 720, "Estabeleça objetivos mensuráveis e identifique quem pretende alcançar."),
            ("Criar um calendário de conteúdos", 900, "Planeie publicações consistentes para os seus canais digitais."),
            ("Campanhas e métricas principais", 780, "Entenda alcance, interação e conversão para melhorar decisões."),
            ("Projeto prático de campanha", 1080, "Construa uma campanha simples para aplicar os conceitos estudados."),
        ],
    },
]


def preparar_capas():
    origem = PROJECT_ROOT / "static" / "assets" / "images" / "course"
    destino = Path(settings.MEDIA_ROOT) / "cursos"
    destino.mkdir(parents=True, exist_ok=True)
    nomes = []
    for indice, ficheiro in enumerate(IMAGENS, start=1):
        extensao = Path(ficheiro).suffix
        nome_destino = f"demo-catalogo-{indice:02d}{extensao}"
        shutil.copyfile(origem / ficheiro, destino / nome_destino)
        nomes.append(f"cursos/{nome_destino}")
    return nomes


def preparar_capa_video(indice):
    origem = PROJECT_ROOT / "static" / "assets" / "images" / "course" / IMAGENS[indice]
    destino = Path(settings.MEDIA_ROOT) / "cursos" / "capas"
    destino.mkdir(parents=True, exist_ok=True)
    nome = f"demo-video-{indice + 1:02d}{origem.suffix}"
    shutil.copyfile(origem, destino / nome)
    return f"cursos/capas/{nome}"


@transaction.atomic
def carregar_catalogo():
    categorias = {}
    for nome, slug in CATEGORIAS:
        categoria, _ = Categoria.objects.update_or_create(
            slug=slug,
            defaults={"nome": nome, "descricao": f"Formações de {nome.lower()} para o catálogo de demonstração."},
        )
        categorias[nome] = categoria

    # Arquiva o curso de teste anterior sem apagar o histórico. Assim, o
    # catálogo público fica limitado aos vinte cursos desta carga demonstrativa.
    Curso.objects.filter(
        titulo="Informática Básica Demo",
    ).update(publicado=False, ativo=False)

    centros = []
    for dados in CENTROS:
        centro, _ = CentroDeFormacao.objects.update_or_create(
            email=dados["email"],
            defaults={**dados, "ativo": True, "pais": "AO"},
        )
        centros.append(centro)

    capas = preparar_capas()
    hoje = date.today()
    turnos = [
        ("MANHA", time(8, 30), time(11, 30), "SEG,QUA,SEX"),
        ("TARDE", time(14, 0), time(17, 0), "TER,QUI"),
        ("NOITE", time(18, 0), time(21, 0), "SEG,QUA,SEX"),
        ("SABADO", time(9, 0), time(13, 0), "SAB"),
    ]

    for indice, dados in enumerate(CURSOS, start=1):
        centro = centros[dados["centro"]]
        gratuito = dados.get("gratuito", False)
        curso, _ = Curso.objects.update_or_create(
            centro=centro,
            titulo=dados["titulo"],
            defaults={
                "descricao": dados["descricao"],
                "descricao_curta": dados["curta"],
                "categoria": categorias[dados["categoria"]],
                "nivel": dados["nivel"],
                "idioma": dados["idioma"],
                "certificado": True,
                "carga_horaria": dados["horas"],
                "is_gratuito": gratuito,
                "moeda": "AOA",
                "preco": 0 if gratuito else dados["preco"],
                "preco_inscricao": 0 if gratuito else dados["taxa"],
                "mensalidade": 0 if gratuito else dados["mensalidade"],
                "tipo_cobranca_inscricao": "SEM_PAGAMENTO" if gratuito else dados["cobranca"],
                # A oferta simplificada mantém as formações de centros como presenciais.
                # O conteúdo gravado é publicado pelo produto Curso_video.
                "modalidade": "PRESENCIAL",
                "duracao": dados["duracao"],
                "ativo": True,
                # A publicação é feita por QuerySet após gravar a capa, para
                # não disparar notificações externas ao criar dados de teste.
                "publicado": False,
                "destaque": indice <= 10,
                "requisitos": "Sem pré-requisitos formais. Vontade de aprender e participação nas aulas.",
                "objetivo_geral": dados["curta"],
                "documento_requerido": "NENHUM",
                "permite_parcelamento": not gratuito and dados["mensalidade"] > 0,
                "max_parcelas": 3 if not gratuito and dados["mensalidade"] > 0 else 1,
                "tags": dados["tags"],
                "data_inicio": hoje + timedelta(days=7 + indice * 2),
            },
        )
        curso.imagem.name = capas[indice - 1]
        curso.save(update_fields=["imagem"])
        Curso.objects.filter(pk=curso.pk).update(publicado=True)

        turno, inicio_hora, fim_hora, dias = turnos[(indice - 1) % len(turnos)]
        inicio = hoje + timedelta(days=7 + indice * 2)
        Turma.objects.update_or_create(
            codigo=f"DEMO{indice:02d}",
            defaults={
                "curso": curso,
                "nome": f"Turma de Demonstração {indice:02d}",
                "data_inicio": inicio,
                "data_fim": inicio + timedelta(days=56),
                "turno": turno,
                "horario_inicio": inicio_hora,
                "horario_fim": fim_hora,
                "dias_semana": dias,
                "vagas_totais": 24 + (indice % 4) * 4,
                "vagas_ocupadas": (indice * 3) % 11,
                "local": centro.endereco or centro.nome,
                "sala": f"Sala {1 + (indice % 5)}",
                "status": "ABERTA",
                "observacoes": "Turma criada para demonstrar o catálogo público da Edukangola.",
            },
        )

    for indice, dados in enumerate(VIDEO_CURSOS, start=1):
        centro = centros[dados["centro"]] if dados["centro"] is not None else None
        video, _ = Curso_video.objects.update_or_create(
            titulo=dados["titulo"],
            defaults={
                "descricao": dados["descricao"],
                "categoria": categorias[dados["categoria"]],
                "centro": centro,
                "is_pago": dados["preco"] > 0,
                "preco": dados["preco"],
                "is_original_edukangola": dados["original"],
                "destaque": True,
            },
        )
        video.capa.name = preparar_capa_video(dados["imagem"])
        video.save(update_fields=["capa"])
        for ordem, (titulo, duracao, descricao) in enumerate(dados["aulas"], start=1):
            Aula.objects.update_or_create(
                curso=video,
                ordem=ordem,
                defaults={"titulo": titulo, "duracao_segundos": duracao, "descricao": descricao},
            )
        if not dados["original"]:
            TurmaVideo.objects.update_or_create(
                codigo=f"VIDEODEMO{indice:02d}",
                defaults={
                    "curso": video,
                    "nome": "Turma de acompanhamento online",
                    "data_inicio": hoje + timedelta(days=14),
                    "data_fim": hoje + timedelta(days=42),
                    "turno": "NOITE",
                    "horario_inicio": time(18, 30),
                    "horario_fim": time(20, 0),
                    "dias_semana": "TER,QUI",
                    "vagas_totais": 30,
                    "vagas_ocupadas": 6,
                    "status": "ABERTA",
                    "observacoes": "Turma de acompanhamento para vídeo-curso de demonstração.",
                },
            )

    resumo = {
        "categorias": Categoria.objects.filter(slug__in=[slug for _, slug in CATEGORIAS]).count(),
        "cursos": Curso.objects.filter(titulo__in=[curso["titulo"] for curso in CURSOS], publicado=True, ativo=True).count(),
        "turmas_abertas": Turma.objects.filter(codigo__startswith="DEMO", status="ABERTA", vagas_disponiveis__gt=0).count(),
        "video_cursos": Curso_video.objects.filter(titulo__in=[curso["titulo"] for curso in VIDEO_CURSOS]).count(),
    }
    print(f"CATALOGO_DEMO={resumo}")


if __name__ == "__main__":
    carregar_catalogo()
