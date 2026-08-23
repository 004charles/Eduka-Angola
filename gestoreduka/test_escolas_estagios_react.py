from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from escolas.models import Escola, PerfilEscola
from estagio.models import AreaEstagio, Estagio, InscricaoEstagio
from usuarios.models import Aluno, Usuario

from .models import CentroDeFormacao, ModuloPublico


class EscolasEEstagiosReactTests(TestCase):
    def setUp(self):
        ModuloPublico.objects.update_or_create(chave='ESCOLAS', defaults={'ativo': True, 'ordem': 110})
        ModuloPublico.objects.update_or_create(chave='ESTAGIOS', defaults={'ativo': True, 'ordem': 120})
        gestor = Usuario.objects.create_user(email='gestor.oportunidades@test.com', nome='Gestor Oportunidades', password='SenhaSegura123', tipo_usuario='GESTOR')
        self.centro = CentroDeFormacao.objects.create(usuario=gestor, nome='Centro Oportunidades', email=gestor.email, ativo=True)
        self.escola = Escola.objects.create(nome='Escola React', provincia='Luanda', municipio='Talatona', tipo_rede='PRIVADA')
        PerfilEscola.objects.create(escola=self.escola, descricao='Escola para validar a página React.', inscricoes_abertas=True)
        area = AreaEstagio.objects.create(nome='Tecnologia', slug='tecnologia')
        hoje = timezone.localdate()
        self.estagio = Estagio.objects.create(titulo='Estágio React', descricao='Descrição completa de um estágio para cobertura da nova página React.', resumo='Oportunidade de tecnologia', centro_formacao=self.centro, area=area, local_trabalho='Talatona', cidade='Luanda', provincia='Luanda', requisitos='Conhecimentos básicos de informática.', data_inicio=hoje + timedelta(days=30), data_limite_inscricao=hoje + timedelta(days=15), vagas_disponiveis=2)

    def test_catalogos_react_respeitam_modulos_ativos(self):
        escolas = self.client.get('/api/react/escolas/')
        estagios = self.client.get('/api/react/estagios/')

        self.assertEqual(escolas.status_code, 200)
        self.assertEqual(escolas.json()['escolas'][0]['nome'], 'Escola React')
        self.assertEqual(estagios.status_code, 200)
        self.assertEqual(estagios.json()['estagios'][0]['slug'], self.estagio.slug)

    def test_candidatura_de_estagio_e_isolada_por_aluno(self):
        utilizador = Usuario.objects.create_user(email='aluno.estagio@test.com', nome='Aluno Estágio', password='SenhaSegura123', tipo_usuario='ALUNO')
        aluno = Aluno.objects.create(usuario=utilizador, nome=utilizador.nome)
        self.client.force_login(utilizador)

        resposta = self.client.post(f'/api/react/estagios/{self.estagio.slug}/candidaturas/', {'carta_motivacao': 'Quero aprender na prática e desenvolver competências profissionais na área de tecnologia.'})
        repetida = self.client.post(f'/api/react/estagios/{self.estagio.slug}/candidaturas/', {'carta_motivacao': 'Quero aprender na prática e desenvolver competências profissionais na área de tecnologia.'})

        self.assertEqual(resposta.status_code, 201, resposta.content.decode())
        self.assertEqual(repetida.status_code, 409)
        self.assertEqual(InscricaoEstagio.objects.get(aluno=aluno).estagio, self.estagio)

    def test_rotas_html_de_detalhe_redirecionam_para_react(self):
        escola = self.client.get(f'/escolas/perfil/{self.escola.id}/')
        estagio = self.client.get(f'/estagio/{self.estagio.slug}/')

        self.assertEqual(escola['Location'], f'/escolas/{self.escola.id}')
        self.assertEqual(estagio['Location'], f'/estagios/{self.estagio.slug}')
