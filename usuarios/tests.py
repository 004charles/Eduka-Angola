from django.test import TestCase
from .models import Usuario, Aluno
from gestoreduka.models import CentroDeFormacao

class UserUnificationTest(TestCase):
    def setUp(self):
        self.user_aluno = Usuario.objects.create_user(
            email='aluno@test.com',
            nome='Teste Aluno',
            password='testpassword123',
            tipo_usuario='ALUNO'
        )
        self.user_centro = Usuario.objects.create_user(
            email='centro@test.com',
            nome='Teste Centro',
            password='testpassword123',
            tipo_usuario='GESTOR'
        )

    def test_aluno_profile_creation(self):
        aluno = Aluno.objects.create(
            usuario=self.user_aluno,
            nome='Teste Aluno'
        )
        self.assertEqual(aluno.usuario.email, 'aluno@test.com')
        self.assertEqual(self.user_aluno.aluno_profile, aluno)

    def test_centro_profile_creation(self):
        centro = CentroDeFormacao.objects.create(
            usuario=self.user_centro,
            nome='Teste Centro',
            email='centro@test.com'
        )
        self.assertEqual(centro.usuario.email, 'centro@test.com')
        self.assertEqual(self.user_centro.centro_profile, centro)

    def test_cascade_delete(self):
        Aluno.objects.create(usuario=self.user_aluno, nome='Teste Aluno')
        self.user_aluno.delete()
        self.assertEqual(Aluno.objects.count(), 0)

    def test_user_types(self):
        self.assertEqual(self.user_aluno.tipo_usuario, 'ALUNO')
        self.assertEqual(self.user_centro.tipo_usuario, 'GESTOR')
