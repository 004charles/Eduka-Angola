from unittest.mock import Mock, patch

import requests
from django.core.cache import cache
from django.test import Client, TestCase, override_settings


class PublicEdukaAiApiTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client()

    def test_requires_a_question(self):
        response = self.client.post('/api/public/eduka-ai/perguntar/', data='{}', content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('pergunta', response.json()['detail'].lower())

    @override_settings(GROQ_API_KEY='test-key')
    @patch('core.views.requests.post')
    def test_returns_factual_guidance_for_enrollment_without_calling_model(self, mocked_post):
        response = self.client.post(
            '/api/public/eduka-ai/perguntar/',
            data='{"question":"Como faço uma inscrição?"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn('catálogo', payload['answer'].lower())
        self.assertIn({'label': 'Como funciona', 'path': '/como-funciona'}, payload['links'])
        mocked_post.assert_not_called()

    @override_settings(GROQ_API_KEY='test-key')
    @patch('core.views.requests.post')
    def test_guides_future_instructors_to_the_react_application_without_calling_model(self, mocked_post):
        for question in ('Como me torno formador?', 'Quero ser formador na Edukangola', 'Posso publicar um curso?'):
            with self.subTest(question=question):
                response = self.client.post(
                    '/api/public/eduka-ai/perguntar/',
                    data=f'{{"question":"{question}"}}',
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, 200)
                payload = response.json()
                self.assertIn('configurações', payload['answer'])
                self.assertIn('analisada', payload['answer'])
                self.assertIn({'label': 'Configurações da conta', 'path': '/aluno/configuracoes'}, payload['links'])
        mocked_post.assert_not_called()

    @override_settings(GROQ_API_KEY='test-key')
    @patch('core.views.requests.post')
    def test_identifies_the_platform_creators_without_calling_model(self, mocked_post):
        questions = [
            'Quem são os criadores da plataforma Edukangola?',
            'Quem desenvolveu a Edukangola?',
            'Quem é o desenvolvedor deste site?',
            'Quem está por detrás da plataforma?',
        ]

        for question in questions:
            with self.subTest(question=question):
                response = self.client.post(
                    '/api/public/eduka-ai/perguntar/',
                    data=f'{{"question":"{question}"}}',
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, 200)
                payload = response.json()
                self.assertEqual(payload['answer'], 'Carlos Muquissi, Nelson Muquissi e Herlander Vandik são os criadores da Edukangola.')
                self.assertIn({'label': 'Conhecer a Edukangola', 'path': '/sobre'}, payload['links'])
        mocked_post.assert_not_called()

    @override_settings(GROQ_API_KEY='test-key')
    @patch('core.views.requests.post')
    def test_returns_a_scoped_answer_and_navigation_link(self, mocked_post):
        mocked_response = Mock()
        mocked_response.raise_for_status.return_value = None
        mocked_response.json.return_value = {'choices': [{'message': {'content': 'Pode explorar os **centros** e comparar os cursos publicados.'}}]}
        mocked_post.return_value = mocked_response

        response = self.client.post(
            '/api/public/eduka-ai/perguntar/',
            data='{"question":"Que centros existem na plataforma?"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertIn('explorar os centros', payload['answer'].lower())
        self.assertNotIn('**', payload['answer'])
        self.assertIn({'label': 'Conhecer centros', 'path': '/centros'}, payload['links'])
        mocked_post.assert_called_once()

    @override_settings(GROQ_API_KEY='test-key')
    @patch('core.views.time.sleep')
    @patch('core.views.requests.post')
    def test_retries_once_after_a_temporary_provider_failure(self, mocked_post, mocked_sleep):
        successful_response = Mock()
        successful_response.raise_for_status.return_value = None
        successful_response.json.return_value = {'choices': [{'message': {'content': 'Pode explorar os centros publicados.'}}]}
        mocked_post.side_effect = [requests.Timeout(), successful_response]

        response = self.client.post(
            '/api/public/eduka-ai/perguntar/',
            data='{"question":"Que centros existem na plataforma?"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(mocked_post.call_count, 2)
        mocked_sleep.assert_called_once_with(0.4)

    @override_settings(GROQ_API_KEY='test-key')
    @patch('core.views.time.sleep')
    @patch('core.views.requests.post', side_effect=requests.Timeout())
    def test_returns_a_clear_message_only_after_retry_is_exhausted(self, mocked_post, mocked_sleep):
        response = self.client.post(
            '/api/public/eduka-ai/perguntar/',
            data='{"question":"Que centros existem na plataforma?"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn('ocupada', response.json()['detail'].lower())
        self.assertEqual(mocked_post.call_count, 2)
        mocked_sleep.assert_called_once_with(0.4)

    @override_settings(GROQ_API_KEY='test-key')
    @patch('core.views.requests.post')
    def test_does_not_retry_a_provider_error_that_is_not_temporary(self, mocked_post):
        provider_response = Mock(status_code=400)
        provider_error = requests.HTTPError(response=provider_response)
        mocked_post.side_effect = provider_error

        response = self.client.post(
            '/api/public/eduka-ai/perguntar/',
            data='{"question":"Que centros existem na plataforma?"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 503)
        mocked_post.assert_called_once()

    @override_settings(GROQ_API_KEY='test-key')
    @patch('core.views.requests.post')
    def test_visitor_rate_limit_is_preserved_before_provider_calls(self, mocked_post):
        for _ in range(8):
            response = self.client.post(
                '/api/public/eduka-ai/perguntar/',
                data='{"question":"Como faço uma inscrição?"}',
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            '/api/public/eduka-ai/perguntar/',
            data='{"question":"Como faço uma inscrição?"}',
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 429)
        mocked_post.assert_not_called()
