import json

from django.test import TestCase
from django.urls import resolve

from core.react_delivery import react_application
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

    def test_admin_principal_entrega_react_e_contingencia_fica_interna(self):
        self.assertIs(resolve('/admin/').func, react_application)
        resposta = self.client.get('/admin-interno/')
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/admin-interno/login/', resposta['Location'])

    def test_sessao_administrativa_existente_acessa_painel_react(self):
        self.client.force_login(self.staff)
        chave_sessao = self.client.cookies['eduka_session'].value
        self.client.cookies['eduka_admin_session'] = chave_sessao
        del self.client.cookies['eduka_session']

        resposta = self.client.get('/api/react/administracao/resumo/')

        self.assertEqual(resposta.status_code, 200)

    def test_login_react_administrativo_cria_sessao_isolada(self):
        resposta = self.client.post('/auth/api/react/admin/login/', data=json.dumps({
            'email': self.staff.email,
            'senha': 'SenhaSegura123',
        }), content_type='application/json')

        self.assertEqual(resposta.status_code, 200)
        self.assertIn('eduka_admin_session', self.client.cookies)
        self.assertEqual(self.client.get('/api/react/administracao/resumo/').status_code, 200)

    def test_login_react_administrativo_rejeita_conta_comum(self):
        resposta = self.client.post('/auth/api/react/admin/login/', data=json.dumps({
            'email': self.aluno.email,
            'senha': 'SenhaSegura123',
        }), content_type='application/json')

        self.assertEqual(resposta.status_code, 401)

    def test_staff_consulta_metricas_e_controla_modulo(self):
        self.client.force_login(self.staff)
        resumo = self.client.get('/api/react/administracao/resumo/')
        atualizacao = self.client.post('/api/react/administracao/modulos/', data='{"chave":"BOLSAS","ativo":true}', content_type='application/json')

        self.assertEqual(resumo.status_code, 200)
        self.assertIn('metricas', resumo.json())
        self.assertEqual(atualizacao.status_code, 200)
        self.modulo.refresh_from_db()
        self.assertTrue(self.modulo.ativo)
