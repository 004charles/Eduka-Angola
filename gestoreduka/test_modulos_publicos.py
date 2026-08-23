import json

from django.test import TestCase

from bolsas.models import CandidaturaBolsa
from cursos_app.models import Categoria, Curso
from usuarios.models import Aluno, Usuario
from .models import CentroDeFormacao, ModuloPublico


class ModulosPublicosTests(TestCase):
    def setUp(self):
        self.modulo, _ = ModuloPublico.objects.get_or_create(chave='BOLSAS')

    def test_modulo_desactivado_nao_aparece_no_menu_nem_expoe_bolsas(self):
        self.modulo.ativo = False
        self.modulo.save()

        menu = self.client.get('/api/public/modulos/')
        bolsas = self.client.get('/api/react/bolsas/')

        self.assertEqual(menu.status_code, 200)
        self.assertEqual(menu.json()['modulos'], [])
        self.assertEqual(bolsas.status_code, 404)

    def test_modulo_activado_expoe_metadados_e_pagina_bolsas(self):
        self.modulo.ativo = True
        self.modulo.save()

        menu = self.client.get('/api/public/modulos/')
        bolsas = self.client.get('/api/react/bolsas/')

        self.assertEqual(menu.status_code, 200)
        self.assertEqual(menu.json()['modulos'][0]['rota'], '/bolsas')
        self.assertEqual(bolsas.status_code, 200)
        self.assertIn('cursos', bolsas.json())

    def test_candidatura_exige_sessao_de_aluno(self):
        self.modulo.ativo = True
        self.modulo.save()

        response = self.client.post('/api/react/bolsas/', data=json.dumps({'curso_pretendido': 1}), content_type='application/json')

        self.assertEqual(response.status_code, 401)

    def test_aluno_envia_candidatura_pela_api_react(self):
        self.modulo.ativo = True
        self.modulo.save()
        utilizador = Usuario.objects.create_user(email='bolsa.aluno@test.com', nome='Aluno Bolsa', password='SenhaSegura123', tipo_usuario='ALUNO')
        aluno = Aluno.objects.create(usuario=utilizador, nome=utilizador.nome)
        gestor = Usuario.objects.create_user(email='bolsa.centro@test.com', nome='Gestor Bolsa', password='SenhaSegura123', tipo_usuario='GESTOR')
        centro = CentroDeFormacao.objects.create(usuario=gestor, nome='Centro para Bolsa', email=gestor.email)
        categoria = Categoria.objects.create(nome='Categoria Bolsas', slug='categoria-bolsas')
        curso = Curso.objects.create(centro=centro, titulo='Curso para Bolsa', descricao='Curso utilizado para testar a candidatura React a bolsas.', categoria=categoria, carga_horaria=12, preco=1000, publicado=True, ativo=True)
        self.client.force_login(utilizador)

        response = self.client.post('/api/react/bolsas/', data={
            'curso_pretendido': curso.id,
            'justificativa': 'Preciso de apoio para concluir uma formação que melhore as minhas oportunidades profissionais.',
            'renda_familiar': '150000',
        })

        self.assertEqual(response.status_code, 201, response.content.decode())
        candidatura = CandidaturaBolsa.objects.get(aluno=aluno)
        self.assertEqual(candidatura.curso_pretendido, curso)
        self.assertEqual(candidatura.status, 'PENDENTE')
