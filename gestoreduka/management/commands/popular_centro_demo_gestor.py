import os
from datetime import time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from avaliacoes.models import Comentario
from cursos_app.models import (
    Categoria, CertificadoCurso, Curso, Instrutor, Inscricao, Matricula,
    NotaAluno, ParcelaMatricula, Presenca, Turma,
)
from cursovideoapp.models import Aula, Certificado, Curso_video, ProgressoAula, TurmaVideo
from estagio.models import AreaEstagio, Estagio, InscricaoEstagio
from gestoreduka.models import (
    AnuncioCentro, CentroDeFormacao, CentroSeguimento, Conversa, Evento,
    Filial, Mensagem, PerfilCentroDeFormacao,
)
from pagamentos.models import FinanceiroCentro, RecebimentoCentro
from planos.models import AssinaturaMembro, Plano
from usuarios.models import Aluno, PerfilAluno, Usuario


class Command(BaseCommand):
    help = "Cria dados completos, idempotentes e seguros para testar o GestorEduka."

    manager_email = "gestor.teste@edukangola.local"

    def create_user(self, email, name, user_type="ALUNO", password=None):
        user, created = Usuario.objects.get_or_create(
            email=email,
            defaults={"nome": name, "tipo_usuario": user_type, "is_active": True},
        )
        changed = False
        if user.nome != name:
            user.nome = name
            changed = True
        if user.tipo_usuario != user_type:
            user.tipo_usuario = user_type
            changed = True
        if not user.is_active:
            user.is_active = True
            changed = True
        if created and password:
            user.set_password(password)
            changed = True
        elif created:
            user.set_unusable_password()
            changed = True
        if changed:
            user.save()
        return user

    def handle(self, *args, **options):
        today = timezone.localdate()
        now = timezone.now()
        self.stdout.write(self.style.MIGRATE_HEADING("A preparar o Centro Demonstração GestorEduka…"))

        gestor = self.create_user(
            self.manager_email,
            "Gestor de Teste Eduka",
            "GESTOR",
            os.environ.get("DEMO_GESTOR_PASSWORD"),
        )
        centro, _ = CentroDeFormacao.objects.get_or_create(
            email=self.manager_email,
            defaults={
                "usuario": gestor,
                "nome": "Centro Demonstração GestorEduka",
                "nif": "5417273980",
                "pais": "AO",
                "endereco": "Avenida 4 de Fevereiro, Mutamba",
                "cidade": "Luanda",
                "provincia": "Luanda",
                "telefone": "+244 900 000 000",
                "site": "https://edukangola.example/centro-demo",
                "ativo": True,
                "localizacao": "-8.8137,13.2302",
                "banco_nome": "Banco de Fomento Angola",
                "banco_iban": "AO06000600000012345678901",
                "banco_titular": "Centro Demonstração GestorEduka",
            },
        )
        centro.usuario = gestor
        centro.nome = "Centro Demonstração GestorEduka"
        centro.nif = centro.nif or "5417273980"
        centro.pais = "AO"
        centro.endereco = "Avenida 4 de Fevereiro, Mutamba"
        centro.cidade = "Luanda"
        centro.provincia = "Luanda"
        centro.telefone = "+244 900 000 000"
        centro.site = "https://edukangola.example/centro-demo"
        centro.ativo = True
        centro.localizacao = "-8.8137,13.2302"
        centro.banco_nome = "Banco de Fomento Angola"
        centro.banco_iban = "AO06000600000012345678901"
        centro.banco_titular = "Centro Demonstração GestorEduka"
        centro.save()

        PerfilCentroDeFormacao.objects.update_or_create(
            centro=centro,
            defaults={
                "dono": "Gestor de Teste Eduka",
                "descricao": "Centro de formação profissional orientado para competências digitais, gestão e empregabilidade, com turmas presenciais e acompanhamento próximo.",
                "missao": "Transformar ambição em competências práticas para o mercado de trabalho angolano.",
                "visao": "Ser uma referência nacional na formação aplicada e na ligação entre talento e oportunidades.",
                "valores": "Rigor, inclusão, prática, confiança e inovação.",
                "ano_fundacao": 2021,
                "horario_funcionamento": "Segunda a sábado, 08:00–20:00",
                "tipo": "Centro de formação profissional",
                "modalidade": "Híbrido",
                "facebook": "https://facebook.com/edukangola",
                "instagram": "https://instagram.com/edukangola",
                "linkedin": "https://linkedin.com/company/edukangola",
                "youtube": "https://youtube.com/@edukangola",
                "whatsapp": "+244900000000",
                "destaque": True,
                "verificado": True,
                "slug": "centro-demonstracao-gestoreduka",
            },
        )

        plan, _ = Plano.objects.get_or_create(
            nome="Demonstração Integral",
            defaults={
                "descricao": "Plano de demonstração com todos os módulos do GestorEduka activos.",
                "preco": Decimal("0.00"),
                "limite_cursos": 50,
                "alcance_km": 250,
                "selo_verificacao": True,
                "prioridade_busca": 10,
                "destaque_home": True,
                "acesso_relatorios": True,
                "permite_inscricao_manual": True,
                "permite_gerar_certificado": True,
                "permite_cursos_video": True,
                "limite_cursos_video": 30,
                "ativo": True,
            },
        )
        AssinaturaMembro.objects.update_or_create(
            centro=centro,
            defaults={"plano": plan, "status": "ATIVO", "data_inicio": now - timedelta(days=30), "data_fim": now + timedelta(days=365), "renovacao_automatica": False},
        )

        categories = {}
        for name, description in [
            ("Tecnologia e Dados", "Competências digitais, programação e dados."),
            ("Gestão e Negócios", "Gestão de equipas, vendas e empreendedorismo."),
            ("Idiomas", "Comunicação profissional e idiomas aplicados."),
            ("Design e Comunicação", "Criação visual, marca e produção de conteúdos."),
        ]:
            categories[name], _ = Categoria.objects.get_or_create(
                slug=slugify(name), defaults={"nome": name, "descricao": description}
            )

        branches = []
        for index, values in enumerate([
            ("Filial Mutamba", "Rua Amílcar Cabral, Mutamba", "+244 923 111 222", "filial.mutamba@edukangola.local", "-8.8131", "13.2307"),
            ("Filial Talatona", "Via Expressa, Talatona", "+244 923 333 444", "filial.talatona@edukangola.local", "-8.9166", "13.1825"),
        ]):
            name, address, phone, email, latitude, longitude = values
            branch, _ = Filial.objects.update_or_create(
                email=email,
                defaults={"centro_principal": centro, "nome": name, "endereco": address, "telefone": phone, "whatsapp": phone, "latitude": Decimal(latitude), "longitude": Decimal(longitude), "ativo": True},
            )
            branches.append(branch)

        instructors = []
        instructor_specs = [
            ("Marta dos Santos", "marta.santos.demo@edukangola.local", "Especialista em Dados", "Tecnologia_INFORMACAO", "TECNOLOGIA_INFORMACAO", "Analista de dados com experiência em formação aplicada a equipas e negócios."),
            ("David Manuel", "david.manuel.demo@edukangola.local", "Engenheiro de Redes", "TECNOLOGIA_INFORMACAO", "TECNOLOGIA_INFORMACAO", "Formador técnico focado em redes, suporte e cibersegurança."),
            ("Helena Nzinga", "helena.nzinga.demo@edukangola.local", "Consultora de Gestão", "NEGOCIO", "NEGOCIO", "Consultora em gestão de pequenas empresas e operações comerciais."),
            ("Rui António", "rui.antonio.demo@edukangola.local", "Formador de Inglês", "LINGUAS", "LINGUAS", "Professor de inglês profissional com foco em comunicação no trabalho."),
        ]
        for idx, (name, email, title, area, _, bio) in enumerate(instructor_specs):
            instructor_user = self.create_user(email, name, "INSTRUTOR")
            instructor, _ = Instrutor.objects.update_or_create(
                email=email,
                defaults={"usuario": instructor_user, "centro_de_formacao": centro, "filial": branches[idx % len(branches)], "nome": name, "titulo": title, "biografia": bio, "area_especializacao": area, "ativo": True, "total_alunos": 12 + idx * 4, "total_cursos": 2, "nota_media": Decimal("4.7")},
            )
            instructors.append(instructor)

        course_specs = [
            ("Suporte Técnico e Redes", "Prepare-se para instalar, configurar e manter redes e computadores em ambientes profissionais.", "Tecnologia e Dados", 72, Decimal("85000"), Decimal("7500"), Decimal("18000"), "I", "3_MESES", "PRESENCIAL", 0),
            ("Excel e Power BI para Gestão", "Transforme dados em relatórios claros e úteis para apoiar decisões de negócio.", "Tecnologia e Dados", 60, Decimal("68000"), Decimal("5000"), Decimal("16000"), "I", "2_MESES", "HIBRIDO", 0),
            ("Marketing Digital para Pequenos Negócios", "Aprenda a planear campanhas, conteúdo e vendas digitais de forma prática.", "Gestão e Negócios", 48, Decimal("58000"), Decimal("4500"), Decimal("14500"), "B", "2_MESES", "PRESENCIAL", 1),
            ("Inglês Profissional para Atendimento", "Desenvolva vocabulário e confiança para comunicação profissional em inglês.", "Idiomas", 56, Decimal("62000"), Decimal("5000"), Decimal("15500"), "B", "3_MESES", "PRESENCIAL", 3),
            ("Fundamentos de Cibersegurança", "Conheça boas práticas para proteger dados, contas e operações digitais.", "Tecnologia e Dados", 36, Decimal("45000"), Decimal("3500"), Decimal("12000"), "B", "1_MES", "ONLINE", 1),
            ("Design de Marca para Empreendedores", "Crie uma identidade visual simples e consistente para pequenos negócios.", "Design e Comunicação", 40, Decimal("52000"), Decimal("4000"), Decimal("13000"), "B", "2_MESES", "HIBRIDO", 2),
        ]
        courses = []
        for idx, (title, summary, category_name, hours, price, fee, monthly, level, duration, modality, instructor_idx) in enumerate(course_specs):
            course, _ = Curso.objects.update_or_create(
                centro=centro,
                titulo=title,
                defaults={
                    "descricao": f"{summary} Esta formação integra exercícios práticos, acompanhamento de formador e preparação para desafios reais do mercado.",
                    "descricao_curta": summary,
                    "nivel": level,
                    "idioma": "PT",
                    "categoria": categories[category_name],
                    "certificado": True,
                    "carga_horaria": hours,
                    "is_gratuito": False,
                    "moeda": "AOA",
                    "preco": price,
                    "preco_inscricao": fee,
                    "mensalidade": monthly,
                    "tipo_cobranca_inscricao": "TAXA_E_MENSALIDADE",
                    "modalidade": modality,
                    "duracao": duration,
                    "ativo": True,
                    "publicado": True,
                    "destaque": idx < 3,
                    "vagas_minimas": 8,
                    "data_inicio": today + timedelta(days=10 + idx * 7),
                    "data_inicio_inscricoes": now - timedelta(days=21),
                    "data_fim_inscricoes": now + timedelta(days=90),
                    "permite_parcelamento": True,
                    "max_parcelas": 3,
                    "documento_requerido": "BI",
                    "requisitos": "Documento de identificação e disponibilidade para participar nas sessões.",
                    "objetivo_geral": "Desenvolver competências aplicadas e valorizadas no mercado de trabalho.",
                    "tags": "formação, emprego, competências, Luanda",
                    "visualizacoes": 120 + idx * 37,
                },
            )
            course.instrutores.set([instructors[instructor_idx]])
            course.filiais.set(branches if idx in {0, 1, 4} else [branches[idx % len(branches)]])
            courses.append(course)

        classes = []
        class_specs = [
            (courses[0], branches[0], "Turma Rede · Manhã", "GE-RED-2026-A", today + timedelta(days=14), today + timedelta(days=92), "MANHA", "ABERTA", 26, "Sala de Redes", "SEG,QUA,SEX", instructors[1]),
            (courses[1], branches[0], "Turma Dados · Noite", "GE-DAD-2026-B", today - timedelta(days=12), today + timedelta(days=48), "NOITE", "EM_ANDAMENTO", 22, "Laboratório 2", "TER,QUI", instructors[0]),
            (courses[2], branches[1], "Turma Marketing · Tarde", "GE-MKT-2026-C", today + timedelta(days=21), today + timedelta(days=77), "TARDE", "ABERTA", 20, "Sala Criativa", "SEG,QUA", instructors[2]),
            (courses[3], branches[1], "Turma Inglês · Sábado", "GE-ING-2026-D", today - timedelta(days=75), today - timedelta(days=10), "SABADO", "CONCLUIDA", 18, "Sala 4", "SAB", instructors[3]),
            (courses[4], branches[0], "Turma Segurança · Online", "GE-SEG-2026-E", today + timedelta(days=28), today + timedelta(days=56), "NOITE", "ABERTA", 28, "Sala virtual Eduka", "TER,QUI", instructors[1]),
        ]
        for course, branch, name, code, start, end, turn, status, seats, room, days, instructor in class_specs:
            turma, _ = Turma.objects.update_or_create(
                codigo=code,
                defaults={"curso": course, "filial": branch, "nome": name, "data_inicio": start, "data_fim": end, "turno": turn, "horario_inicio": time(8 if turn == "MANHA" else 14 if turn == "TARDE" else 18, 0), "horario_fim": time(11 if turn == "MANHA" else 17 if turn == "TARDE" else 21, 0), "dias_semana": days, "vagas_totais": seats, "local": branch.endereco, "sala": room, "status": status, "observacoes": "Turma criada para demonstração do GestorEduka.", "instrutor_principal": instructor},
            )
            classes.append(turma)

        student_specs = [
            ("Ana Luísa Vieira", "ana.vieira.demo@edukangola.local"), ("Bruno Miguel", "bruno.miguel.demo@edukangola.local"),
            ("Carla Domingos", "carla.domingos.demo@edukangola.local"), ("Dário Kiala", "dario.kiala.demo@edukangola.local"),
            ("Elisa Tavares", "elisa.tavares.demo@edukangola.local"), ("Fábio Soares", "fabio.soares.demo@edukangola.local"),
            ("Graça Manuel", "graca.manuel.demo@edukangola.local"), ("Hugo António", "hugo.antonio.demo@edukangola.local"),
            ("Inês Paulo", "ines.paulo.demo@edukangola.local"), ("João Luís", "joao.luis.demo@edukangola.local"),
        ]
        students = []
        for idx, (name, email) in enumerate(student_specs):
            user = self.create_user(email, name)
            student, _ = Aluno.objects.get_or_create(usuario=user, defaults={"nome": name, "ativo": True})
            if student.nome != name or not student.ativo:
                student.nome, student.ativo = name, True
                student.save(update_fields=["nome", "ativo"])
            PerfilAluno.objects.get_or_create(aluno=student, defaults={"onboarding_completo": True, "nivel_conhecimento": "B" if idx % 2 else "I", "telefone": f"+244 923 200 {idx:03d}", "biografia": "Perfil de demonstração para testar a experiência Edukangola."})
            students.append(student)

        enrollment_specs = [
            (0, 0, 0, "A", "ONLINE", Decimal("25500")), (1, 0, 0, "P", "ONLINE", None),
            (2, 1, 1, "A", "ONLINE", Decimal("21000")), (3, 1, 1, "N", "ONLINE", None),
            (4, 2, 2, "A", "PRESENCIAL", Decimal("19000")), (5, 3, 3, "A", "PRESENCIAL", Decimal("20500")),
            (6, 4, 4, "C", "ONLINE", Decimal("15500")), (7, 0, 0, "A", "PRESENCIAL", Decimal("25500")),
            (8, 5, 2, "P", "ONLINE", None), (9, 2, 2, "A", "ONLINE", Decimal("19000")),
        ]
        enrollments = []
        for index, course_idx, class_idx, status, kind, paid in enrollment_specs:
            student, course, turma = students[index], courses[course_idx], classes[class_idx]
            enrollment, _ = Inscricao.objects.update_or_create(
                aluno=student,
                curso=course,
                defaults={"turma_escolhida": turma, "status": status, "tipo_inscricao": kind, "forma_pagamento": "TRANSFERENCIA" if kind == "ONLINE" else "DINHEIRO", "valor_pago": paid, "data_pagamento": now - timedelta(days=3 + index) if paid else None, "pagamento_simulado": bool(paid and kind == "ONLINE"), "codigo_simulacao": f"DEMO-PAG-{index + 1:03d}" if paid and kind == "ONLINE" else None, "data_simulacao": now - timedelta(days=3 + index) if paid and kind == "ONLINE" else None, "observacoes": "Registo criado para demonstração operacional."},
            )
            enrollments.append(enrollment)

        matriculation_states = {0: "ATIVA", 2: "ATIVA", 4: "SUSPENSA", 5: "CONCLUIDA", 7: "ATIVA", 9: "ATIVA"}
        matriculations = {}
        for enrollment_index, state in matriculation_states.items():
            enrollment = enrollments[enrollment_index]
            matriculation, _ = Matricula.objects.update_or_create(
                inscricao=enrollment,
                defaults={"aluno": enrollment.aluno, "curso": enrollment.curso, "turma": enrollment.turma_escolhida, "origem": "EDUKA_ANGOLA" if enrollment.tipo_inscricao == "ONLINE" else "PRESENCIAL", "estado": state, "valor_acordado": enrollment.curso.preco, "desconto": Decimal("0"), "responsavel": gestor, "observacoes": "Matrícula de demonstração criada para validar o dossiê académico.", "data_conclusao": now - timedelta(days=5) if state == "CONCLUIDA" else None},
            )
            matriculations[enrollment_index] = matriculation
            for number in (1, 2, 3):
                due = today + timedelta(days=30 * (number - 1))
                paid_installment = number == 1 and state in {"ATIVA", "CONCLUIDA"}
                ParcelaMatricula.objects.update_or_create(
                    matricula=matriculation, numero=number,
                    defaults={"descricao": f"Parcela {number} da formação", "valor": enrollment.curso.mensalidade or Decimal("12000"), "vencimento": due, "status": "PAGA" if paid_installment else "PENDENTE", "valor_pago": enrollment.curso.mensalidade if paid_installment else Decimal("0"), "data_pagamento": now - timedelta(days=2) if paid_installment else None},
                )

        for enrollment_index in (0, 2, 7, 9):
            enrollment = enrollments[enrollment_index]
            turma = enrollment.turma_escolhida
            for days_ago, attendance_state in ((7, "PRESENTE"), (4, "ATRASO"), (1, "PRESENTE")):
                Presenca.objects.update_or_create(turma=turma, inscricao=enrollment, data=today - timedelta(days=days_ago), defaults={"estado": attendance_state, "observacao": "Registo de demonstração."})
            NotaAluno.objects.update_or_create(turma=turma, inscricao=enrollment, avaliacao="Projecto prático", defaults={"nota": Decimal("16.50") if enrollment_index != 2 else Decimal("18.00"), "observacao": "Bom desempenho nas actividades práticas."})

        CertificadoCurso.objects.get_or_create(inscricao=enrollments[5])

        for enrollment_index, value, payment_form in [(0, Decimal("18000"), "DINHEIRO"), (2, Decimal("16000"), "TRANSFERENCIA"), (4, Decimal("14500"), "CARTAO_DEBITO"), (7, Decimal("18000"), "DINHEIRO")]:
            matriculation = matriculations.get(enrollment_index)
            if matriculation:
                RecebimentoCentro.objects.update_or_create(
                    centro=centro, matricula=matriculation, aluno=matriculation.aluno,
                    defaults={"valor": value, "forma": payment_form, "estado": "CONFIRMADO", "recebido_por": gestor, "data_recebimento": now - timedelta(days=enrollment_index + 1), "observacoes": "Recebimento presencial de demonstração."},
                )
        FinanceiroCentro.objects.update_or_create(
            centro=centro, periodo=now.strftime("%B/%Y"),
            defaults={"total_bruto_inscricoes": Decimal("120500"), "percentual_comissao_plataforma": Decimal("12.50"), "valor_comissao_plataforma": Decimal("15062.50"), "valor_liquido_centro": Decimal("105437.50"), "pago": False},
        )

        video_courses = []
        for title, description, category, instructor, price in [
            ("Excel para Decisões Rápidas", "Curso em vídeo com exercícios de Excel e Power BI para gestores e equipas.", categories["Tecnologia e Dados"], instructors[0], Decimal("18000")),
            ("Empreendedorismo na Prática", "Curso em vídeo para estruturar uma ideia de negócio, validar clientes e organizar vendas.", categories["Gestão e Negócios"], instructors[2], Decimal("15000")),
        ]:
            video_course, _ = Curso_video.objects.update_or_create(
                slug=slugify(f"{title}-centro-demo"),
                defaults={"titulo": title, "descricao": description, "instrutor": instructor, "centro": centro, "categoria": category, "destaque": True, "is_pago": True, "preco": price, "is_original_edukangola": False},
            )
            video_courses.append(video_course)
            for lesson_number, lesson_title in enumerate(["Boas-vindas e objectivos", "Fundamentos essenciais", "Aplicação guiada", "Desafio final"], start=1):
                Aula.objects.update_or_create(curso=video_course, ordem=lesson_number, defaults={"titulo": lesson_title, "descricao": f"Aula {lesson_number} do curso em vídeo {title}.", "duracao_segundos": 480 + lesson_number * 90, "visualizacoes": 45 + lesson_number * 19, "requer_conclusao_anterior": lesson_number > 1})
        video_courses[0].inscritos.set([students[0], students[2], students[4], students[7]])
        video_courses[1].inscritos.set([students[1], students[5], students[8]])
        for video_course in video_courses:
            TurmaVideo.objects.update_or_create(codigo=f"VID-{video_course.id}-2026", defaults={"curso": video_course, "nome": f"Acompanhamento {video_course.titulo}", "data_inicio": today + timedelta(days=5), "data_fim": today + timedelta(days=45), "turno": "NOITE", "horario_inicio": time(19, 0), "horario_fim": time(20, 30), "dias_semana": "TER,QUI", "vagas_totais": 40, "vagas_ocupadas": video_course.inscritos.count(), "status": "ABERTA", "observacoes": "Sessões semanais de acompanhamento ao vivo."})
            for lesson in video_course.aulas.all():
                ProgressoAula.objects.update_or_create(aluno=students[0], aula=lesson, defaults={"concluida": lesson.ordem <= 2, "tempo_assistido": lesson.duracao_segundos if lesson.ordem <= 2 else lesson.duracao_segundos // 3})
        Certificado.objects.update_or_create(aluno=students[0], curso=video_courses[0], defaults={"status": "EMITIDO", "aprovado_por": gestor, "nota_final": Decimal("18.00"), "total_exercicios_concluidos": 4, "analise_ia_competencias": "Demonstra domínio de análise de dados e comunicação de indicadores."})

        for student, course, text, rating, approved, response in [
            (students[0], courses[0], "O laboratório e o acompanhamento do formador ajudaram-me a ganhar confiança em redes.", 5, True, "Obrigado, Ana. Continue a praticar com os desafios da turma."),
            (students[2], courses[1], "As aulas de Excel estão claras e consigo aplicar no meu trabalho.", 5, True, "Ficamos felizes com a sua evolução, Carla."),
            (students[4], courses[2], "Gostaria de ver mais exemplos de campanhas para pequenos negócios locais.", 4, False, ""),
        ]:
            Comentario.objects.update_or_create(aluno=student, curso=course, comentario=text, defaults={"avaliacao": rating, "aprovado": approved, "resposta": response or None, "resposta_data": now if response else None})

        for student in students[:5]:
            CentroSeguimento.objects.get_or_create(aluno=student, centro=centro)
        for title, content, important in [
            ("Novas turmas abertas para julho", "Abrimos novas turmas de tecnologia, dados e marketing. Consulte o calendário e reserve a sua vaga.", True),
            ("Workshop de currículo e empregabilidade", "No próximo sábado teremos uma sessão aberta sobre currículo, entrevistas e portfólio profissional.", False),
            ("Laboratório com horário alargado", "O laboratório da Mutamba passa a estar disponível até às 19h00 para alunos com actividades práticas.", False),
        ]:
            AnuncioCentro.objects.update_or_create(centro=centro, titulo=title, defaults={"conteudo": content, "importante": important, "ativo": True})

        for title, description, start_offset, event_type, location, featured in [
            ("Feira de Talento Digital", "Encontro entre alunos, empresas e formadores para apresentar projectos e oportunidades.", 18, "FEIRA", "Auditório da Filial Mutamba", True),
            ("Aula aberta: Power BI", "Sessão demonstrativa com criação de um painel de gestão a partir de dados reais.", 31, "AULA_ABERTA", "Laboratório 2 · Mutamba", False),
            ("Palestra sobre cibersegurança", "Boas práticas de protecção digital para profissionais e pequenos negócios.", 44, "PALESTRA", "Sala Criativa · Talatona", False),
        ]:
            Evento.objects.update_or_create(centro=centro, titulo=title, defaults={"descricao": description, "data_inicio": now + timedelta(days=start_offset), "data_fim": now + timedelta(days=start_offset, hours=3), "local": location, "tipo": event_type, "link_inscricao": "https://edukangola.example/eventos", "destaque": featured})

        internship_area, _ = AreaEstagio.objects.get_or_create(nome="Tecnologia", defaults={"descricao": "Oportunidades em tecnologia e dados.", "icone": "laptop"})
        for title, summary, duration, modality, stipend, days in [
            ("Estágio em Suporte Técnico", "Apoio à equipa de TI e resolução de pedidos internos.", 6, "presencial", Decimal("85000"), 35),
            ("Estágio em Conteúdo Digital", "Criação de peças, publicações e relatórios de desempenho.", 4, "hibrido", Decimal("70000"), 28),
            ("Estágio em Análise de Dados", "Organização e análise de dados operacionais com Excel e Power BI.", 6, "hibrido", Decimal("95000"), 42),
        ]:
            internship, _ = Estagio.objects.update_or_create(
                centro_formacao=centro, titulo=title,
                defaults={"descricao": f"{summary} O estágio inclui orientação, metas mensais e feedback de desempenho.", "resumo": summary, "area": internship_area, "tipo_remuneracao": "remunerado", "valor_remuneracao": stipend, "beneficios": "Mentoria, certificado de participação e acesso ao laboratório.", "modalidade": modality, "duracao_meses": duration, "carga_horaria_semanal": 30, "vagas_disponiveis": 5, "vagas_preenchidas": 1, "local_trabalho": "Centro Demonstração GestorEduka", "cidade": "Luanda", "provincia": "Luanda", "requisitos": "Estar inscrito ou ter concluído formação relevante no centro.", "competencias_desejadas": "Comunicação, responsabilidade e vontade de aprender.", "data_inicio": today + timedelta(days=60), "data_fim": today + timedelta(days=60 + duration * 30), "data_limite_inscricao": today + timedelta(days=days), "ativo": True, "destaque": title == "Estágio em Análise de Dados", "visualizacoes": 80},
            )
            InscricaoEstagio.objects.get_or_create(estagio=internship, aluno=students[0], defaults={"status": "analise", "carta_motivacao": "Quero aplicar as competências desenvolvidas nas formações do centro."})

        for idx, student in enumerate(students[:3]):
            conversation, _ = Conversa.objects.get_or_create(centro=centro, aluno=student, defaults={"ativa": True, "ultima_mensagem": now - timedelta(hours=idx)})
            if not conversation.mensagens.exists():
                Mensagem.objects.create(conversa=conversation, remetente_aluno=student, mensagem="Olá, gostaria de confirmar os materiais necessários para a turma.", data_envio=now - timedelta(days=idx + 1, hours=2))
                Mensagem.objects.create(conversa=conversation, remetente_centro=centro, mensagem="Olá! Os materiais e orientações estão disponíveis na área da turma. Conte connosco.", data_envio=now - timedelta(days=idx + 1))

        self.stdout.write(self.style.SUCCESS("Centro de demonstração populado com sucesso."))
        self.stdout.write("Cursos presenciais: 6 | Turmas: 5 | Alunos: 10 | Inscrições: 10 | Matrículas: 6")
        self.stdout.write("Cursos em vídeo: 2 | Eventos: 3 | Estágios: 3 | Comunicados: 3 | Conversas: 3")
