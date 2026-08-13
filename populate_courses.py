"""
Populate database with 20 courses + 4 video courses with generated images.
Usage: python manage.py shell < populate_courses.py
"""
import os, sys, django
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduangolacore.settings')
django.setup()

from cursos_app.models import Categoria, Curso, Instrutor
from gestoreduka.models import CentroDeFormacao
from cursovideoapp.models import Curso_video, Aula
from django.core.files.base import ContentFile
from io import BytesIO

MEDIA = Path(__file__).parent / 'media'
MEDIA.mkdir(exist_ok=True)

# Colors for placeholder images
COLORS = [
    ('#5B18E6', '#EDE7FE'), ('#159B5E', '#DDF3E8'), ('#B57A12', '#FBF0D9'),
    ('#E8433D', '#FDE7E7'), ('#3B7DD8', '#E7F0FD'), ('#D94E8E', '#FDE7F3'),
    ('#2ECC71', '#D5F5E3'), ('#E67E22', '#FDEBD0'), ('#8E44AD', '#EBDEF0'),
    ('#1ABC9C', '#D1F2EB'), ('#C0392B', '#FADBD8'), ('#2980B9', '#D6EAF8'),
    ('#27AE60', '#D4EFDF'), ('#F39C12', '#FEF9E7'), ('#9B59B6', '#F4ECF7'),
    ('#16A085', '#E8F8F5'), ('#D35400', '#FDEBD0'), ('#C0392B', '#F9EBEA'),
    ('#7F8C8D', '#EAECEE'), ('#2C3E50', '#D5D8DC'), ('#8E44AD', '#E8DAEF'),
]

def make_image(text, color1, color2, size=(800, 500), filename='temp.png'):
    """Generate a colored placeholder image with text."""
    img = Image.new('RGB', size, color1)
    draw = ImageDraw.Draw(img)
    # Add a colored band
    draw.rectangle([0, 0, size[0], size[1]//3], fill=color2)
    # Add circle decoration
    draw.ellipse([size[0]-120, 20, size[0]-20, 120], fill=color1)
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", 36)
        small_font = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default()
        small_font = font
    # Center text
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((size[0]-tw)//2, (size[1]-th)//2), text, fill='#ffffff', font=font)
    # Subtitle
    draw.text((30, size[1]-50), 'EdukAngola', fill=color1, font=small_font)
    
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return ContentFile(buf.read(), filename)

# Get or create center
centro, _ = CentroDeFormacao.objects.get_or_create(
    email='centro@teste.com',
    defaults={'nome': 'Centro de Formação EdukAngola', 'ativo': True}
)
print(f'Centro: {centro.nome} (id={centro.id})')

# Get categories
cats = list(Categoria.objects.all())
if len(cats) < 5:
    print('Precisa de mais categorias!')
    sys.exit(1)

# === 20 CURSOS ===
cursos_data = [
    {'titulo': 'Introdução à Programação Web', 'cat_idx': 0, 'nivel': 'B', 'duracao': '3_MESES', 'preco': 45000, 'modalidade': 'PRESENCIAL', 'carga': 120},
    {'titulo': 'Desenvolvimento Mobile com React Native', 'cat_idx': 0, 'nivel': 'I', 'duracao': '4_MESES', 'preco': 65000, 'modalidade': 'ONLINE', 'carga': 160},
    {'titulo': 'Gestão de Projetos com Scrum', 'cat_idx': 1, 'nivel': 'B', 'duracao': '2_MESES', 'preco': 35000, 'modalidade': 'HIBRIDO', 'carga': 80},
    {'titulo': 'Contabilidade Geral e Aplicada', 'cat_idx': 8, 'nivel': 'B', 'duracao': '6_MESES', 'preco': 55000, 'modalidade': 'PRESENCIAL', 'carga': 240},
    {'titulo': 'Primeiros Socorros e Emergência', 'cat_idx': 2, 'nivel': 'B', 'duracao': '1_MES', 'preco': 25000, 'modalidade': 'PRESENCIAL', 'carga': 40},
    {'titulo': 'Design Gráfico com Adobe Creative Suite', 'cat_idx': 3, 'nivel': 'B', 'duracao': '3_MESES', 'preco': 50000, 'modalidade': 'ONLINE', 'carga': 120},
    {'titulo': 'Metodologias de Ensino Inovadoras', 'cat_idx': 4, 'nivel': 'I', 'duracao': '4_MESES', 'preco': 40000, 'modalidade': 'HIBRIDO', 'carga': 160},
    {'titulo': 'Automação Industrial com Arduino', 'cat_idx': 5, 'nivel': 'I', 'duracao': '3_MESES', 'preco': 55000, 'modalidade': 'PRESENCIAL', 'carga': 120},
    {'titulo': 'Marketing Digital e Redes Sociais', 'cat_idx': 6, 'nivel': 'B', 'duracao': '2_MESES', 'preco': 30000, 'modalidade': 'ONLINE', 'carga': 80},
    {'titulo': 'Inglês para Negócios', 'cat_idx': 7, 'nivel': 'B', 'duracao': '6_MESES', 'preco': 45000, 'modalidade': 'HIBRIDO', 'carga': 180},
    {'titulo': 'Análise Financeira com Excel', 'cat_idx': 8, 'nivel': 'B', 'duracao': '1_MES', 'preco': 20000, 'modalidade': 'ONLINE', 'carga': 40},
    {'titulo': 'Soldagem e Caldeiraria', 'cat_idx': 9, 'nivel': 'B', 'duracao': '4_MESES', 'preco': 35000, 'modalidade': 'PRESENCIAL', 'carga': 160},
    {'titulo': 'Cibersegurança Fundamentals', 'cat_idx': 0, 'nivel': 'B', 'duracao': '3_MESES', 'preco': 60000, 'modalidade': 'ONLINE', 'carga': 120},
    {'titulo': 'Gestão de Recursos Humanos', 'cat_idx': 1, 'nivel': 'I', 'duracao': '3_MESES', 'preco': 40000, 'modalidade': 'HIBRIDO', 'carga': 120},
    {'titulo': 'Enfermagem Geral', 'cat_idx': 2, 'nivel': 'B', 'duracao': '1_ANO', 'preco': 85000, 'modalidade': 'PRESENCIAL', 'carga': 480},
    {'titulo': 'Fotografia e Edição Digital', 'cat_idx': 3, 'nivel': 'B', 'duracao': '2_MESES', 'preco': 30000, 'modalidade': 'ONLINE', 'carga': 80},
    {'titulo': 'Construção Civil Sustentável', 'cat_idx': 5, 'nivel': 'I', 'duracao': '6_MESES', 'preco': 70000, 'modalidade': 'PRESENCIAL', 'carga': 240},
    {'titulo': 'Espanhol Básico', 'cat_idx': 7, 'nivel': 'B', 'duracao': '4_MESES', 'preco': 35000, 'modalidade': 'HIBRIDO', 'carga': 160},
    {'titulo': 'Empreendedorismo e Plano de Negócios', 'cat_idx': 1, 'nivel': 'B', 'duracao': '2_MESES', 'preco': 25000, 'modalidade': 'ONLINE', 'carga': 80},
    {'titulo': 'Manutenção de Computadores', 'cat_idx': 0, 'nivel': 'B', 'duracao': '2_MESES', 'preco': 28000, 'modalidade': 'PRESENCIAL', 'carga': 80},
]

created_cursos = 0
for i, data in enumerate(cursos_data):
    if Curso.objects.filter(titulo=data['titulo']).exists():
        print(f'  [skip] {data["titulo"]}')
        continue
    
    cat = cats[data['cat_idx'] % len(cats)]
    c1, c2 = COLORS[i % len(COLORS)]
    
    slug = data['titulo'].lower().replace(' ', '-').replace('ã', 'a').replace('ç', 'c').replace('í', 'i').replace('ó', 'o').replace('é', 'e').replace('ê', 'e').replace('á', 'a')
    
    curso = Curso(
        centro=centro,
        titulo=data['titulo'],
        descricao=f'{data["titulo"]}. Curso completo com certificado. Modalidade: {data["modalidade"]}. Carga horária: {data["carga"]}h.',
        descricao_curta=f'{data["titulo"]} - Modalidade {data["modalidade"]}',
        nivel=data['nivel'],
        categoria=cat,
        carga_horaria=data['carga'],
        preco=data['preco'],
        modalidade=data['modalidade'],
        duracao=data['duracao'],
        ativo=True,
        publicado=True,
        destaque=(i < 5),
        tags=data['titulo'],
    )
    curso.save()
    
    # Generate image
    img_file = make_image(data['titulo'][:30], c1, c2, filename=f'curso_{curso.id}.png')
    curso.imagem.save(f'curso_{curso.id}.png', img_file, save=True)
    
    created_cursos += 1
    print(f'  [create] {data["titulo"]} (cat={cat.nome}, {data["modalidade"]}, {data["preco"]} Kz)')

print(f'\n=== {created_cursos} cursos criados (total: {Curso.objects.count()}) ===')

# === 4 VIDEO CURSOS ===
video_cursos_data = [
    {
        'titulo': 'Python do Zero ao Avançado',
        'cat_idx': 0,
        'descricao': 'Aprenda Python completo: variáveis, funções, POO, APIs, banco de dados e muito mais.',
        'preco': 35000,
        'aulas': [
            'Introdução ao Python e Ambiente de Desenvolvimento',
            'Variáveis, Tipos de Dados e Operadores',
            'Estruturas de Controle (if/else/for/while)',
            'Funções e Escopos',
            'Programação Orientada a Objetos',
            'Tratamento de Erros e Exceções',
            'Trabalhando com Arquivos',
            'Módulos e Pacotes',
            'Introdução a APIs REST',
            'Projeto Final: Sistema Completo',
        ],
    },
    {
        'titulo': 'UI/UX Design com Figma',
        'cat_idx': 3,
        'descricao': 'Domine Figma: wireframes, prototipagem, design systems e entregas profissionais.',
        'preco': 40000,
        'aulas': [
            'Introdução ao Figma e Interface',
            'Wireframing e Arquitetura de Informação',
            'Design de Componentes',
            'Sistemas de Design',
            'Prototipagem Interativa',
            'Design Responsivo',
            'Auto Layout e Variants',
            'Handoff para Desenvolvedores',
            'Projeto: App Mobile Completo',
            'Projeto Final: Portfolio de Design',
        ],
    },
    {
        'titulo': 'Excel Avançado para Empresas',
        'cat_idx': 8,
        'descricao': 'Fórmulas avançadas, tabelas dinâmicas, dashboards, macros VBA e automação.',
        'preco': 25000,
        'aulas': [
            'Atalhos e Formatação Profissional',
            'Fórmulas Avançadas (PROCV, SE, ÍNDICE)',
            'Tabelas Dinâmicas',
            'Gráficos Dinâmicos e Dashboards',
            'Validação de Dados',
            'Funções de Texto e Data',
            'Introdução a Macros VBA',
            'Automação de Relatórios',
            'Power Query e Power Pivot',
            'Projeto Final: Dashboard Empresarial',
        ],
    },
    {
        'titulo': 'Inglês Conversação e Negócios',
        'cat_idx': 7,
        'descricao': 'Inglês prático para o mundo corporativo: reuniões, emails, apresentações e networking.',
        'preco': 45000,
        'aulas': [
            'Greetings and Introductions',
            'Email Writing for Business',
            'Meeting Vocabulary and Phrases',
            'Giving Presentations',
            'Negotiation Skills in English',
            'Phone and Video Calls',
            'Networking Events',
            'Report Writing',
            'Job Interviews in English',
            'Final Project: Business Presentation',
        ],
    },
]

created_videos = 0
for i, data in enumerate(video_cursos_data):
    if Curso_video.objects.filter(titulo=data['titulo']).exists():
        print(f'  [skip] {data["titulo"]}')
        continue
    
    cat = cats[data['cat_idx'] % len(cats)]
    c1, c2 = COLORS[(i + 10) % len(COLORS)]
    
    vc = Curso_video(
        titulo=data['titulo'],
        descricao=data['descricao'],
        categoria=cat,
        centro=centro,
        preco=data['preco'],
        is_pago=True,
        destaque=True,
    )
    vc.save()
    
    # Generate cover image
    img_file = make_image(data['titulo'][:30], c1, c2, filename=f'video_curso_{vc.id}.png', size=(800, 450))
    vc.capa.save(f'video_curso_{vc.id}.png', img_file, save=True)
    
    # Create aulas
    for j, aula_titulo in enumerate(data['aulas']):
        Aula.objects.create(
            curso=vc,
            titulo=aula_titulo,
            ordem=j + 1,
            duracao_segundos=600 + (j * 120),
            descricao=f'Aula {j+1}: {aula_titulo}',
        )
    
    created_videos += 1
    print(f'  [create] {data["titulo"]} ({len(data["aulas"])} aulas, capa gerada)')

print(f'\n=== {created_videos} video-cursos criados (total: {Curso_video.objects.count()}) ===')
print(f'\n=== RESUMO FINAL ===')
print(f'  Categorias: {Categoria.objects.count()}')
print(f'  Cursos presenciais/online: {Curso.objects.count()}')
print(f'  Video-cursos: {Curso_video.objects.count()}')
print(f'  Aulas totais: {Aula.objects.count()}')
print(f'  Imagens salvas em: {MEDIA / "cursos"}')
