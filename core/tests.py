from django.test import TestCase

from cursos_app.models import Categoria
from cursovideoapp.models import Curso_video
from usuarios.models import Aluno, Usuario

from .models import Publicidade


class EducationalSponsorApiTest(TestCase):
    def test_home_expoe_apenas_patronicios_com_destino_interno(self):
        Publicidade.objects.create(
            titulo='Bolsa Edukangola',
            subtitulo='Oportunidade educativa interna.',
            tag_label='Selecção Edukangola',
            posicao='GERAL',
            url_destino='/bolsas',
            ativo=True,
        )
        Publicidade.objects.create(
            titulo='Destino externo bloqueado',
            posicao='GERAL',
            url_destino='https://exemplo-publicidade.test/oferta',
            ativo=True,
        )

        response = self.client.get('/api/public/home/')
        self.assertEqual(response.status_code, 200)
        patrocinios = response.json()['patrocinios_educativos']
        self.assertEqual(len(patrocinios), 1)
        self.assertEqual(patrocinios[0]['titulo'], 'Bolsa Edukangola')
        self.assertEqual(patrocinios[0]['url'], '/bolsas')


class StudentDashboardVideoRouteTest(TestCase):
    def test_dashboard_serializa_curso_em_video_na_rota_react_mesmo_com_slug_unicode(self):
        user = Usuario.objects.create_user(
            email='aluno.dashboard@test.com',
            nome='Aluno do Painel',
            password='SenhaSegura123',
            tipo_usuario='ALUNO',
        )
        aluno = Aluno.objects.create(usuario=user, nome='Aluno do Painel')
        categoria = Categoria.objects.create(nome='Tecnologia', slug='tecnologia-dashboard')
        video = Curso_video.objects.create(
            titulo='Comunicação Digital Profissional',
            descricao='Curso de demonstração.',
            categoria=categoria,
            slug='comunicação-digital-profissional',
        )
        video.inscritos.add(aluno)

        self.client.force_login(user)
        response = self.client.get('/api/react/aluno/dashboard/')

        self.assertEqual(response.status_code, 200)
        curso = response.json()['continuar_aprender'][0]
        self.assertEqual(curso['detalhe_url'], '/video-cursos/comunicação-digital-profissional')
        self.assertEqual(curso['aprendizagem_url'], '/aprender/video/comunicação-digital-profissional')
