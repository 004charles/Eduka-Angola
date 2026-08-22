import json
import os
from unittest.mock import Mock, patch

import requests
from django.test import TestCase, override_settings

from usuarios.models import Usuario

from .models import Autor, Livro


class CartesiaVoiceApiTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='leitor.cartesia@test.com', nome='Leitor Cartesia', password='SenhaSegura123', tipo_usuario='ALUNO')
        self.author = Autor.objects.create(nome='Autora da Biblioteca Cartesia')
        self.book = Livro.objects.create(
            titulo='Livro de Teste Cartesia', autor=self.author, sinopse='Texto autorizado para testes.',
            categoria='Tecnologia', estado=Livro.ESTADO_PUBLICADO, direitos_confirmados=True,
            conteudo_leitura='# Capítulo um\n\nEste é um trecho autorizado para narração natural.',
        )
        self.client.force_login(self.user)

    @override_settings(CARTESIA_API_KEY='test-key', CARTESIA_VOICE_ID='voice-test')
    @patch('biblioteca.views.requests.post')
    def test_generates_audio_only_from_the_authorized_book_chapter(self, mocked_post):
        provider_response = Mock()
        provider_response.raise_for_status.return_value = None
        provider_response.content = b'ID3-cartesia-audio'
        mocked_post.return_value = provider_response

        response = self.client.post(
            f'/api/react/biblioteca/{self.book.slug}/voz/',
            data=json.dumps({'capitulo': 0, 'velocidade': 1.0, 'texto': 'ignorar este texto arbitrario'}),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'audio/mpeg')
        self.assertEqual(response.content, b'ID3-cartesia-audio')
        request_data = mocked_post.call_args.kwargs
        self.assertEqual(request_data['headers']['Cartesia-Version'], '2026-08-14')
        self.assertEqual(request_data['json']['voice'], {'id': 'voice-test'})
        self.assertEqual(request_data['json']['transcript'], 'Capítulo um Este é um trecho autorizado para narração natural.')
        self.assertNotIn('ignorar este texto arbitrario', str(request_data['json']))

    @override_settings(CARTESIA_API_KEY='', CARTESIA_VOICE_ID='')
    @patch.dict(os.environ, {'CARTESIA_API_KEY': '', 'CARTESIA_VOICE_ID': ''})
    @patch('biblioteca.views.requests.post')
    def test_returns_a_safe_message_when_cartesia_is_not_configured(self, mocked_post):
        response = self.client.post(f'/api/react/biblioteca/{self.book.slug}/voz/', data='{}', content_type='application/json')

        self.assertEqual(response.status_code, 503)
        self.assertIn('preparada', response.json()['detail'])
        mocked_post.assert_not_called()

    @override_settings(CARTESIA_API_KEY='test-key', CARTESIA_VOICE_ID='voice-test')
    @patch('biblioteca.views.requests.post', side_effect=requests.Timeout())
    def test_handles_a_temporary_cartesia_failure_without_leaking_provider_details(self, mocked_post):
        response = self.client.post(f'/api/react/biblioteca/{self.book.slug}/voz/', data='{}', content_type='application/json')

        self.assertEqual(response.status_code, 503)
        self.assertIn('temporariamente indisponível', response.json()['detail'])
        mocked_post.assert_called_once()

    @override_settings(CARTESIA_API_KEY='test-key', CARTESIA_VOICE_ID='voice-test')
    @patch('biblioteca.views.requests.post')
    def test_rejects_an_invalid_chapter_before_calling_cartesia(self, mocked_post):
        response = self.client.post(f'/api/react/biblioteca/{self.book.slug}/voz/', data=json.dumps({'capitulo': 4}), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        mocked_post.assert_not_called()

    @override_settings(CARTESIA_API_KEY='test-key', CARTESIA_VOICE_ID='voice-test')
    @patch('biblioteca.views.requests.post')
    def test_does_not_narrate_a_book_without_confirmed_distribution_rights(self, mocked_post):
        restricted_book = Livro.objects.create(
            titulo='Livro sem Direitos', autor=self.author, sinopse='Não pode ser narrado.', categoria='Tecnologia',
            estado=Livro.ESTADO_PUBLICADO, direitos_confirmados=False, conteudo_leitura='Texto restrito.',
        )

        response = self.client.post(f'/api/react/biblioteca/{restricted_book.slug}/voz/', data='{}', content_type='application/json')

        self.assertEqual(response.status_code, 404)
        mocked_post.assert_not_called()
