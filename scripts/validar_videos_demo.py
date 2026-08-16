from blog.models import Post
from rest_framework.test import APIClient

videos = list(Post.objects.filter(status='publicado', tipo_conteudo='video').values('slug', 'video_url', 'imagem_capa'))
print('VIDEO_COUNT', len(videos))
for video in videos:
    print(video)
response = APIClient().get('/api/v1/blog/')
items = response.data.get('results', [])
print('API_STATUS', response.status_code)
print('API_COUNT', response.data.get('count'))
print('API_VIDEO_COUNT', sum(1 for item in items if item.get('tipo_conteudo') == 'video' and item.get('video_url')))
