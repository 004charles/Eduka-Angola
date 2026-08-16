from django.test import TestCase
import json
from unittest.mock import patch

from django.test import Client, TestCase

from .models import Aluno, CodigoVerificacao, Usuario
from gestoreduka.models import CentroDeFormacao

class UserUnificationTest(TestCase):
    def setUp(self):
        self.user_aluno = Usuario.objects.create_user(
            email='aluno@test.com',
            nome='Teste Aluno',
            password='testpassword123',
            tipo_usuario='ALUNO'
        )
        self.user_centro = Usuario.objects.create_user(
            email='centro@test.com',
            nome='Teste Centro',
            password='testpassword123',
            tipo_usuario='GESTOR'
        )

    def test_aluno_profile_creation(self):
        aluno = Aluno.objects.create(
            usuario=self.user_aluno,
            nome='Teste Aluno'
        )
        self.assertEqual(aluno.usuario.email, 'aluno@test.com')
        self.assertEqual(self.user_aluno.aluno_profile, aluno)

    def test_centro_profile_creation(self):
        centro = CentroDeFormacao.objects.create(
            usuario=self.user_centro,
            nome='Teste Centro',
            email='centro@test.com'
        )
        self.assertEqual(centro.usuario.email, 'centro@test.com')
        self.assertEqual(self.user_centro.centro_profile, centro)

    def test_cascade_delete(self):
        Aluno.objects.create(usuario=self.user_aluno, nome='Teste Aluno')
        self.user_aluno.delete()
        self.assertEqual(Aluno.objects.count(), 0)

    def test_user_types(self):
        self.assertEqual(self.user_aluno.tipo_usuario, 'ALUNO')
        self.assertEqual(self.user_centro.tipo_usuario, 'GESTOR')


class ReactAuthApiTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='aluno.react@test.com',
            nome='Aluno React',
            password='SenhaSegura123',
            tipo_usuario='ALUNO',
        )
        Aluno.objects.create(usuario=self.user, nome='Aluno React')

    def post_json(self, url, data):
        return self.client.post(url, data=json.dumps(data), content_type='application/json')

    def test_login_react_cria_sessao_e_preserva_destino_local(self):
        response = self.post_json('/auth/api/react/login/', {
            'email': self.user.email,
            'senha': 'SenhaSegura123',
            'next': '/cursos/2/',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(response.json()['redirect'], '/cursos/2/')
        self.assertEqual(str(self.client.session.get('_auth_user_id')), str(self.user.id))

    def test_resumo_react_do_aluno_exige_sessao_e_retorna_dados_reais(self):
        sem_sessao = self.client.get('/auth/api/react/aluno/resumo/')
        self.assertEqual(sem_sessao.status_code, 401)

        self.client.force_login(self.user)
        response = self.client.get('/auth/api/react/aluno/resumo/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['aluno']['nome'], 'Aluno React')
        self.assertEqual(data['resumo']['cursos_ativos'], 0)
        self.assertEqual(data['continuar_aprender'], [])

    @patch('usuarios.views.enviar_codigo_verificacao')
    def test_registro_react_cria_conta_pendente_de_verificacao(self, mocked_email):
        response = self.post_json('/auth/api/react/registro/', {
            'nome': 'Nova Aluna',
            'email': 'nova.react@test.com',
            'senha': 'SenhaSegura123',
            'confirmar_senha': 'SenhaSegura123',
            'next': '/video-cursos/excel-para-o-dia-a-dia/',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['requires_verification'])
        user = Usuario.objects.get(email='nova.react@test.com')
        self.assertFalse(user.is_active)
        self.assertTrue(Aluno.objects.filter(usuario=user, ativo=False).exists())
        mocked_email.assert_called_once_with('nova.react@test.com', 'CADASTRO')

    @patch('usuarios.views.enviar_codigo_verificacao')
    def test_registro_react_aceita_origem_de_previsualizacao_com_csrf(self, mocked_email):
        client = Client(enforce_csrf_checks=True)
        origin = 'https://5173-teste.manus.computer'
        csrf_response = client.get('/auth/api/react/csrf/', HTTP_ORIGIN=origin)
        self.assertEqual(csrf_response.status_code, 200)
        token = client.cookies['csrftoken'].value
        response = client.post(
            '/auth/api/react/registro/',
            data=json.dumps({
                'nome': 'Aluna com CSRF',
                'email': 'aluna.csrf@test.com',
                'senha': 'SenhaSegura123',
                'confirmar_senha': 'SenhaSegura123',
            }),
            content_type='application/json',
            HTTP_ORIGIN=origin,
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['requires_verification'])
        mocked_email.assert_called_once_with('aluna.csrf@test.com', 'CADASTRO')

    @patch('usuarios.views.enviar_email_confirmacao_aluno')
    def test_verificacao_react_ativa_conta_e_inicia_sessao(self, mocked_welcome):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
        Aluno.objects.filter(usuario=self.user).update(ativo=False)
        CodigoVerificacao.objects.create(email=self.user.email, codigo='123456', tipo='CADASTRO')
        session = self.client.session
        session['email_verificacao'] = self.user.email
        session['public_auth_next'] = '/cursos/2/'
        session.save()

        response = self.post_json('/auth/api/react/verificar-email/', {'codigo': '123456'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(response.json()['redirect'], '/cursos/2/')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(Aluno.objects.get(usuario=self.user).ativo)
        self.assertEqual(str(self.client.session.get('_auth_user_id')), str(self.user.id))
        mocked_welcome.assert_called_once_with(self.user.nome, self.user.email)
