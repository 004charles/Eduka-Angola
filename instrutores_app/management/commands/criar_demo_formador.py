from decimal import Decimal

from django.contrib.auth import authenticate
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from cursos_app.models import Categoria, Instrutor
from cursovideoapp.models import Aula, ComentarioAula, Curso_video
from usuarios.models import Aluno, Usuario


class Command(BaseCommand):
    help = "Cria um cenário idempotente para demonstrar o painel React do formador."

    instructor_email = "formador.demo@edukangola.local"
    instructor_password = "EdukaDemo2026"
    student_email = "aluna.demo.formador@edukangola.local"

    def ensure_user(self, email, name, user_type, password):
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
        if created or not user.check_password(password):
            user.set_password(password)
            changed = True
        if changed:
            user.save()
        return user

    def handle(self, *args, **options):
        category, _ = Categoria.objects.get_or_create(
            slug="tecnologia-e-dados",
            defaults={
                "nome": "Tecnologia e Dados",
                "descricao": "Competências digitais, programação e análise de dados.",
            },
        )

        instructor_user = self.ensure_user(
            self.instructor_email,
            "Amélia Ventura",
            "INSTRUTOR",
            self.instructor_password,
        )
        instructor, _ = Instrutor.objects.update_or_create(
            email=self.instructor_email,
            defaults={
                "usuario": instructor_user,
                "nome": "Amélia Ventura",
                "titulo": "Especialista em Dados e Excel",
                "biografia": "Formadora de competências digitais com experiência em Excel, análise de dados e aprendizagem aplicada ao trabalho.",
                "area_especializacao": "TECNOLOGIA_INFORMACAO",
                "ativo": True,
                "nota_media": Decimal("4.8"),
            },
        )

        course, _ = Curso_video.objects.update_or_create(
            slug="excel-aplicado-ao-trabalho-demo-formador",
            defaults={
                "titulo": "Excel aplicado ao trabalho",
                "descricao": "Aprenda a organizar dados, criar relatórios claros e tomar decisões mais rápidas com ferramentas práticas de Excel.",
                "categoria": category,
                "instrutor": instructor,
                "destaque": True,
                "is_pago": False,
                "preco": Decimal("0"),
                "is_original_edukangola": False,
            },
        )

        lesson, _ = Aula.objects.update_or_create(
            curso=course,
            ordem=1,
            defaults={
                "titulo": "Organize a informação antes de analisar",
                "descricao": "Uma introdução à estruturação de tabelas e à preparação dos dados para relatórios úteis.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "duracao_segundos": 720,
            },
        )

        student_user = self.ensure_user(
            self.student_email,
            "Lurdes Miguel",
            "ALUNO",
            "EdukaAluno2026!",
        )
        student, _ = Aluno.objects.get_or_create(
            usuario=student_user,
            defaults={"nome": "Lurdes Miguel", "ativo": True},
        )
        if student.nome != "Lurdes Miguel" or not student.ativo:
            student.nome = "Lurdes Miguel"
            student.ativo = True
            student.save(update_fields=["nome", "ativo"])
        course.inscritos.add(student)

        question = ComentarioAula.objects.filter(
            aluno=student,
            aula=lesson,
            parent__isnull=True,
        ).first()
        if not question:
            ComentarioAula.objects.create(
                aluno=student,
                aula=lesson,
                texto="Como posso escolher as colunas mais importantes para o primeiro relatório?",
            )

        authenticated = authenticate(username=self.instructor_email, password=self.instructor_password)
        if not authenticated or authenticated.pk != instructor_user.pk:
            self.stderr.write(self.style.ERROR("Não foi possível validar as credenciais do formador de demonstração."))
            return

        self.stdout.write(self.style.SUCCESS("Cenário de formador criado com sucesso."))
        self.stdout.write(f"E-mail: {self.instructor_email}")
        self.stdout.write(f"Palavra-passe: {self.instructor_password}")
        self.stdout.write(f"Curso: {course.titulo} | Aula: {lesson.titulo}")
        self.stdout.write("Inclui uma dúvida pendente de Lurdes Miguel para testar a resposta do formador.")
        self.stdout.write("Credenciais autenticadas com sucesso no Django.")
