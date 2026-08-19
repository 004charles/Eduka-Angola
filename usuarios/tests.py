from django.test import TestCase, override_settings
import json
from unittest.mock import patch

from django.test import Client, TestCase

from .models import Aluno, CodigoVerificacao, NotificacaoAluno, PreferenciaNotificacaoAluno, SubscricaoWebPush, Usuario
from .web_push import enviar_notificacao_web_push
from gestoreduka.models import CentroDeFormacao, Conversa, Mensagem, NotificacaoGestor

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


class StudentMessagingApiTest(TestCase):
    def setUp(self):
        self.aluno_user = Usuario.objects.create_user(email='chat.aluno@test.com', nome='Aluna Chat', password=None, tipo_usuario='ALUNO')
        self.aluno = Aluno.objects.create(usuario=self.aluno_user, nome='Aluna Chat')
        self.gestor_user = Usuario.objects.create_user(email='chat.gestor@test.com', nome='Gestor Chat', password=None, tipo_usuario='GESTOR')
        self.centro = CentroDeFormacao.objects.create(usuario=self.gestor_user, nome='Centro Chat', email='chat.centro@test.com', ativo=True)

    def post_json(self, url, data):
        return self.client.post(url, data=json.dumps(data), content_type='application/json')

    def test_aluno_inicia_conversa_envia_e_recebe_notificacoes(self):
        self.client.force_login(self.aluno_user)
        create_response = self.post_json('/auth/api/react/aluno/conversas/iniciar/', {'centro_id': self.centro.id})
        self.assertEqual(create_response.status_code, 201)
        conversa_id = create_response.json()['conversa']['id']

        sent_response = self.post_json(f'/auth/api/react/aluno/conversas/{conversa_id}/mensagens/', {'mensagem': 'Gostaria de confirmar o horário da turma.'})
        self.assertEqual(sent_response.status_code, 201)
        self.assertTrue(NotificacaoGestor.objects.filter(centro=self.centro, tipo='MENSAGEM', link__contains=f'conversa={conversa_id}').exists())

        conversa = Conversa.objects.get(id=conversa_id)
        resposta = Mensagem.objects.create(conversa=conversa, remetente_centro=self.centro, mensagem='A turma inicia às 18h, de segunda a sexta.')
        notification = NotificacaoAluno.objects.get(aluno=self.aluno, tipo='CHAT')
        self.assertIn(f'conversa={conversa_id}', notification.link)

        detail_response = self.client.get(f'/auth/api/react/aluno/conversas/{conversa_id}/')
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(len(detail_response.json()['mensagens']), 2)
        resposta.refresh_from_db()
        notification.refresh_from_db()
        self.assertTrue(resposta.lida)
        self.assertTrue(notification.lida)

        self.client.force_login(self.gestor_user)
        manager_detail = self.client.get(f'/gestoreduka/api/react/conversas/{conversa_id}/')
        self.assertEqual(manager_detail.status_code, 200)
        self.assertEqual(manager_detail.json()['conversa']['aluno'], self.aluno.nome)
        self.assertFalse(NotificacaoGestor.objects.filter(centro=self.centro, tipo='MENSAGEM', lida=False).exists())


@override_settings(VAPID_PUBLIC_KEY='B' * 87, VAPID_PRIVATE_KEY='test-private-vapid-key', VAPID_SUBJECT='mailto:suporte@edukangola.com')
class WebPushApiTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='push.aluno@test.com', nome='Aluna Push', password='SenhaSegura123', tipo_usuario='ALUNO')
        self.aluno = Aluno.objects.create(usuario=self.user, nome='Aluna Push')
        self.endpoint = 'https://push.example.test/subscription/abc123'
        self.subscription = {'endpoint': self.endpoint, 'keys': {'p256dh': 'a' * 65, 'auth': 'b' * 24}}

    def post_json(self, url, data):
        return self.client.post(url, data=json.dumps(data), content_type='application/json')

    def test_estado_exige_sessao_de_aluno(self):
        response = self.client.get('/auth/api/react/aluno/push/estado/')
        self.assertEqual(response.status_code, 401)

    def test_subscricao_persiste_apenas_para_o_aluno_autenticado(self):
        self.client.force_login(self.user)
        response = self.post_json('/auth/api/react/aluno/push/subscrever/', self.subscription)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        subscricao = SubscricaoWebPush.objects.get(endpoint=self.endpoint)
        self.assertEqual(subscricao.aluno, self.aluno)
        self.assertTrue(subscricao.ativa)
        self.assertTrue(PreferenciaNotificacaoAluno.objects.get(aluno=self.aluno).receber_push)

        state = self.client.get('/auth/api/react/aluno/push/estado/')
        self.assertEqual(state.status_code, 200)
        self.assertTrue(state.json()['configured'])
        self.assertEqual(state.json()['subscription_count'], 1)

    def test_cancelamento_desactiva_a_subscricao_do_proprio_aluno(self):
        SubscricaoWebPush.objects.create(aluno=self.aluno, endpoint=self.endpoint, chave_p256dh='a' * 65, chave_auth='b' * 24)
        PreferenciaNotificacaoAluno.objects.filter(aluno=self.aluno).update(receber_push=True)
        self.client.force_login(self.user)
        response = self.post_json('/auth/api/react/aluno/push/cancelar/', {'endpoint': self.endpoint})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SubscricaoWebPush.objects.get(endpoint=self.endpoint).ativa)
        self.assertFalse(PreferenciaNotificacaoAluno.objects.get(aluno=self.aluno).receber_push)

    @patch('pywebpush.webpush')
    def test_entrega_usa_vapid_e_respeita_o_consentimento(self, mocked_webpush):
        SubscricaoWebPush.objects.create(aluno=self.aluno, endpoint=self.endpoint, chave_p256dh='a' * 65, chave_auth='b' * 24)
        PreferenciaNotificacaoAluno.objects.filter(aluno=self.aluno).update(receber_push=True)
        notificacao = NotificacaoAluno(aluno=self.aluno, titulo='Novo curso', mensagem='Já pode explorar uma nova formação.', link='/cursos', tipo='CURSO')
        notificacao._skip_web_push_delivery = True
        notificacao.save()

        result = enviar_notificacao_web_push(notificacao.id)
        self.assertEqual(result, {'configured': True, 'sent': 1, 'failed': 0})
        mocked_webpush.assert_called_once()
        self.assertEqual(mocked_webpush.call_args.kwargs['vapid_private_key'], 'test-private-vapid-key')

        PreferenciaNotificacaoAluno.objects.filter(aluno=self.aluno).update(receber_push=False)
        result = enviar_notificacao_web_push(notificacao.id)
        self.assertEqual(result, {'configured': True, 'sent': 0, 'failed': 0})
        mocked_webpush.assert_called_once()
