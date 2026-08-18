from django.test import TestCase

from cursos_app.models import Categoria
from cursovideoapp.models import Certificado, Curso_video
from usuarios.models import Aluno, Usuario


class PublicCertificateVerificationTest(TestCase):
    def setUp(self):
        user = Usuario.objects.create_user(email='certificado.publico@teste.local', nome='Aluno Certificado', password='senha-segura')
        aluno = Aluno.objects.create(usuario=user, nome='Aluno Certificado')
        categoria = Categoria.objects.create(nome='Certificados públicos', slug='certificados-publicos')
        curso = Curso_video.objects.create(titulo='Curso de validação', descricao='Curso usado apenas para validar a consulta pública.', categoria=categoria, slug='curso-validacao')
        self.certificado = Certificado.objects.create(aluno=aluno, curso=curso, codigo_verificacao='VALIDO-QR-2026')

    def test_exposes_an_emitted_video_certificate_without_authentication(self):
        response = self.client.get('/api/public/certificados/VALIDO-QR-2026/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()['certificado']
        self.assertEqual(payload['estado'], 'válido')
        self.assertEqual(payload['aluno'], 'Aluno Certificado')
        self.assertEqual(payload['curso'], 'Curso de validação')

    def test_returns_a_png_qr_for_a_valid_certificate(self):
        response = self.client.get('/api/public/certificados/VALIDO-QR-2026/qr/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response.content.startswith(b'\x89PNG'))

    def test_does_not_expose_unknown_certificate_codes(self):
        response = self.client.get('/api/public/certificados/INEXISTENTE/')
        self.assertEqual(response.status_code, 404)
