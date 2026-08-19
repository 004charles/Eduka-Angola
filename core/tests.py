from django.test import TestCase

from .models import Publicidade


class EducationalSponsorApiTest(TestCase):
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
