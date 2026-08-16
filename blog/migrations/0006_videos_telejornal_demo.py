from django.db import migrations
from django.utils import timezone


VIDEOS = [
    ('telejornal-demo-educacao-em-movimento', 'Telejornal demo: Educação em movimento', 'Demonstração do formato Edukangola Agora para testar o destaque e o filtro de notícias em vídeo. Este conteúdo é apenas de teste.', 'https://www.youtube.com/watch?v=ysz5S6PUM-U', '03:14', 'art-blog-01.png'),
    ('telejornal-demo-aprender-com-tecnologia', 'Telejornal demo: Aprender com tecnologia', 'Vídeo de demonstração para validar a apresentação de notícias audiovisuais no Blog Edukangola. Não é uma notícia editorial real.', 'https://www.youtube.com/watch?v=ScMzIvxBSi4', '02:48', 'blog-card-02.jpg'),
    ('telejornal-demo-ideias-que-avancam', 'Telejornal demo: Ideias que fazem avançar', 'Publicação de vídeo de teste para verificar o filtro Telejornal, o cartão audiovisual e a página de detalhe.', 'https://www.youtube.com/watch?v=aqz-KE-bpKQ', '04:02', 'blog-card-04.jpg'),
]


def publish_demo_videos(apps, schema_editor):
    Categoria = apps.get_model('blog', 'Categoria')
    Post = apps.get_model('blog', 'Post')
    categoria, _ = Categoria.objects.get_or_create(
        slug='telejornal',
        defaults={'nome': 'Telejornal', 'descricao': 'Notícias e vídeos de demonstração do Edukangola Agora.'},
    )
    for slug, titulo, resumo, video_url, duracao, image_name in VIDEOS:
        Post.objects.update_or_create(
            slug=slug,
            defaults={
                'titulo': titulo,
                'categoria': categoria,
                'resumo': resumo,
                'conteudo': resumo,
                'imagem_capa': f'static/blog/{image_name}',
                'tipo_conteudo': 'video',
                'video_url': video_url,
                'duracao_video': duracao,
                'status': 'publicado',
                'publicado_em': timezone.now(),
            },
        )


def keep_demo_videos(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0005_publicar_noticias_iniciais'),
    ]

    operations = [migrations.RunPython(publish_demo_videos, keep_demo_videos)]
