from django.test import TestCase


class LegacyReactRedirectsTests(TestCase):
    def test_rotas_de_aluno_legadas_redireccionam_para_react(self):
        response = self.client.get('/auth/aluno/dashboard/?origem=email')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/aluno?origem=email')

    def test_rotas_de_autenticacao_legadas_redireccionam_para_react(self):
        response = self.client.get('/auth/esqueci_senha/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/recuperar-palavra-passe')

    def test_catalogo_e_aula_de_video_legados_redireccionam_para_react(self):
        catalogo = self.client.get('/curso_video/lista/')
        detalhe = self.client.get('/curso_video/curso-antigo/')
        aula = self.client.get('/curso_video/curso-antigo/aula/9/')

        self.assertEqual(catalogo['Location'], '/cursos-em-video')
        self.assertEqual(detalhe['Location'], '/video-cursos/curso-antigo')
        self.assertEqual(aula['Location'], '/aprender/video/curso-antigo')
