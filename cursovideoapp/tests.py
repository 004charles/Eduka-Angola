import json
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.utils import timezone
from django.core import mail

from cursos_app.models import Categoria
from cursovideoapp.models import AssinaturaVideoAluno, AvisoExpiracaoSubscricaoVideo, Curso_video, PlanoSubscricaoVideo
from cursovideoapp.subscription_notifications import processar_avisos_expiracao_subscricao_video
from pagamentos.models import Pagamento
from pagamentos.services import get_payment_service
from usuarios.models import Aluno, NotificacaoAluno, PreferenciaNotificacaoAluno, Usuario


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

    @override_settings(BREVO_API_KEY='')
    def test_aviso_de_sete_dias_cria_notificacao_email_e_nao_duplica(self):
        agora = timezone.now()
        assinatura = AssinaturaVideoAluno.objects.create(
            aluno=self.aluno,
            plano=self.plano,
            status='ATIVA',
            data_inicio=agora - timedelta(days=23),
            data_fim=agora + timedelta(days=6, hours=23),
            valor_cobrado=self.plano.preco,
        )

        primeiro = processar_avisos_expiracao_subscricao_video(agora)
        segundo = processar_avisos_expiracao_subscricao_video(agora)

        self.assertEqual(primeiro['avisos_criados'], 1)
        self.assertEqual(primeiro['notificacoes_plataforma'], 1)
        self.assertEqual(primeiro['emails_enviados'], 1)
        self.assertEqual(segundo['avisos_criados'], 0)
        self.assertEqual(AvisoExpiracaoSubscricaoVideo.objects.filter(assinatura=assinatura, antecedencia_horas=168).count(), 1)
        self.assertEqual(NotificacaoAluno.objects.filter(aluno=self.aluno, tipo='APRENDIZAGEM').count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('7 dias', mail.outbox[0].subject)

    def test_aviso_respeita_preferencias_de_email_e_plataforma(self):
        agora = timezone.now()
        PreferenciaNotificacaoAluno.objects.update_or_create(
            aluno=self.aluno,
            defaults={'receber_na_plataforma': False, 'receber_por_email': False, 'atualizacoes_aprendizagem': False},
        )
        assinatura = AssinaturaVideoAluno.objects.create(
            aluno=self.aluno,
            plano=self.plano,
            status='ATIVA',
            data_inicio=agora - timedelta(days=28),
            data_fim=agora + timedelta(hours=20),
            valor_cobrado=self.plano.preco,
        )

        resultado = processar_avisos_expiracao_subscricao_video(agora)
        aviso = AvisoExpiracaoSubscricaoVideo.objects.get(assinatura=assinatura, antecedencia_horas=24)

        self.assertEqual(resultado['notificacoes_plataforma'], 0)
        self.assertEqual(resultado['emails_enviados'], 0)
        self.assertIsNone(aviso.notificacao)
        self.assertIsNotNone(aviso.email_processado_em)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(BREVO_API_KEY='')
    def test_aviso_de_tres_dias_usa_a_janela_correcta(self):
        agora = timezone.now()
        assinatura = AssinaturaVideoAluno.objects.create(
            aluno=self.aluno,
            plano=self.plano,
            status='ATIVA',
            data_inicio=agora - timedelta(days=27),
            data_fim=agora + timedelta(days=2, hours=23),
            valor_cobrado=self.plano.preco,
        )

        resultado = processar_avisos_expiracao_subscricao_video(agora)

        self.assertEqual(resultado['avisos_criados'], 1)
        self.assertTrue(AvisoExpiracaoSubscricaoVideo.objects.filter(assinatura=assinatura, antecedencia_horas=72).exists())
        self.assertIn('3 dias', mail.outbox[0].subject)
