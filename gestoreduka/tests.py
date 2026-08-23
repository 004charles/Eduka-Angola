from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from .models import CandidaturaCentro


class CentroCandidaturaApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.payload = {'email': 'centro@example.com', 'nif': '541 001 999'}

    @patch('gestoreduka.api_views.enviar_email_brevo', return_value=True)
    def test_link_unico_confirma_conclui_e_nao_reutiliza(self, enviar_email):
        response = self.client.post('/api/public/centros/candidatura/solicitar/', self.payload, format='json')
        self.assertEqual(response.status_code, 200)
        candidatura = CandidaturaCentro.objects.get()
        self.assertTrue(enviar_email.called)

        confirm = self.client.get(f'/api/public/centros/candidatura/confirmar/?convite={candidatura.link_token}')
        self.assertEqual(confirm.status_code, 200)
        self.assertEqual(confirm.data['email'], self.payload['email'])

        complete = self.client.post(
            '/api/public/centros/candidatura/concluir/',
            {
                **self.payload,
                'candidatura_id': candidatura.id,
                'convite': str(candidatura.link_token),
                'nome_centro': 'Centro Teste Verificado',
                'nome_gestor': 'Gestor Teste',
                'senha': 'SenhaSegura123',
                'confirm_senha': 'SenhaSegura123',
            },
            format='json',
        )
        self.assertEqual(complete.status_code, 201)
        candidatura.refresh_from_db()
        self.assertTrue(candidatura.link_usado)
        self.assertEqual(candidatura.status, 'CONCLUIDA')

        reuse = self.client.get(f'/api/public/centros/candidatura/confirmar/?convite={candidatura.link_token}')
        self.assertEqual(reuse.status_code, 404)


class CentroPlanosPublicosTests(TestCase):
    def test_a_vitrina_publica_devolve_quatro_planos_activos_ordenados(self):
        response = APIClient().get('/api/public/centros/planos/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([plano['nome'] for plano in response.data], ['Essencial', 'Crescimento', 'Profissional', 'Rede'])
        self.assertEqual(len(response.data), 4)
        self.assertEqual(response.data[0]['preco'], '0.00')
        self.assertFalse(response.data[-1]['permite_cursos_video'])
