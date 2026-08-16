from django.db import migrations
from django.utils import timezone


POSTS = [
    ('educacao-que-abre-portas', 'Educação que abre portas para novas oportunidades', 'educacao', 'A formação continua a ser uma das ferramentas mais importantes para transformar planos em oportunidades concretas.', 'Conheça caminhos de aprendizagem que ajudam estudantes e profissionais a preparar o próximo passo.', 'art-blog-01.png'),
    ('como-escolher-uma-formacao', 'Como escolher uma formação alinhada com os seus objetivos', 'educacao', 'Escolher um curso é mais simples quando se começa pelo objetivo que se quer alcançar.', 'Um guia prático para comparar áreas, duração, modalidade, local e condições antes de se inscrever.', 'art-blog-02.png'),
    ('competencias-digitais-angola', 'Competências digitais ganham espaço no mercado angolano', 'tecnologia', 'As competências digitais passaram de diferencial a parte essencial de muitas oportunidades profissionais.', 'Veja por onde começar e como organizar uma rotina de aprendizagem digital.', 'art-blog-03.png'),
    ('aprender-ao-longo-da-vida', 'Aprender ao longo da vida: uma escolha para qualquer idade', 'educacao', 'A aprendizagem não termina com o primeiro diploma. Novas competências podem ser construídas em qualquer fase.', 'Formação presencial e vídeo-cursos podem combinar-se com trabalho, família e outros compromissos.', 'blog-bl-02.jpg'),
    ('centros-de-formacao-comunidade', 'O papel dos centros de formação na comunidade', 'comunidade', 'Um centro de formação aproxima conhecimento, formadores e pessoas que procuram uma oportunidade.', 'Conheça como a informação clara sobre cursos pode ajudar mais alunos a decidir.', 'blog-card-01.jpg'),
    ('primeiros-passos-na-tecnologia', 'Primeiros passos para entrar na área de tecnologia', 'tecnologia', 'Começar na tecnologia não exige saber tudo. Exige curiosidade, prática e um percurso organizado.', 'Descubra áreas iniciais como ferramentas digitais, programação, dados e suporte técnico.', 'blog-card-02.jpg'),
    ('formacao-e-empregabilidade', 'Formação e empregabilidade: preparar o próximo passo', 'carreira', 'Uma formação útil liga conhecimento a uma competência que pode ser demonstrada.', 'Veja como definir metas, acompanhar progresso e apresentar melhor aquilo que já sabe fazer.', 'blog-card-03.jpg'),
    ('historias-de-aprendizagem', 'Histórias de aprendizagem que inspiram novas escolhas', 'comunidade', 'Cada percurso de aprendizagem começa com uma decisão: procurar informação e dar o primeiro passo.', 'A Edukangola reúne cursos e centros para tornar essa decisão mais simples.', 'blog-card-04.jpg'),
    ('guia-para-estudar-online', 'Guia para estudar online com consistência', 'tecnologia', 'Estudar online funciona melhor quando existe um horário realista e objetivos pequenos.', 'Cinco práticas para manter o ritmo, rever conteúdos e concluir uma formação em vídeo.', 'blog-card-05.jpg'),
    ('educacao-e-futuro-de-angola', 'Educação e o futuro de Angola', 'carreira', 'O futuro da formação constrói-se com acesso, informação de qualidade e oportunidades próximas das pessoas.', 'Uma reflexão sobre como estudantes, centros e plataformas podem participar nessa transformação.', 'blog-card-06.jpg'),
]


CATEGORY_DATA = {
    'educacao': ('Educação', 'Formação, aprendizagem e oportunidades educativas.'),
    'tecnologia': ('Tecnologia', 'Tecnologia e competências para o futuro.'),
    'carreira': ('Carreira', 'Empregabilidade, orientação e desenvolvimento profissional.'),
    'comunidade': ('Comunidade', 'Histórias e iniciativas da comunidade Edukangola.'),
}


def publish_posts(apps, schema_editor):
    Categoria = apps.get_model('blog', 'Categoria')
    Post = apps.get_model('blog', 'Post')
    for slug, titulo, category_slug, resumo, conteudo, image_name in POSTS:
        nome, descricao = CATEGORY_DATA[category_slug]
        categoria, _ = Categoria.objects.get_or_create(slug=category_slug, defaults={'nome': nome, 'descricao': descricao})
        Post.objects.update_or_create(
            slug=slug,
            defaults={
                'titulo': titulo,
                'categoria': categoria,
                'resumo': resumo,
                'conteudo': conteudo,
                'imagem_capa': f'static/blog/{image_name}',
                'tipo_conteudo': 'artigo',
                'video_url': '',
                'duracao_video': '',
                'status': 'publicado',
                'publicado_em': timezone.now(),
            },
        )


def keep_posts(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0004_post_duracao_video_post_tipo_conteudo_post_video_url'),
    ]

    operations = [migrations.RunPython(publish_posts, keep_posts)]
