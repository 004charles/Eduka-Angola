from django.core import mail
from django.test import TestCase, override_settings
import json
from datetime import date, time, timedelta
from unittest.mock import patch

from cursos_app.models import Categoria, Curso, Inscricao, Turma
from gestoreduka.models import CentroDeFormacao
from gestoreduka.models import Filial
from usuarios.models import Aluno, Usuario


class ReactCheckoutPresencialTest(TestCase):
    def setUp(self):
        gestor = Usuario.objects.create_user(
            email='gestor.checkout@test.com', nome='Gestor Checkout', password='SenhaSegura123', tipo_usuario='GESTOR'
        )
        centro = CentroDeFormacao.objects.create(usuario=gestor, nome='Centro Checkout', email=gestor.email)
        categoria = Categoria.objects.create(nome='Categoria Checkout', slug='categoria-checkout')
        self.curso = Curso.objects.create(
            centro=centro,
            titulo='Formação Checkout',
            descricao='Curso para validar a inscrição pública.',
            categoria=categoria,
            carga_horaria=12,
            preco=25000,
            preco_inscricao=2500,
            tipo_cobranca_inscricao='APENAS_TAXA',
            publicado=True,
            ativo=True,
        )
        self.turma = Turma.objects.create(
            curso=self.curso,
            nome='Turma React',
            codigo='RCT-001',
            data_inicio=date.today() + timedelta(days=14),
            data_fim=date.today() + timedelta(days=35),
            turno='MANHA',
            horario_inicio=time(8, 0),
            horario_fim=time(12, 0),
            dias_semana='SEG,QUA,SEX',
            vagas_totais=20,
            vagas_disponiveis=20,
            local='Luanda',
            status='ABERTA',
        )
        self.filial = Filial.objects.create(
            centro_principal=centro,
            nome='Unidade Zango',
            endereco='Zango III, primeira paragem',
            telefone='+244 923 000 000',
            email='zango.checkout@test.com',
            ativo=True,
        )
        self.turma.filial = self.filial
        self.turma.local = self.filial.endereco
        self.turma.save(update_fields=['filial', 'local'])

    def test_visitante_inicia_inscricao_com_dados_minimos_e_turma(self):
        response = self.client.post(
            f'/cursos/api/react/checkout/{self.curso.id}/',
            data=json.dumps({
                'nome': 'Visitante Checkout',
                'email': 'visitante.checkout.unico@test.com',
                'telefone': '+244 923 000 000',
                'turma_id': self.turma.id,
            }),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201, response.content.decode())
        data = response.json()
        self.assertTrue(data['ok'])
        self.assertEqual(data['status'], 'pendente')
        self.assertTrue(data['requires_payment'])
        self.assertEqual(data['valor_agora'], 2500.0)
        inscricao = Inscricao.objects.get(id=data['inscricao_id'])
        self.assertEqual(inscricao.turma_escolhida, self.turma)
        self.assertEqual(self.client.session['guest_inscricao_id'], inscricao.id)
        self.assertEqual(data['turma']['filial_nome'], 'Unidade Zango')
        self.assertEqual(data['turma']['filial_endereco'], 'Zango III, primeira paragem')

    def test_aluno_autenticado_com_inscricao_antiga_sem_turma_avanca_ao_resumo(self):
        utilizador = Usuario.objects.create_user(
            email='aluno.checkout@test.com', nome='Aluno Checkout', password='SenhaSegura123', tipo_usuario='ALUNO'
        )
        aluno = Aluno.objects.create(usuario=utilizador, nome=utilizador.nome)
        inscricao = Inscricao.objects.create(aluno=aluno, curso=self.curso, status='P', tipo_inscricao='ONLINE')
        self.client.force_login(utilizador)

        response = self.client.post(
            f'/cursos/api/react/checkout/{self.curso.id}/',
            data=json.dumps({
                'nome': utilizador.nome,
                'email': utilizador.email,
                'telefone': '+244 923 000 000',
                'turma_id': self.turma.id,
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200, response.content.decode())
        inscricao.refresh_from_db()
        self.assertEqual(inscricao.turma_escolhida, self.turma)
        self.assertEqual(response.json()['turma']['id'], self.turma.id)

    @override_settings(BREVO_API_KEY='')
    def test_comprovativo_confirmado_e_enviado_uma_unica_vez_com_a_filial(self):
        utilizador = Usuario.objects.create_user(
            email='aluno.comprovativo@test.com', nome='Aluno Comprovativo', password='SenhaSegura123', tipo_usuario='ALUNO'
        )
        aluno = Aluno.objects.create(usuario=utilizador, nome=utilizador.nome)
        inscricao = Inscricao.objects.create(
            aluno=aluno,
            curso=self.curso,
            turma_escolhida=self.turma,
            status='A',
            tipo_inscricao='ONLINE',
            forma_pagamento='CARTAO_CREDITO',
            valor_pago=2500,
        )

        self.assertTrue(inscricao.enviar_comprovativo_inscricao())
        inscricao.refresh_from_db()
        self.assertIsNotNone(inscricao.comprovativo_enviado_em)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Comprovativo de inscrição confirmado', mail.outbox[0].subject)
        self.assertIn('Unidade Zango', mail.outbox[0].alternatives[0][0])
        self.assertIn('Zango III, primeira paragem', mail.outbox[0].alternatives[0][0])
        self.assertIn(inscricao.codigo_inscricao, mail.outbox[0].alternatives[0][0])

        self.assertFalse(inscricao.enviar_comprovativo_inscricao())
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(BREVO_API_KEY='chave-de-teste')
    @patch('core.email_utils.enviar_email_brevo', return_value=True)
    def test_comprovativo_confirmado_usa_brevo_quando_configurado(self, email_brevo):
        utilizador = Usuario.objects.create_user(
            email='aluno.brevo@test.com', nome='Aluno Brevo', password='SenhaSegura123', tipo_usuario='ALUNO'
        )
        aluno = Aluno.objects.create(usuario=utilizador, nome=utilizador.nome)
        inscricao = Inscricao.objects.create(
            aluno=aluno,
            curso=self.curso,
            turma_escolhida=self.turma,
            status='A',
            tipo_inscricao='ONLINE',
            valor_pago=2500,
        )

        self.assertTrue(inscricao.enviar_comprovativo_inscricao())
        inscricao.refresh_from_db()
        self.assertIsNotNone(inscricao.comprovativo_enviado_em)
        email_brevo.assert_called_once()
        self.assertEqual(email_brevo.call_args.args[0], utilizador.email)
        self.assertIn(inscricao.codigo_inscricao, email_brevo.call_args.args[1])
