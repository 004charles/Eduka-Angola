import json
from unittest.mock import patch

from django.test import TestCase

from cursos_app.models import Categoria
from cursovideoapp.models import Aula, Curso_video, ProgressoAula
from usuarios.models import Aluno, CandidaturaFormador, CodigoVerificacao, Usuario


class CandidaturaFormadorIntegradaTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            email='aluna.formadora@teste.local', nome='Luzia António', password='senha-segura', tipo_usuario='ALUNO'
        )
        self.aluno = Aluno.objects.create(usuario=self.user, nome='Luzia António', ativo=True)
        self.categoria, _ = Categoria.objects.get_or_create(slug='tecnologia', defaults={'nome': 'Tecnologia', 'descricao': 'Tecnologia'})
        self.client.force_login(self.user)

    def concluir_curso(self, numero):
        curso = Curso_video.objects.create(
            titulo=f'Curso concluído {numero}', descricao='Curso de demonstração para validar elegibilidade.', categoria=self.categoria
        )
        aula = Aula.objects.create(curso=curso, titulo=f'Aula {numero}', ordem=1, duracao_segundos=120)
        curso.inscritos.add(self.aluno)
        ProgressoAula.objects.create(aluno=self.aluno, aula=aula, concluida=True, tempo_assistido=120)
        return curso

    def test_does_not_expose_the_application_before_two_video_completions(self):
        self.concluir_curso(1)
        response = self.client.get('/auth/api/react/aluno/configuracoes/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json()['formador'])

    def test_exposes_the_application_after_two_video_completions(self):
        self.concluir_curso(1)
        self.concluir_curso(2)
        response = self.client.get('/auth/api/react/aluno/configuracoes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['formador']['estado'], 'ELEGIVEL')

    @patch('usuarios.views.enviar_codigo_verificacao', return_value='123456')
    def test_creates_a_verified_application_without_replacing_the_student_account(self, mocked_send):
        self.concluir_curso(1)
        self.concluir_curso(2)
        response = self.client.post('/auth/api/react/aluno/formador/enviar-codigo/', data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 200)
        mocked_send.assert_called_once_with(self.user.email, 'FORMADOR')
        CodigoVerificacao.objects.create(email=self.user.email, codigo='123456', tipo='FORMADOR')
        session = self.client.session
        session['formador_codigo_email'] = self.user.email
        session.save()
        response = self.client.post('/auth/api/react/aluno/formador/candidatar/', data=json.dumps({
            'codigo': '123456',
            'titulo_profissional': 'Especialista em Dados',
            'area_especializacao': 'TECNOLOGIA_INFORMACAO',
            'biografia': 'Tenho experiência em análise de dados e preparo aulas práticas que acompanham o ritmo de cada aluno.',
            'proposta_curso': 'Pretendo criar um curso de análise de dados com exercícios reais, projectos e acompanhamento aos participantes.',
            'respostas_teste': {'aprendizagem': 'B', 'inclusao': 'A', 'conteudo': 'B'},
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        candidatura = CandidaturaFormador.objects.get(aluno=self.aluno)
        self.assertEqual(candidatura.estado, 'PENDENTE_ANALISE')
        self.assertTrue(candidatura.teste_aprovado)
        self.user.refresh_from_db()
        self.assertEqual(self.user.tipo_usuario, 'ALUNO')
