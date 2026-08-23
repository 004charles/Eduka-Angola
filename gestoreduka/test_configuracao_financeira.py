import json

from django.core.exceptions import ValidationError
from django.test import TestCase

from usuarios.models import Usuario
from .models import CentroDeFormacao, ConfiguracaoFinanceiraCentro


class ConfiguracaoFinanceiraCentroTests(TestCase):
    def setUp(self):
        self.gestor_mz = Usuario.objects.create_user(email='gestor.mz@test.com', nome='Gestor MZ', password='SenhaSegura123', tipo_usuario='GESTOR')
        self.centro_mz = CentroDeFormacao.objects.create(usuario=self.gestor_mz, nome='Centro Moçambique', email=self.gestor_mz.email, pais='MZ')
        self.gestor_ao = Usuario.objects.create_user(email='gestor.ao@test.com', nome='Gestor AO', password='SenhaSegura123', tipo_usuario='GESTOR')
        self.centro_ao = CentroDeFormacao.objects.create(usuario=self.gestor_ao, nome='Centro Angola', email=self.gestor_ao.email, pais='AO')

    def test_configuracao_mostra_a_moeda_correta_para_o_pais_do_centro(self):
        self.client.force_login(self.gestor_mz)
        response = self.client.get('/gestoreduka/api/react/financeiro/')

        self.assertEqual(response.status_code, 200)
        configuracao = response.json()['configuracao_financeira']
        self.assertEqual(configuracao['moeda_cobranca'], 'MZN')
        self.assertFalse(configuracao['pode_cobrar'])
        self.assertEqual(configuracao['estado'], 'PENDENTE_VALIDACAO')

    def test_gestor_guarda_a_configuracao_do_proprio_centro_sem_activar_cobranca(self):
        self.client.force_login(self.gestor_mz)
        response = self.client.patch('/gestoreduka/api/react/financeiro/', data=json.dumps({'moeda_cobranca': 'MZN'}), content_type='application/json')

        self.assertEqual(response.status_code, 200, response.content.decode())
        configuracao = ConfiguracaoFinanceiraCentro.objects.get(centro=self.centro_mz)
        self.assertEqual(configuracao.moeda_cobranca, 'MZN')
        self.assertEqual(configuracao.estado, 'PENDENTE_VALIDACAO')
        self.assertIsNone(configuracao.validado_por)

    def test_gestor_nao_pode_escolher_moeda_de_outro_mercado(self):
        self.client.force_login(self.gestor_mz)
        response = self.client.patch('/gestoreduka/api/react/financeiro/', data=json.dumps({'moeda_cobranca': 'EUR'}), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(ConfiguracaoFinanceiraCentro.objects.filter(centro=self.centro_mz).exists())

    def test_configuracao_financeira_e_isolada_por_centro(self):
        ConfiguracaoFinanceiraCentro.objects.create(centro=self.centro_ao, moeda_apresentacao='AOA', moeda_cobranca='AOA', gateway='PRONTU')
        self.client.force_login(self.gestor_mz)
        response = self.client.patch('/gestoreduka/api/react/financeiro/', data=json.dumps({'moeda_cobranca': 'MZN'}), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ConfiguracaoFinanceiraCentro.objects.get(centro=self.centro_ao).moeda_cobranca, 'AOA')
        self.assertEqual(ConfiguracaoFinanceiraCentro.objects.get(centro=self.centro_mz).moeda_cobranca, 'MZN')

    def test_moeda_internacional_nao_pode_ser_activada_sem_gateway_validado(self):
        configuracao = ConfiguracaoFinanceiraCentro(
            centro=self.centro_mz,
            moeda_apresentacao='MZN',
            moeda_cobranca='MZN',
            gateway='PRONTU',
            estado='ACTIVA',
        )

        with self.assertRaises(ValidationError):
            configuracao.full_clean()

    def test_endpoint_exige_sessao_de_gestor(self):
        self.assertEqual(self.client.get('/gestoreduka/api/react/financeiro/').status_code, 302)
