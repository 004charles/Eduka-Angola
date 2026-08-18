import json

from django.test import TestCase

from cursos_app.models import Categoria, Instrutor
from cursovideoapp.models import Aula, ComentarioAula, Curso_video
from usuarios.models import Aluno, Usuario


class InstructorReactPortalTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(email='formador.portal@teste.local', nome='Formador React', password='senha-segura', tipo_usuario='INSTRUTOR')
        self.instrutor = Instrutor.objects.create(usuario=self.user, nome='Formador React', email='formador.portal@teste.local', biografia='Formador usado para testar o painel React.', area_especializacao='TECNOLOGIA_INFORMACAO')
        self.category = Categoria.objects.create(nome='Tecnologia React', slug='tecnologia-react')
        self.course = Curso_video.objects.create(titulo='Curso do formador', descricao='Curso criado para validar o painel do formador em React.', categoria=self.category, instrutor=self.instrutor, slug='curso-formador-react')
        self.lesson = Aula.objects.create(curso=self.course, titulo='Aula inicial', video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ', ordem=1)
        student_user = Usuario.objects.create_user(email='aluno.duvida@teste.local', nome='Aluno com Dúvida', password='senha-segura')
        student = Aluno.objects.create(usuario=student_user, nome='Aluno com Dúvida')
        self.question = ComentarioAula.objects.create(aluno=student, aula=self.lesson, texto='Como posso aprofundar este tema?')

    def test_requires_an_instructor_session(self):
        response = self.client.get('/instrutor/api/react/dashboard/')
        self.assertEqual(response.status_code, 401)

    def test_accepts_a_public_instructor_application_pending_approval(self):
        options = self.client.get('/instrutor/api/react/candidatura/opcoes/')
        self.assertEqual(options.status_code, 200)
        self.assertTrue(options.json()['areas'])

        response = self.client.post('/instrutor/api/react/candidatura/', data=json.dumps({
            'nome_completo': 'Candidata React',
            'email': 'candidata.react@teste.local',
            'password': 'senha-segura-2026',
            'confirm_password': 'senha-segura-2026',
            'area_especializacao': 'TECNOLOGIA_INFORMACAO',
            'biografia': 'Profissional com experiência prática e vontade de ensinar novos alunos.',
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        candidate = Usuario.objects.get(email='candidata.react@teste.local')
        self.assertEqual(candidate.tipo_usuario, 'INSTRUTOR')
        self.assertFalse(candidate.is_active)

    def test_exposes_dashboard_and_allows_course_and_answer_creation(self):
        self.client.force_login(self.user)
        dashboard = self.client.get('/instrutor/api/react/dashboard/')
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.json()['instrutor']['nome'], 'Formador React')
        self.assertEqual(len(dashboard.json()['duvidas']), 1)

        create_course = self.client.post('/instrutor/api/react/cursos/', data=json.dumps({'titulo': 'Novo curso React', 'descricao': 'Uma descrição suficientemente completa para publicar o novo curso.', 'categoria_id': self.category.id, 'is_pago': True, 'preco': 3500}), content_type='application/json')
        self.assertEqual(create_course.status_code, 201)
        self.assertEqual(create_course.json()['curso']['titulo'], 'Novo curso React')

        answer = self.client.post(f'/instrutor/api/react/duvidas/{self.question.id}/responder/', data=json.dumps({'texto': 'Comece pelos exercícios e reveja a aula com calma.'}), content_type='application/json')
        self.assertEqual(answer.status_code, 200)
        self.assertEqual(answer.json()['resposta']['autor'], 'Formador React')
