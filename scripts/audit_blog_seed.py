from pathlib import Path
from blog.models import Post

root = Path('edukangola exemplo/assets/images/blog')
print('ASSETS')
for path in sorted(root.glob('*')):
    if path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}:
        print(path)
print('POSTS')
for post in Post.objects.order_by('-publicado_em'):
    print(post.id, post.slug, post.tipo_conteudo, post.status, post.imagem_capa.name or '')
