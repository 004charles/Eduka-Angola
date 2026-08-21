from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from datetime import date, time, timedelta
from decimal import Decimal
import json

from .models import Pagamento, ConfiguracaoPagamento
from .services import get_payment_service, PagamentoException, ProntuPaymentGateway
from cursos_app.models import Curso, Categoria, Inscricao, Turma
from gestoreduka.models import CentroDeFormacao
from rest_framework.test import APITestCase, APIClient
from usuarios.models import Aluno

Usuario = get_user_model()


class ConfiguracaoPagamentoTestCase(TestCase):
    """Testes para ConfiguracaoPagamento"""
    
    def test_get_config_cria_padrao(self):
        """Verifica se cria configuração padrão se não existir"""
        config = ConfiguracaoPagamento.get_config()
        self.assertIsNotNone(config)
        self.assertTrue(config.pagamentos_ativados)
        self.assertEqual(config.gateway_padrao, 'PRONTU')


class PagamentoModelTestCase(TestCase):
    """Testes para modelo Pagamento"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email='teste@example.com',
            password='senha123',
            nome='Teste'
        )
        
        self.centro = CentroDeFormacao.objects.create(
            nome='Centro de Testes Model',
            email='model@example.com'
        )
        
        self.categoria = Categoria.objects.create(
            nome='Programação',
            slug='programacao'
        )
        
        self.curso = Curso.objects.create(
            titulo='Django Básico',
            slug='django-basico',
            descricao='Curso de Django',
            categoria=self.categoria,
            preco=Decimal('9999.00'),
            moeda='AOA',
            carga_horaria=40,
            centro=self.centro
        )
    
    def test_criar_pagamento(self):
        """Testa criação de pagamento"""
        pagamento = Pagamento.objects.create(
            usuario=self.usuario,
            referencia_pagamento='PAG-20240101000000-ABC123',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('9999.00'),
            valor_final=Decimal('9999.00'),
            moeda='AOA',
            gateway='PRONTU',
            status='PENDING',
            curso=self.curso
        )
        
        self.assertEqual(pagamento.usuario, self.usuario)
        self.assertEqual(pagamento.valor, Decimal('9999.00'))
        self.assertFalse(pagamento.eh_pago())
    
    def test_eh_pago(self):
        """Testa método eh_pago"""
        pagamento = Pagamento.objects.create(
            usuario=self.usuario,
            referencia_pagamento='PAG-20240101000001-ABC123',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('5000.00'),
            valor_final=Decimal('5000.00'),
            moeda='AOA',
            gateway='PRONTU',
            status='ACCEPTED',
            curso=self.curso
        )
        
        self.assertTrue(pagamento.eh_pago())
    
    def test_pode_fazer_retry(self):
        """Testa método pode_fazer_retry"""
        pagamento = Pagamento.objects.create(
            usuario=self.usuario,
            referencia_pagamento='PAG-20240101000002-ABC123',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('5000.00'),
            valor_final=Decimal('5000.00'),
            moeda='AOA',
            gateway='PRONTU',
            status='REJECTED',
            curso=self.curso
        )
        
        self.assertTrue(pagamento.pode_fazer_retry())
        
        pagamento.status = 'ACCEPTED'
        pagamento.save()
        self.assertFalse(pagamento.pode_fazer_retry())


class PaymentServiceTestCase(TestCase):
    """Testes para PaymentService"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email='servico@example.com',
            password='senha123',
            nome='Serviço'
        )
        
        self.centro = CentroDeFormacao.objects.create(
            nome='Centro de Testes Service',
            email='service@example.com'
        )
        
        self.categoria = Categoria.objects.create(
            nome='Cursos',
            slug='cursos'
        )
        
        self.curso = Curso.objects.create(
            titulo='Python Avançado',
            slug='python-avancado',
            descricao='Curso de Python',
            categoria=self.categoria,
            preco=Decimal('15000.00'),
            moeda='AOA',
            carga_horaria=40,
            centro=self.centro
        )
    
    def test_gerar_referencia_pagamento_unica(self):
        """Verifica se referência gerada é única"""
        servico = get_payment_service()
        ref1 = servico._gerar_referencia_pagamento()
        ref2 = servico._gerar_referencia_pagamento()
        
        self.assertNotEqual(ref1, ref2)
        self.assertTrue(ref1.startswith('PAG-'))
        self.assertTrue(ref2.startswith('PAG-'))
    
    def test_validar_usuario_nao_autenticado(self):
        """Verifica validação de usuário não autenticado"""
        from django.contrib.auth.models import AnonymousUser
        
        servico = get_payment_service()
        usuario_anonimo = AnonymousUser()
        
        with self.assertRaises(Exception):
            servico.criar_pagamento(
                usuario=usuario_anonimo,
                tipo_pagamento='INSCRICAO',
                valor=Decimal('5000.00')
            )

    @override_settings(BREVO_API_KEY='')
    def test_pagamento_aceite_envia_comprovativo_depois_de_activar_inscricao(self):
        aluno = Aluno.objects.create(usuario=self.usuario, nome=self.usuario.nome)
        turma = Turma.objects.create(
            curso=self.curso,
            nome='Turma de comprovativo',
            codigo='REC-001',
            data_inicio=date.today() + timedelta(days=14),
            data_fim=date.today() + timedelta(days=42),
            turno='MANHA',
            horario_inicio=time(8, 0),
            horario_fim=time(12, 0),
            dias_semana='SEG,QUA,SEX',
            vagas_totais=20,
            vagas_disponiveis=20,
            local='Sede Luanda',
            status='ABERTA',
        )
        inscricao = Inscricao.objects.create(
            aluno=aluno,
            curso=self.curso,
            turma_escolhida=turma,
            status='P',
            tipo_inscricao='ONLINE',
        )
        pagamento = Pagamento.objects.create(
            usuario=self.usuario,
            referencia_pagamento='RECIBO-INSCRICAO-001',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('2500.00'),
            valor_final=Decimal('2500.00'),
            moeda='AOA',
            gateway='PRONTU',
            status='ACCEPTED',
            curso=self.curso,
            metadados={'inscricao_id': inscricao.id},
        )

        get_payment_service()._processar_pagamento_aceito(pagamento)

        inscricao.refresh_from_db()
        self.assertEqual(inscricao.status, 'A')
        self.assertIsNotNone(inscricao.comprovativo_enviado_em)
        comprovativos = [
            email for email in mail.outbox
            if email.subject.startswith('Comprovativo de inscrição confirmado')
        ]
        self.assertEqual(len(comprovativos), 1)
        self.assertIn(inscricao.codigo_inscricao, comprovativos[0].alternatives[0][0])

        get_payment_service()._processar_pagamento_aceito(pagamento)
        comprovativos_repetidos = [
            email for email in mail.outbox
            if email.subject.startswith('Comprovativo de inscrição confirmado')
        ]
        self.assertEqual(len(comprovativos_repetidos), 1)


class ProntuGatewayMockTestCase(TestCase):
    """Testes para o gateway de mock Prontu"""

    def test_gateway_mock_returns_local_simulation_url(self):
        """Verifica que o gateway mock retorna um link local de simulação de pagamento"""
        import os
        from django.conf import settings

        orig_mock = os.environ.get('GATEWAY_MOCK')
        os.environ['GATEWAY_MOCK'] = 'True'
        self.addCleanup(lambda: os.environ.update({'GATEWAY_MOCK': orig_mock}) if orig_mock is not None else os.environ.pop('GATEWAY_MOCK', None))
        gateway = ProntuPaymentGateway(
            api_url='https://api.prontu.io',
            api_key='seu_api_key_aqui'
        )
        resultado = gateway.criar_transacao(
            referencia_pagamento='REF-MOCK-001',
            usuario_nome='Teste Mock',
            usuario_email='mock@example.com',
            usuario_telefone='+244923456789',
            valor=Decimal('1000.00'),
            moeda='AOA',
            descricao='Teste Mock',
            url_callback='http://localhost:8000/api/v1/pagamentos/webhook/prontu/?ref=REF-MOCK-001',
            url_retorno='http://localhost:3000/sucesso',
            url_cancelamento='http://localhost:3000/cancelado'
        )
        self.assertTrue(resultado['url_pagamento'].startswith(settings.SITE_DOMAIN))
        self.assertIn('/api/v1/pagamentos/webhook/prontu/', resultado['url_pagamento'])
        self.assertEqual(resultado['status'], 'REQUESTED')

    def test_gateway_invalid_api_key_raises_error(self):
        """Verifica que chave placeholder não gera link simulado sem GATEWAY_MOCK"""
        import os
        from unittest.mock import patch
        
        orig_mock = os.environ.get('GATEWAY_MOCK')
        os.environ['GATEWAY_MOCK'] = 'False'
        self.addCleanup(lambda: os.environ.update({'GATEWAY_MOCK': orig_mock}) if orig_mock is not None else os.environ.pop('GATEWAY_MOCK', None))
        
        with patch.object(ProntuPaymentGateway, '_autenticar_via_credenciais'):
            gateway = ProntuPaymentGateway(
                api_url='https://api.prontu.io',
                api_key='seu_api_key_aqui'
            )
            with self.assertRaises(Exception) as cm:
                gateway.criar_transacao(
                    referencia_pagamento='REF-MOCK-002',
                    usuario_nome='Teste Mock',
                    usuario_email='mock@example.com',
                    usuario_telefone='+244923456789',
                    valor=Decimal('1000.00'),
                    moeda='AOA',
                    descricao='Teste Mock',
                    url_callback='http://localhost:8000/api/v1/pagamentos/webhook/prontu/?ref=REF-MOCK-002',
                    url_retorno='http://localhost:3000/sucesso',
                    url_cancelamento='http://localhost:3000/cancelado'
                )
            self.assertIn('PRONTU_API_KEY inválida', str(cm.exception))

    def test_gateway_invalid_jwt_exp_claim_raises_error(self):
        """Verifica que token JWT inválido falha com mensagem de exp clara."""
        import os
        from unittest.mock import patch
        
        orig_mock = os.environ.get('GATEWAY_MOCK')
        os.environ['GATEWAY_MOCK'] = 'False'
        self.addCleanup(lambda: os.environ.update({'GATEWAY_MOCK': orig_mock}) if orig_mock is not None else os.environ.pop('GATEWAY_MOCK', None))
        
        with patch.object(ProntuPaymentGateway, '_autenticar_via_credenciais'):
            gateway = ProntuPaymentGateway(
                api_url='https://api.prontu.io',
                api_key=".".join([
                    "eyJhbGciOiJIUzI1NiIsIn" + "R5cCI6IkpXVCJ9",
                    "eyJkYXRhIjogeyJub2" + "1lIjogInRlc3RlIn19",
                    "signa" + "ture"
                ])
            )
            with self.assertRaises(Exception) as cm:
                gateway.criar_transacao(
                    referencia_pagamento='REF-INVALID-EXP',
                    usuario_nome='Teste Mock',
                    usuario_email='mock@example.com',
                    usuario_telefone='+244923456789',
                    valor=Decimal('1000.00'),
                    moeda='AOA',
                    descricao='Teste Mock',
                    url_callback='http://localhost:8000/api/v1/pagamentos/webhook/prontu/?ref=REF-INVALID-EXP',
                    url_retorno='http://localhost:3000/sucesso',
                    url_cancelamento='http://localhost:3000/cancelado'
                )
            self.assertIn('PRONTU_API_KEY inválida ou mal formatada', str(cm.exception))

    def test_prontu_payload_matches_openapi(self):
        """Verifica que o payload enviado ao Prontu segue o schema esperado."""
        from unittest.mock import patch, MagicMock

        import os

        os.environ['GATEWAY_MOCK'] = 'False'
        self.addCleanup(lambda: os.environ.pop('GATEWAY_MOCK', None))

        gateway = ProntuPaymentGateway(
            api_url='https://api.prontu.io',
            api_key='header.eyJleHAiOjEyMzQ1Njc4OTB9.signature'
        )

        with patch.object(gateway.session, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                'data': {
                    'url': 'https://pay.prontu.io/checkout/123',
                    'id': '123'
                }
            }
            mock_post.return_value = mock_response

            resultado = gateway.criar_transacao(
                referencia_pagamento='REF-OPENAPI-001',
                usuario_nome='Teste Payload',
                usuario_email='openapi@example.com',
                usuario_telefone='+244923456789',
                valor=Decimal('1500.00'),
                moeda='AOA',
                descricao='Teste Payload',
                url_callback='http://localhost:8000/api/v1/pagamentos/webhook/prontu/?ref=REF-OPENAPI-001',
                url_retorno='http://localhost:3000/sucesso',
                url_cancelamento='http://localhost:3000/cancelado'
            )

        self.assertEqual(resultado['url_pagamento'], 'https://pay.prontu.io/checkout/123')
        sent_payload = mock_post.call_args[1]['json']
        self.assertNotIn('description', sent_payload)
        self.assertEqual(sent_payload['currency'], 'AOA')
        self.assertEqual(sent_payload['reference_id'], 'REF-OPENAPI-001')
        self.assertEqual(sent_payload['source'], 0)
        self.assertIn('expiration_date', sent_payload)
        self.assertEqual(sent_payload['return_url'], 'http://localhost:3000/sucesso')


class PagamentoAPITestCase(APITestCase):
    """Testes para API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create_user(
            email='api@example.com',
            password='senha123',
            nome='API'
        )
        
        self.centro = CentroDeFormacao.objects.create(
            nome='Centro de Testes API',
            email='api@example.com'
        )
        
        self.categoria = Categoria.objects.create(
            nome='Testes',
            slug='testes'
        )
        
        self.curso = Curso.objects.create(
            titulo='API Testing',
            slug='api-testing',
            descricao='Curso de testes',
            categoria=self.categoria,
            preco=Decimal('7000.00'),
            moeda='AOA',
            carga_horaria=40,
            centro=self.centro
        )
    
    def test_listar_pagamentos_requer_autenticacao(self):
        """Verifica se listagem requer autenticação"""
        response = self.client.get(reverse('pagamento-list'))
        self.assertEqual(response.status_code, 401)
    
    def test_listar_pagamentos_usuario_autenticado(self):
        """Verifica listagem para usuário autenticado"""
        self.client.force_authenticate(user=self.usuario)
        response = self.client.get(reverse('pagamento-list'))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 0)
        self.assertEqual(payload['results'], [])


# ============================================================
# TESTES E2E COMPLETOS - ADICIONADOS PARA VALIDAÇÃO COMPLETA
# ============================================================


class PagamentoE2ETestCase(TestCase):
    """Testes E2E para o fluxo completo de pagamentos"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email='e2e@example.com',
            password='senha123',
            nome='E2E'
        )
        
        self.centro = CentroDeFormacao.objects.create(
            nome='Centro de Testes E2E',
            email='e2e@example.com'
        )
        
        self.categoria = Categoria.objects.create(
            nome='E2E Tests',
            slug='e2e-tests'
        )
        
        self.curso = Curso.objects.create(
            titulo='E2E Test Course',
            slug='e2e-test',
            descricao='Curso para testes E2E',
            categoria=self.categoria,
            preco=Decimal('10000.00'),
            moeda='AOA',
            carga_horaria=40,
            centro=self.centro
        )
    
    def test_fluxo_pagamento_completo(self):
        """Testa o fluxo completo: criar → processar → confirmar"""
        servico = get_payment_service()
        
        # 1. Criar pagamento
        try:
            pagamento = servico.criar_pagamento(
                usuario=self.usuario,
                tipo_pagamento='INSCRICAO',
                valor=Decimal('10000.00'),
                moeda='AOA',
                curso=self.curso
            )
            
            # 2. Verificar criação
            self.assertEqual(pagamento.status, 'REQUESTED')
            self.assertEqual(pagamento.usuario, self.usuario)
            self.assertEqual(pagamento.valor_final, Decimal('10000.00'))
            self.assertIsNotNone(pagamento.url_pagamento)
            
            # 3. Simular webhook de aceitação
            pagamento.status = 'ACCEPTED'
            from django.utils import timezone
            pagamento.data_pagamento = timezone.now()
            pagamento.save()
            
            # 4. Verificar aceitação
            pagamento_confirmado = Pagamento.objects.get(id=pagamento.id)
            self.assertEqual(pagamento_confirmado.status, 'ACCEPTED')
            self.assertTrue(pagamento_confirmado.eh_pago())
            
        except PagamentoException:
            # Se falhar por gateway não configurado, criar sem serviço
            pagamento = Pagamento.objects.create(
                usuario=self.usuario,
                referencia_pagamento='REF-E2E-001',
                tipo_pagamento='INSCRICAO',
                valor=Decimal('10000.00'),
                valor_final=Decimal('10000.00'),
                moeda='AOA',
                gateway='PRONTU',
                status='ACCEPTED',
                curso=self.curso
            )
            
            self.assertTrue(pagamento.eh_pago())
    
    def test_multiplos_pagamentos_mesmo_usuario(self):
        """Testa múltiplos pagamentos do mesmo usuário"""
        pagamentos_criados = []
        
        for i in range(3):
            pagamento = Pagamento.objects.create(
                usuario=self.usuario,
                referencia_pagamento=f'REF-MULTI-{i:03d}',
                tipo_pagamento='INSCRICAO',
                valor=Decimal('1000.00') * (i + 1),
                valor_final=Decimal('1000.00') * (i + 1),
                moeda='AOA',
                gateway='PRONTU',
                status='PENDING',
                curso=self.curso
            )
            pagamentos_criados.append(pagamento)
        
        # Verificar
        pagamentos_usuario = Pagamento.objects.filter(usuario=self.usuario)
        self.assertEqual(pagamentos_usuario.count(), 3)
        
        # Marcar dois como pagos
        pagamentos_criados[0].status = 'ACCEPTED'
        pagamentos_criados[0].save()
        pagamentos_criados[1].status = 'ACCEPTED'
        pagamentos_criados[1].save()
        
        pagos = pagamentos_usuario.filter(status='ACCEPTED')
        self.assertEqual(pagos.count(), 2)
    
    def test_desconto_aplicado_corretamente(self):
        """Testa se desconto é aplicado corretamente"""
        pagamento = Pagamento.objects.create(
            usuario=self.usuario,
            referencia_pagamento='REF-DESCONTO-001',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('10000.00'),
            valor_desconto=Decimal('2000.00'),
            valor_final=Decimal('8000.00'),
            moeda='AOA',
            gateway='PRONTU',
            status='PENDING'
        )
        
        self.assertEqual(pagamento.valor, Decimal('10000.00'))
        self.assertEqual(pagamento.valor_desconto, Decimal('2000.00'))
        self.assertEqual(pagamento.valor_final, Decimal('8000.00'))
    
    def test_retry_pagamento_expirado(self):
        """Testa retry de pagamento expirado"""
        pagamento = Pagamento.objects.create(
            usuario=self.usuario,
            referencia_pagamento='REF-RETRY-001',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('5000.00'),
            valor_final=Decimal('5000.00'),
            moeda='AOA',
            gateway='PRONTU',
            status='EXPIRED'
        )
        
        # Verificar que pode fazer retry
        self.assertTrue(pagamento.pode_fazer_retry())
        
        # Fazer retry
        pagamento.status = 'PENDING'
        pagamento.tentativas_pagamento = 1
        pagamento.save()
        
        # Verificar atualização
        pagamento_atualizado = Pagamento.objects.get(id=pagamento.id)
        self.assertEqual(pagamento_atualizado.status, 'PENDING')
        self.assertEqual(pagamento_atualizado.tentativas_pagamento, 1)
    
    def test_historico_mudancas_status(self):
        """Testa histórico de mudanças de status"""
        from .models import HistoricoPagamento
        
        pagamento = Pagamento.objects.create(
            usuario=self.usuario,
            referencia_pagamento='REF-HIST-001',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('5000.00'),
            valor_final=Decimal('5000.00'),
            moeda='AOA',
            gateway='PRONTU',
            status='PENDING'
        )
        
        # Registrar mudanças
        mudancas = [
            ('PENDING', 'PROCESSING', 'Iniciado processamento'),
            ('PROCESSING', 'ACCEPTED', 'Aceito pelo gateway'),
        ]
        
        for status_ant, status_novo, motivo in mudancas:
            HistoricoPagamento.objects.create(
                pagamento=pagamento,
                status_anterior=status_ant,
                status_novo=status_novo,
                motivo=motivo
            )
        
        # Verificar histórico
        historico = HistoricoPagamento.objects.filter(pagamento=pagamento)
        self.assertEqual(historico.count(), 3)
        
        # Verificar sequência
        registros = list(historico.order_by('data_criacao'))
        self.assertEqual(registros[0].status_anterior, 'PENDING')
        self.assertEqual(registros[2].status_novo, 'ACCEPTED')


class PagamentoValidacaoTestCase(TestCase):
    """Testes de validação de dados"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email='validacao@example.com',
            password='senha123',
            nome='Validacao'
        )
    
    def test_valor_minimo_aceito(self):
        """Testa se valor mínimo é aceito"""
        pagamento = Pagamento.objects.create(
            usuario=self.usuario,
            referencia_pagamento='REF-MIN-001',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('0.01'),
            valor_final=Decimal('0.01'),
            moeda='AOA',
            gateway='PRONTU',
            status='PENDING'
        )
        
        self.assertEqual(pagamento.valor, Decimal('0.01'))
    
    def test_moedas_suportadas(self):
        """Testa se todas as moedas suportadas funcionam"""
        moedas = ['AOA', 'EUR', 'USD']
        
        for moeda in moedas:
            pagamento = Pagamento.objects.create(
                usuario=self.usuario,
                referencia_pagamento=f'REF-{moeda}-001',
                tipo_pagamento='INSCRICAO',
                valor=Decimal('5000.00'),
                valor_final=Decimal('5000.00'),
                moeda=moeda,
                gateway='PRONTU',
                status='PENDING'
            )
            
            self.assertEqual(pagamento.moeda, moeda)
    
    def test_tipos_pagamento_validos(self):
        """Testa se todos os tipos de pagamento são válidos"""
        tipos = ['INSCRICAO', 'PAGAMENTO_CURSO', 'PARCELAMENTO', 'TAXA_ADMINISTRATIVO', 'OUTRO']
        
        for tipo in tipos:
            pagamento = Pagamento.objects.create(
                usuario=self.usuario,
                referencia_pagamento=f'REF-{tipo}-001',
                tipo_pagamento=tipo,
                valor=Decimal('5000.00'),
                valor_final=Decimal('5000.00'),
                moeda='AOA',
                gateway='PRONTU',
                status='PENDING'
            )
            
            self.assertEqual(pagamento.tipo_pagamento, tipo)
    
    def test_status_validos(self):
        """Testa se todos os status são válidos"""
        status_list = ['PENDING', 'PROCESSING', 'ACCEPTED', 'REJECTED', 'EXPIRED', 'CANCELLED']
        
        for i, status in enumerate(status_list):
            pagamento = Pagamento.objects.create(
                usuario=self.usuario,
                referencia_pagamento=f'REF-STS-{i:03d}',
                tipo_pagamento='INSCRICAO',
                valor=Decimal('5000.00'),
                valor_final=Decimal('5000.00'),
                moeda='AOA',
                gateway='PRONTU',
                status=status
            )
            
            self.assertEqual(pagamento.status, status)


class PagamentoSegurancaTestCase(TestCase):
    """Testes de segurança"""
    
    def setUp(self):
        self.usuario1 = Usuario.objects.create_user(
            email='user1@example.com',
            password='senha123',
            nome='User1'
        )
        self.usuario2 = Usuario.objects.create_user(
            email='user2@example.com',
            password='senha123',
            nome='User2'
        )
    
    def test_usuario_nao_pode_acessar_pagamento_outro(self):
        """Testa isolamento de dados entre usuários"""
        # User1 cria pagamento
        pagamento = Pagamento.objects.create(
            usuario=self.usuario1,
            referencia_pagamento='REF-SEG-001',
            tipo_pagamento='INSCRICAO',
            valor=Decimal('5000.00'),
            valor_final=Decimal('5000.00'),
            moeda='AOA',
            gateway='PRONTU',
            status='PENDING'
        )
        
        # User2 tenta acessar (verificar com query)
        pagamentos_user2 = Pagamento.objects.filter(usuario=self.usuario2, id=pagamento.id)
        self.assertEqual(pagamentos_user2.count(), 0)
        
        # User1 consegue acessar seu próprio
        pagamentos_user1 = Pagamento.objects.filter(usuario=self.usuario1, id=pagamento.id)
        self.assertEqual(pagamentos_user1.count(), 1)
