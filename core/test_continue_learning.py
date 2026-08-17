import json

from django.test import RequestFactory, TestCase

from core.views import public_home_data
from cursos_app.models import Categoria
from cursovideoapp.models import Aula, Curso_video, ProgressoAula
from usuarios.models import Aluno, Usuario


class ContinueLearningPayloadTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = Usuario.objects.create_user(
            email="continuidade@edukangola.test",
            nome="Aluno de Continuidade",
            password="senha-segura-de-teste",
            tipo_usuario="ALUNO",
        )
        self.aluno = Aluno.objects.create(usuario=self.user, nome="Aluno de Continuidade")
        self.category = Categoria.objects.create(nome="Tecnologia de Teste", slug="tecnologia-de-teste")

    def create_video_course(self, title):
        course = Curso_video.objects.create(
            titulo=title,
            descricao="Curso criado para validar o payload de continuidade.",
            categoria=self.category,
            is_original_edukangola=True,
        )
        first_lesson = Aula.objects.create(curso=course, titulo="Primeira aula", ordem=1, duracao_segundos=600)
        second_lesson = Aula.objects.create(curso=course, titulo="Segunda aula", ordem=2, duracao_segundos=600)
        course.inscritos.add(self.aluno)
        return course, first_lesson, second_lesson

    def test_returns_only_started_and_unfinished_video_courses(self):
        in_progress, first_lesson, _ = self.create_video_course("Curso em andamento")
        completed, completed_first, completed_second = self.create_video_course("Curso concluído")
        ProgressoAula.objects.create(aluno=self.aluno, aula=first_lesson, concluida=True, tempo_assistido=600)
        ProgressoAula.objects.create(aluno=self.aluno, aula=completed_first, concluida=True, tempo_assistido=600)
        ProgressoAula.objects.create(aluno=self.aluno, aula=completed_second, concluida=True, tempo_assistido=600)

        request = self.factory.get("/api/react/home/")
        request.user = self.user
        response = public_home_data(request)
        payload = json.loads(response.content)

        self.assertEqual(len(payload["continuar_video"]), 1)
        item = payload["continuar_video"][0]
        self.assertEqual(item["video_slug"], in_progress.slug)
        self.assertEqual(item["aulas_concluidas"], 1)
        self.assertEqual(item["total_aulas"], 2)
        self.assertEqual(item["proxima_aula"], "Segunda aula")
        self.assertGreater(item["progresso"], 0)
        self.assertLess(item["progresso"], 100)
        self.assertNotEqual(item["video_slug"], completed.slug)
