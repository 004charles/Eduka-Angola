from django.test import TestCase

from cursos_app.models import Categoria, Curso
from usuarios.models import Usuario
from .models import CentroDeFormacao


class ReactGestorDashboardTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='gestor.react@test.com', nome='Gestor React', password='SenhaSegura123', tipo_usuario='GESTOR')
        self.centro = CentroDeFormacao.objects.create(usuario=self.user, nome='Centro React', email=self.user.email)
        categoria = Categoria.objects.create(nome='Tecnologia React', slug='tecnologia-react')
        self.curso = Curso.objects.create(centro=self.centro, titulo='Curso React', descricao='Curso de teste.', categoria=categoria, carga_horaria=12, preco=1000, publicado=False, ativo=True)

    def test_dashboard_exige_sessao_e_restringe_os_dados_ao_centro_do_gestor(self):
        self.assertEqual(self.client.get('/gestoreduka/api/react/dashboard/').status_code, 302)
        self.client.force_login(self.user)
        response = self.client.get('/gestoreduka/api/react/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['centro']['id'], self.centro.id)
        self.assertEqual(response.json()['cursos'][0]['id'], self.curso.id)

    def test_gestor_publica_apenas_curso_do_proprio_centro(self):
        self.client.force_login(self.user)
        response = self.client.post(f'/gestoreduka/api/react/cursos/{self.curso.id}/publicacao/', data='{"publicado": true}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.curso.refresh_from_db()
        self.assertTrue(self.curso.publicado)

    def test_formulario_react_de_cursos_devolve_apenas_metadados_do_centro(self):
        self.client.force_login(self.user)
        response = self.client.get('/gestoreduka/api/react/cursos/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('categorias', response.json())
        self.assertIn('instrutores', response.json())
        self.assertIn('modalidade', response.json()['escolhas'])
