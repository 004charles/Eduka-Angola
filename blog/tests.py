from django.test import TestCase
from rest_framework.test import APIClient

from .models import Post


class BlogPublicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.post = Post.objects.create(
            titulo='Notícia de educação em Angola',
            slug='noticia-educacao-angola',
            resumo='Resumo da notícia.',
            conteudo='Conteúdo editorial da notícia.',
            tipo_conteudo='video',
            video_url='https://www.youtube.com/watch?v=abc123xyz00',
            duracao_video='04:20',
            status='publicado',
        )

    def test_lista_e_detalhe_por_slug(self):
        listing = self.client.get('/api/v1/blog/')
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data['results'][0]['tipo_conteudo'], 'video')
        self.assertEqual(listing.data['results'][0]['video_url'], self.post.video_url)

        detail = self.client.get('/api/v1/blog/noticia-educacao-angola/')
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['slug'], self.post.slug)
        self.assertEqual(detail.data['duracao_video'], '04:20')
