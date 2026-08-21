import json
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from cursos_app.models import Categoria
from cursovideoapp.models import AssinaturaVideoAluno, Curso_video, PlanoSubscricaoVideo
from pagamentos.models import Pagamento
from pagamentos.services import get_payment_service
from usuarios.models import Aluno, Usuario


class SubscricaoVideoTest(TestCase):
    def setUp(self):
        categoria = Categoria.objects.create(nome='Vídeo Subscrição', slug='video-subscricao')
        self.curso = Curso_video.objects.create(titulo='Curso de vídeo A', descricao='Curso abrangido pela subscrição.', categoria=categoria)
        self.outro_curso = Curso_video.objects.create(titulo='Curso de vídeo B', descricao='Outro curso abrangido pela subscrição.', categoria=categoria)
        self.plano = PlanoSubscricaoVideo.objects.create(
            nome='Mensal Edukangola Vídeo',
            descricao='Acesso a todo o catálogo de cursos em vídeo.',
            preco=Decimal('3500.00'),
            periodo_dias=30,
            ativo=True,
            destaque=True,
        )
        self.user = Usuario.objects.create_user(email='assinante.video@test.com', nome='Aluno Assinante', password='SenhaSegura123', tipo_usuario='ALUNO')
        self.aluno = Aluno.objects.create(usuario=self.user, nome=self.user.nome)

    def test_catalogo_exige_sessao_de_aluno_para_iniciar_subscricao(self):
        response = self.client.post(
            f'/curso_video/api/react/{self.curso.slug}/acesso/',
            data=json.dumps({}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 401)

    def test_aluno_obtem_no_checkout_o_plano_activo_definido_no_admin(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f'/curso_video/api/react/{self.curso.slug}/acesso/',
            data=json.dumps({'plano_id': self.plano.id}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['status'], 'pendente')
        self.assertEqual(payload['plano']['id'], self.plano.id)
        self.assertEqual(payload['valor_agora'], float(self.plano.preco))

    def test_assinatura_ativa_da_acesso_a_todo_catalogo(self):
        agora = timezone.now()
        AssinaturaVideoAluno.objects.create(
            aluno=self.aluno,
            plano=self.plano,
            status='ATIVA',
            data_inicio=agora - timedelta(minutes=1),
            data_fim=agora + timedelta(days=29),
            valor_cobrado=self.plano.preco,
        )
        self.assertTrue(self.curso.aluno_tem_acesso(self.aluno))
        self.assertTrue(self.outro_curso.aluno_tem_acesso(self.aluno))

        self.client.force_login(self.user)
        response = self.client.get(f'/api/react/video-cursos/{self.outro_curso.slug}/sala/')
        self.assertEqual(response.status_code, 200)

    def test_assinatura_expirada_bloqueia_acesso(self):
        agora = timezone.now()
        AssinaturaVideoAluno.objects.create(
            aluno=self.aluno,
            plano=self.plano,
            status='ATIVA',
            data_inicio=agora - timedelta(days=31),
            data_fim=agora - timedelta(seconds=1),
            valor_cobrado=self.plano.preco,
        )
        self.assertFalse(self.curso.aluno_tem_acesso(self.aluno))

    def test_pagamento_aceite_activa_subscricao_e_nao_duplica_periodo(self):
        agora = timezone.now()
        assinatura = AssinaturaVideoAluno.objects.create(
            aluno=self.aluno,
            plano=self.plano,
            status='PENDENTE',
            data_inicio=agora,
            data_fim=agora,
            valor_cobrado=self.plano.preco,
        )
        pagamento = Pagamento.objects.create(
            usuario=self.user,
            referencia_pagamento='SUB-VIDEO-TESTE-001',
            tipo_pagamento='ASSINATURA_VIDEO',
            valor=self.plano.preco,
            valor_final=self.plano.preco,
            moeda='AOA',
            gateway='PRONTU',
            status='ACCEPTED',
            metadados={'assinatura_video_id': assinatura.id},
        )

        get_payment_service()._processar_pagamento_aceito(pagamento)
        assinatura.refresh_from_db()
        self.assertEqual(assinatura.status, 'ATIVA')
        self.assertEqual(assinatura.referencia_pagamento, pagamento.referencia_pagamento)
        fim_original = assinatura.data_fim
        self.assertTrue(self.curso.aluno_tem_acesso(self.aluno))

        get_payment_service()._processar_pagamento_aceito(pagamento)
        assinatura.refresh_from_db()
        self.assertEqual(assinatura.data_fim, fim_original)

    def test_renovacao_com_pagamento_aceite_comeca_no_fim_da_subscricao_actual(self):
        agora = timezone.now()
        actual = AssinaturaVideoAluno.objects.create(
            aluno=self.aluno,
            plano=self.plano,
            status='ATIVA',
            data_inicio=agora - timedelta(days=20),
            data_fim=agora + timedelta(days=10),
            valor_cobrado=self.plano.preco,
        )
        renovacao = AssinaturaVideoAluno.objects.create(
            aluno=self.aluno,
            plano=self.plano,
            status='PENDENTE',
            data_inicio=agora,
            data_fim=agora,
            valor_cobrado=self.plano.preco,
        )
        pagamento = Pagamento.objects.create(
            usuario=self.user,
            referencia_pagamento='SUB-VIDEO-TESTE-RENOVAR',
            tipo_pagamento='ASSINATURA_VIDEO',
            valor=self.plano.preco,
            valor_final=self.plano.preco,
            moeda='AOA',
            gateway='PRONTU',
            status='ACCEPTED',
            metadados={'assinatura_video_id': renovacao.id},
        )

        get_payment_service()._processar_pagamento_aceito(pagamento)
        renovacao.refresh_from_db()
        self.assertEqual(renovacao.data_inicio, actual.data_fim)
        self.assertEqual(renovacao.data_fim, actual.data_fim + timedelta(days=self.plano.periodo_dias))
