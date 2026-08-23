import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import resolve

from core.react_delivery import react_application
from gestoreduka.models import ModuloPublico
from usuarios.models import CodigoVerificacao, Usuario


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

    @patch('usuarios.views.enviar_codigo_verificacao')
    def test_recuperacao_administrativa_redefine_senha_e_inicia_sessao(self, enviar_codigo):
        pedido = self.client.post('/auth/api/react/admin/recuperar-senha/', data=json.dumps({
            'email': self.staff.email,
        }), content_type='application/json')
        CodigoVerificacao.objects.create(email=self.staff.email, codigo='654321', tipo='RECUPERACAO')
        redefinicao = self.client.post('/auth/api/react/admin/redefinir-senha/', data=json.dumps({
            'codigo': '654321',
            'senha': 'NovaSenhaSegura123',
            'confirmar_senha': 'NovaSenhaSegura123',
        }), content_type='application/json')

        self.assertEqual(pedido.status_code, 200)
        enviar_codigo.assert_called_once_with(self.staff.email, 'RECUPERACAO')
        self.assertEqual(redefinicao.status_code, 200)
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.check_password('NovaSenhaSegura123'))
        self.assertEqual(self.client.get('/api/react/administracao/resumo/').status_code, 200)

    def test_bootstrap_temporario_cria_admin_so_com_token_de_ambiente(self):
        with patch.dict('os.environ', {'ADMIN_BOOTSTRAP_TOKEN': 'token-bootstrap-seguro'}, clear=False):
            resposta = self.client.post('/auth/api/react/admin/criar-conta/', data=json.dumps({
                'nome': 'Nova Administradora',
                'email': 'nova.admin@teste.com',
                'senha': 'SenhaBootstrapForte123',
                'confirmar_senha': 'SenhaBootstrapForte123',
                'token': 'token-bootstrap-seguro',
            }), content_type='application/json')

        nova_admin = Usuario.objects.get(email='nova.admin@teste.com')
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(nova_admin.is_staff)
        self.assertTrue(nova_admin.is_superuser)
        self.assertEqual(nova_admin.tipo_usuario, 'ADMIN')

    def test_bootstrap_temporario_recusa_token_invalido(self):
        with patch.dict('os.environ', {'ADMIN_BOOTSTRAP_TOKEN': 'token-bootstrap-seguro'}, clear=False):
            resposta = self.client.post('/auth/api/react/admin/criar-conta/', data=json.dumps({
                'nome': 'Tentativa',
                'email': 'tentativa@teste.com',
                'senha': 'SenhaBootstrapForte123',
                'confirmar_senha': 'SenhaBootstrapForte123',
                'token': 'invalido',
            }), content_type='application/json')

        self.assertEqual(resposta.status_code, 403)
        self.assertFalse(Usuario.objects.filter(email='tentativa@teste.com').exists())

    def test_staff_consulta_metricas_e_controla_modulo(self):
        self.client.force_login(self.staff)
        resumo = self.client.get('/api/react/administracao/resumo/')
        atualizacao = self.client.post('/api/react/administracao/modulos/', data='{"chave":"BOLSAS","ativo":true}', content_type='application/json')

        self.assertEqual(resumo.status_code, 200)
        self.assertIn('metricas', resumo.json())
        self.assertEqual(atualizacao.status_code, 200)
        self.modulo.refresh_from_db()
        self.assertTrue(self.modulo.ativo)
