from blog.models import Post
from rest_framework.test import APIClient

print('MODEL_COUNT', Post.objects.filter(status='publicado').count())
response = APIClient().get('/api/v1/blog/')
print('API_STATUS', response.status_code)
print('API_COUNT', response.data.get('count') if hasattr(response, 'data') and isinstance(response.data, dict) else len(response.data))
print('API_RESULTS', len(response.data.get('results', [])) if hasattr(response, 'data') and isinstance(response.data, dict) else len(response.data))
if hasattr(response, 'data') and isinstance(response.data, dict) and response.data.get('results'):
    print('FIRST_IMAGE', response.data['results'][0].get('imagem_capa'))
