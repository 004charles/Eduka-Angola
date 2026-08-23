import json

from django.test import TestCase

from core.models import AdminAuditLog, MensagemContato
from pagamentos.models import Pagamento
from usuarios.models import Usuario


class ReactAdminOperationsTests(TestCase):
    def setUp(self):
        self.staff = Usuario.objects.create_superuser(
            email='operador.admin@teste.com',
            nome='Operador Admin',
            password='SenhaAdminSegura123',
        )
        self.common = Usuario.objects.create_user(
            email='utilizador@teste.com',
            nome='Utilizador Comum',
            password='SenhaUtilizador123',
        )

    def test_operacoes_exigem_conta_administrativa(self):
        endpoint = '/api/react/administracao/operacoes/utilizadores/'
        self.assertEqual(self.client.get(endpoint).status_code, 401)
        self.client.force_login(self.common)
        self.assertEqual(self.client.get(endpoint).status_code, 403)

    def test_staff_lista_e_actualiza_utilizador_com_auditoria(self):
        self.client.force_login(self.staff)
        endpoint = '/api/react/administracao/operacoes/utilizadores/'
        lista = self.client.get(endpoint)
        actualizacao = self.client.post(endpoint, data=json.dumps({
            'id': str(self.common.pk),
            'field': 'is_active',
            'value': False,
        }), content_type='application/json')

        self.assertEqual(lista.status_code, 200)
        self.assertEqual(actualizacao.status_code, 200)
        self.common.refresh_from_db()
        self.assertFalse(self.common.is_active)
        auditoria = AdminAuditLog.objects.get(recurso='utilizadores', objeto_id=str(self.common.pk))
        self.assertEqual(auditoria.ator, self.staff)
        self.assertEqual(auditoria.antes, {'is_active': True})
        self.assertEqual(auditoria.depois, {'is_active': False})

    def test_staff_controla_contactos_sem_expor_acoes_desconhecidas(self):
        contacto = MensagemContato.objects.create(nome='Ana', email='ana@teste.com', assunto='Ajuda', mensagem='Preciso de apoio.')
        self.client.force_login(self.staff)
        endpoint = '/api/react/administracao/operacoes/contactos/'
        resposta = self.client.post(endpoint, data=json.dumps({
            'id': str(contacto.pk), 'field': 'lido', 'value': True,
        }), content_type='application/json')
        invalida = self.client.post(endpoint, data=json.dumps({
            'id': str(contacto.pk), 'field': 'email', 'value': 'alterado@teste.com',
        }), content_type='application/json')

        contacto.refresh_from_db()
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(contacto.lido)
        self.assertEqual(invalida.status_code, 400)

    def test_staff_pode_reconciliar_pagamento_com_auditoria(self):
        pagamento = Pagamento.objects.create(
            usuario=self.common,
            tipo_pagamento='OUTRO',
            moeda='AOA',
            valor='2500.00',
            valor_final='2500.00',
            gateway='PRONTU',
            status='PENDING',
        )
        self.client.force_login(self.staff)
        resposta = self.client.post('/api/react/administracao/operacoes/pagamentos/', data=json.dumps({
            'id': str(pagamento.pk), 'field': 'status', 'value': 'ACCEPTED',
        }), content_type='application/json')

        pagamento.refresh_from_db()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(pagamento.status, 'ACCEPTED')
        self.assertIsNotNone(pagamento.data_pagamento)
        self.assertTrue(AdminAuditLog.objects.filter(recurso='pagamentos', objeto_id=str(pagamento.pk)).exists())

    def test_staff_controla_configuracao_de_pagamentos_sem_expor_segredos(self):
        self.client.force_login(self.staff)
        endpoint = '/api/react/administracao/operacoes/configuracoes/'
        consulta = self.client.get(endpoint)
        actualizacao = self.client.post(endpoint, data=json.dumps({
            'id': 'pagamento', 'field': 'pagamentos_ativados', 'value': False,
        }), content_type='application/json')

        self.assertEqual(consulta.status_code, 200)
        self.assertEqual(actualizacao.status_code, 200)
        self.assertEqual(actualizacao.json()['item']['id'], 'pagamento')
        self.assertTrue(AdminAuditLog.objects.filter(recurso='configuracoes', acao='actualizar_pagamentos_ativados').exists())
