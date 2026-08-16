from pathlib import Path
import shutil
from django.conf import settings
from django.db import connection
from django.utils import timezone
from blog.models import Categoria, Tag, Post

# A base atual tem histórico de migrations incompleto. Criamos apenas as tabelas do Blog que não existem.
models_to_create = [Categoria, Tag, Post]
existing_tables = set(connection.introspection.table_names())
with connection.schema_editor() as schema_editor:
    for model in models_to_create:
        table = model._meta.db_table
        if table not in existing_tables:
            schema_editor.create_model(model)
            existing_tables.add(table)

asset_dir = Path(settings.BASE_DIR) / 'edukangola exemplo' / 'assets' / 'images' / 'blog'
media_dir = Path(settings.MEDIA_ROOT) / 'posts' / 'capas'
media_dir.mkdir(parents=True, exist_ok=True)
assets = [
    asset_dir / 'art-blog-01.png', asset_dir / 'art-blog-02.png', asset_dir / 'art-blog-03.png',
    asset_dir / 'blog-bl-02.jpg', asset_dir / 'blog-card-01.jpg', asset_dir / 'blog-card-02.jpg',
    asset_dir / 'blog-card-03.jpg', asset_dir / 'blog-card-04.jpg',     asset_dir / 'blog-card-05.jpg', asset_dir / 'blog-card-06.jpg',
]

category_specs = [
    ('Educação', 'educacao', 'Formação, aprendizagem e oportunidades educativas.'),
    ('Tecnologia', 'tecnologia', 'Tecnologia e competências para o futuro.'),
    ('Carreira', 'carreira', 'Empregabilidade, orientação e desenvolvimento profissional.'),
    ('Comunidade', 'comunidade', 'Histórias e iniciativas da comunidade Edukangola.'),
]
for nome, slug, descricao in category_specs:
    Categoria.objects.get_or_create(slug=slug, defaults={'nome': nome, 'descricao': descricao})

posts = [
    ('educacao-que-abre-portas', 'Educação que abre portas para novas oportunidades', 'educacao', 'A formação continua a ser uma das ferramentas mais importantes para transformar planos em oportunidades concretas.', 'Conheça caminhos de aprendizagem que ajudam estudantes e profissionais a preparar o próximo passo.', 0),
    ('como-escolher-uma-formacao', 'Como escolher uma formação alinhada com os seus objetivos', 'educacao', 'Escolher um curso é mais simples quando se começa pelo objetivo que se quer alcançar.', 'Um guia prático para comparar áreas, duração, modalidade, local e condições antes de se inscrever.', 1),
    ('competencias-digitais-angola', 'Competências digitais ganham espaço no mercado angolano', 'tecnologia', 'As competências digitais passaram de diferencial a parte essencial de muitas oportunidades profissionais.', 'Veja por onde começar e como organizar uma rotina de aprendizagem digital.', 2),
    ('aprender-ao-longo-da-vida', 'Aprender ao longo da vida: uma escolha para qualquer idade', 'educacao', 'A aprendizagem não termina com o primeiro diploma. Novas competências podem ser construídas em qualquer fase.', 'Formação presencial e vídeo-cursos podem combinar-se com trabalho, família e outros compromissos.', 3),
    ('centros-de-formacao-comunidade', 'O papel dos centros de formação na comunidade', 'comunidade', 'Um centro de formação aproxima conhecimento, formadores e pessoas que procuram uma oportunidade.', 'Conheça como a informação clara sobre cursos pode ajudar mais alunos a decidir.', 4),
    ('primeiros-passos-na-tecnologia', 'Primeiros passos para entrar na área de tecnologia', 'tecnologia', 'Começar na tecnologia não exige saber tudo. Exige curiosidade, prática e um percurso organizado.', 'Descubra áreas iniciais como ferramentas digitais, programação, dados e suporte técnico.', 5),
    ('formacao-e-empregabilidade', 'Formação e empregabilidade: preparar o próximo passo', 'carreira', 'Uma formação útil liga conhecimento a uma competência que pode ser demonstrada.', 'Veja como definir metas, acompanhar progresso e apresentar melhor aquilo que já sabe fazer.', 6),
    ('historias-de-aprendizagem', 'Histórias de aprendizagem que inspiram novas escolhas', 'comunidade', 'Cada percurso de aprendizagem começa com uma decisão: procurar informação e dar o primeiro passo.', 'A Edukangola reúne cursos e centros para tornar essa decisão mais simples.', 7),
    ('guia-para-estudar-online', 'Guia para estudar online com consistência', 'tecnologia', 'Estudar online funciona melhor quando existe um horário realista e objetivos pequenos.', 'Cinco práticas para manter o ritmo, rever conteúdos e concluir uma formação em vídeo.', 8),
    ('educacao-e-futuro-de-angola', 'Educação e o futuro de Angola', 'carreira', 'O futuro da formação constrói-se com acesso, informação de qualidade e oportunidades próximas das pessoas.', 'Uma reflexão sobre como estudantes, centros e plataformas podem participar nessa transformação.', 9),
]

for slug, titulo, categoria_slug, resumo, conteudo, asset_index in posts:
    categoria = Categoria.objects.get(slug=categoria_slug)
    source = assets[asset_index]
    destination = media_dir / source.name
    if source.exists() and not destination.exists():
        shutil.copy2(source, destination)
    post, created = Post.objects.update_or_create(
        slug=slug,
        defaults={
            'titulo': titulo,
            'categoria': categoria,
            'resumo': resumo,
            'conteudo': conteudo,
            'imagem_capa': f'static/blog/{source.name}',
            'tipo_conteudo': 'artigo',
            'video_url': '',
            'duracao_video': '',
            'status': 'publicado',
            'publicado_em': timezone.now(),
        },
    )
    print('created' if created else 'updated', post.slug, post.imagem_capa.name)
