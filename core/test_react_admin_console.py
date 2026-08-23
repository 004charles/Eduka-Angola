from django.test import TestCase

from gestoreduka.models import ModuloPublico
from usuarios.models import Usuario


class ReactAdminConsoleTests(TestCase):
    def setUp(self):
        self.staff = Usuario.objects.create_user(email='admin.react@test.com', nome='Admin React', password='SenhaSegura123', tipo_usuario='ADMIN', is_staff=True)
        self.aluno = Usuario.objects.create_user(email='aluno.react@test.com', nome='Aluno React', password='SenhaSegura123', tipo_usuario='ALUNO')
        self.modulo, _ = ModuloPublico.objects.get_or_create(chave='BOLSAS')

    def test_resumo_exige_conta_administrativa(self):
        self.assertEqual(self.client.get('/api/react/administracao/resumo/').status_code, 401)
        self.client.force_login(self.aluno)
        self.assertEqual(self.client.get('/api/react/administracao/resumo/').status_code, 403)

    def test_staff_consulta_metricas_e_controla_modulo(self):
        self.client.force_login(self.staff)
        resumo = self.client.get('/api/react/administracao/resumo/')
        atualizacao = self.client.post('/api/react/administracao/modulos/', data='{"chave":"BOLSAS","ativo":true}', content_type='application/json')

        self.assertEqual(resumo.status_code, 200)
        self.assertIn('metricas', resumo.json())
        self.assertEqual(atualizacao.status_code, 200)
        self.modulo.refresh_from_db()
        self.assertTrue(self.modulo.ativo)
