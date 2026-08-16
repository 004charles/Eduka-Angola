from pathlib import Path
from django.conf import settings
from blog.models import Post

posts = list(Post.objects.filter(status='publicado').order_by('slug'))
print('COUNT', len(posts))
for post in posts:
    image = Path(settings.MEDIA_ROOT) / post.imagem_capa.name if post.imagem_capa else None
    print(post.slug, post.tipo_conteudo, post.imagem_capa.name, image.exists() if image else False)
