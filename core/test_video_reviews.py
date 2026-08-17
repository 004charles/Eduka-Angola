import json

from django.test import TestCase
from django.urls import reverse

from avaliacoes.models import Comentario
from cursos_app.models import Categoria
from cursovideoapp.models import Aula, Curso_video, ProgressoAula
from usuarios.models import Aluno, Usuario


class VideoCourseReviewTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email="avaliador@edukangola.test",
            nome="Aluno Avaliador",
            password="senha-segura-de-teste",
            tipo_usuario="ALUNO",
        )
        self.aluno = Aluno.objects.create(usuario=self.user, nome="Aluno Avaliador")
        category = Categoria.objects.create(nome="Avaliações de Teste", slug="avaliacoes-de-teste")
        self.course = Curso_video.objects.create(
            titulo="Curso para Avaliar",
            descricao="Programa isolado para validar avaliações React.",
            categoria=category,
            is_original_edukangola=True,
        )
        self.lesson = Aula.objects.create(curso=self.course, titulo="Aula de início", ordem=1, duracao_segundos=600)
        self.review_url = reverse("api_react_video_course_review", args=[self.course.slug])

    def test_requires_progress_before_accepting_a_review(self):
        self.course.inscritos.add(self.aluno)
        self.client.force_login(self.user)
        response = self.client.post(self.review_url, data=json.dumps({"avaliacao": 5, "comentario": "Uma avaliação válida com detalhe suficiente."}), content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comentario.objects.count(), 0)

    def test_creates_then_updates_one_review_for_the_same_student(self):
        self.course.inscritos.add(self.aluno)
        ProgressoAula.objects.create(aluno=self.aluno, aula=self.lesson, tempo_assistido=180)
        self.client.force_login(self.user)

        created = self.client.post(self.review_url, data=json.dumps({"avaliacao": 5, "comentario": "Explicações claras e uma experiência muito útil."}), content_type="application/json")
        self.assertEqual(created.status_code, 200)
        self.assertTrue(created.json()["criada"])
        self.assertEqual(Comentario.objects.filter(aluno=self.aluno, curso_video=self.course).count(), 1)

        updated = self.client.post(self.review_url, data=json.dumps({"avaliacao": 4, "comentario": "Atualizei a avaliação depois de rever as aulas."}), content_type="application/json")
        self.assertEqual(updated.status_code, 200)
        self.assertFalse(updated.json()["criada"])
        self.assertEqual(Comentario.objects.filter(aluno=self.aluno, curso_video=self.course).count(), 1)

        detail = self.client.get(reverse("api_public_video_course_detail", args=[self.course.slug])).json()
        self.assertEqual(detail["avaliacoes"]["total"], 1)
        self.assertEqual(detail["avaliacoes"]["media"], 4.0)
        self.assertTrue(detail["permissao_avaliacao"]["pode_avaliar"])
        self.assertEqual(detail["minha_avaliacao"]["avaliacao"], 4)
