import json

from django.test import TestCase

from cursos_app.models import Categoria
from cursovideoapp.models import Curso_video


class ReactCheckoutVideoTest(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nome='Vídeo Checkout', slug='video-checkout')
        self.curso = Curso_video.objects.create(
            titulo='Vídeo gratuito para checkout',
            descricao='Curso usado para validar a criação de acesso visitante.',
            categoria=categoria,
            is_pago=False,
        )

    def test_visitante_ganha_acesso_a_video_gratuito_com_nome_e_email(self):
        response = self.client.post(
            f'/curso_video/api/react/{self.curso.slug}/acesso/',
            data=json.dumps({'nome': 'Visitante Vídeo', 'email': 'visitante.video@test.com'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['status'], 'liberado')
        self.assertTrue(self.curso.inscritos.filter(usuario__email='visitante.video@test.com').exists())
