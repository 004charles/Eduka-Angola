from django.test import TestCase
import json
from datetime import date, time, timedelta

from django.test import TestCase

from cursos_app.models import Categoria, Curso, Inscricao, Turma
from gestoreduka.models import CentroDeFormacao
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
