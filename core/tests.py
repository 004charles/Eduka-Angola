from decimal import Decimal

from django.test import TestCase
from django.urls import resolve

from biblioteca.models import Autor, BibliotecaPessoal, Livro
from cursos_app.models import Categoria, Curso, Inscricao
from cursovideoapp.models import Curso_video
from gestoreduka.models import CentroDeFormacao
from mercado.models import PedidoMercado
from usuarios.models import Aluno, Usuario

from .models import Publicidade
from .react_delivery import react_application


class EducationalSponsorApiTest(TestCase):
    def test_prefixo_backend_reencaminha_a_api_no_mesmo_servico(self):
        response = self.client.get('/backend/api/public/home/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('cursos', response.json())

    def test_recarga_de_rota_publica_e_entregue_pela_spa_react(self):
        self.assertIs(resolve('/cursos/81/').func, react_application)

    def test_home_expoe_apenas_patronicios_com_destino_interno(self):
        Publicidade.objects.create(
            titulo='Bolsa Edukangola',
            subtitulo='Oportunidade educativa interna.',
            tag_label='Selecção Edukangola',
            posicao='GERAL',
            url_destino='/bolsas',
            ativo=True,
        )
        Publicidade.objects.create(
            titulo='Destino externo bloqueado',
            posicao='GERAL',
            url_destino='https://exemplo-publicidade.test/oferta',
            ativo=True,
        )

        response = self.client.get('/api/public/home/')
        self.assertEqual(response.status_code, 200)
        patrocinios = response.json()['patrocinios_educativos']
        self.assertEqual(len(patrocinios), 1)
        self.assertEqual(patrocinios[0]['titulo'], 'Bolsa Edukangola')
        self.assertEqual(patrocinios[0]['url'], '/bolsas')

    def test_home_expoe_inscricao_e_mensalidade_separadas_por_curso(self):
        response = self.client.get('/api/public/home/')

        self.assertEqual(response.status_code, 200)
        curso = next(item for item in response.json()['cursos'] if not item['is_gratuito'])
        financeiro = curso['financeiro']

        self.assertEqual(financeiro['preco_total'], curso['preco'])
        self.assertIn('formatado', financeiro['inscricao'])
        self.assertIn('valor', financeiro['inscricao'])
        self.assertIn('formatado', financeiro['mensalidade'])
        self.assertIn('valor', financeiro['mensalidade'])


class StudentDashboardVideoRouteTest(TestCase):
    def test_dashboard_serializa_curso_em_video_na_rota_react_mesmo_com_slug_unicode(self):
        user = Usuario.objects.create_user(
            email='aluno.dashboard@test.com',
            nome='Aluno do Painel',
            password='SenhaSegura123',
            tipo_usuario='ALUNO',
        )
        aluno = Aluno.objects.create(usuario=user, nome='Aluno do Painel')
        categoria = Categoria.objects.create(nome='Tecnologia', slug='tecnologia-dashboard')
        video = Curso_video.objects.create(
            titulo='Comunicação Digital Profissional',
            descricao='Curso de demonstração.',
            categoria=categoria,
            slug='comunicação-digital-profissional',
        )
        video.inscritos.add(aluno)

        self.client.force_login(user)
        response = self.client.get('/api/react/aluno/dashboard/')

        self.assertEqual(response.status_code, 200)
        curso = response.json()['continuar_aprender'][0]
        self.assertEqual(curso['detalhe_url'], '/video-cursos/comunicação-digital-profissional')
        self.assertEqual(curso['aprendizagem_url'], '/aprender/video/comunicação-digital-profissional')


class StudentHistoryApiTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='historico.aluno@test.com', nome='Aluno Histórico', password='SenhaSegura123', tipo_usuario='ALUNO')
        self.aluno = Aluno.objects.create(usuario=self.user, nome='Aluno Histórico')
        self.other_user = Usuario.objects.create_user(email='historico.outro@test.com', nome='Outro Aluno', password='SenhaSegura123', tipo_usuario='ALUNO')
        self.other_aluno = Aluno.objects.create(usuario=self.other_user, nome='Outro Aluno')
        self.categoria = Categoria.objects.create(nome='Histórico Tecnologia', slug='historico-tecnologia')
        self.centro = CentroDeFormacao.objects.create(nome='Centro Histórico', email='centro.historico@test.com')
        self.curso = Curso.objects.create(centro=self.centro, titulo='Fundamentos para o Histórico', descricao='Curso para cobertura da cronologia.', categoria=self.categoria, carga_horaria=16)

    def test_historico_exige_sessao_de_aluno(self):
        response = self.client.get('/api/react/aluno/historico/')

        self.assertEqual(response.status_code, 401)

    def test_historico_agrega_apenas_registos_da_propria_conta(self):
        inscricao = Inscricao.objects.create(aluno=self.aluno, curso=self.curso, status='A', valor_pago=Decimal('5000'))
        pedido = PedidoMercado.objects.create(utilizador=self.user, nome_comprador='Aluno Histórico', email_comprador=self.user.email, telefone_comprador='900000000', endereco_entrega='Rua da História', bairro='Kilamba', total=Decimal('12000'))
        PedidoMercado.objects.create(utilizador=self.other_user, nome_comprador='Outro Aluno', email_comprador=self.other_user.email, telefone_comprador='911111111', endereco_entrega='Rua Privada', bairro='Zango', total=Decimal('9000'))
        autor = Autor.objects.create(nome='Autor do Histórico')
        livro = Livro.objects.create(titulo='Leitura de Histórico', autor=autor, sinopse='Obra de teste.', categoria='Tecnologia', estado='PUBLICADO')
        BibliotecaPessoal.objects.create(usuario=self.user, livro=livro, progresso_leitura=42)

        self.client.force_login(self.user)
        response = self.client.get('/api/react/aluno/historico/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload['ok'])
        self.assertEqual(payload['resumo']['pedidos_mercado'], 1)
        self.assertEqual(payload['resumo']['inscricoes'], 1)
        self.assertEqual(payload['resumo']['leituras'], 1)
        record_ids = {item['id'] for item in payload['registos']}
        self.assertIn(f'inscricao-{inscricao.id}', record_ids)
        self.assertIn(f'mercado-{pedido.id}', record_ids)
        self.assertIn(f'leitura-{livro.presencas_biblioteca.get(usuario=self.user).id}', record_ids)
        self.assertNotIn('Rua Privada', str(payload))
        self.assertEqual([item['ocorrido_em'] for item in payload['registos']], sorted((item['ocorrido_em'] for item in payload['registos']), reverse=True))

    def test_rota_do_historico_e_entregue_pela_spa_react(self):
        self.assertIs(resolve('/aluno/historico').func, react_application)
