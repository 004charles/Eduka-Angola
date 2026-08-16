from django.utils import timezone
from django.db.models import Q, Count
from datetime import timedelta
from .models import Curso

def get_secoes_config():
    """
    Retorna a configuração das secções de cursos disponíveis no sistema.
    """
    return {
        'destaque': {
            'titulo': 'Cursos em Destaque',
            'slug': 'destaque',
            'descricao': 'Os cursos mais recomendados pelos nossos centros de formação. A EdukAngola ajuda-o a desenvolver as competências mais procuradas pelo mercado de trabalho, com rapidez e eficácia. Avance na sua carreira de forma segura.'
        },
        'desconto': {
            'titulo': 'Cursos com Desconto',
            'slug': 'desconto',
            'descricao': 'Aproveite as melhores ofertas para o seu bolso e inicie já a sua qualificação. Uma excelente oportunidade para impulsionar o seu currículo sem comprometer o orçamento.'
        },
        'promocao': {
            'titulo': 'Cursos em Promoção',
            'slug': 'promocao',
            'descricao': 'Ofertas exclusivas por tempo limitado. Não perca a oportunidade de aprender novas habilidades com os melhores profissionais do país, pagando muito menos do valor habitual.'
        },
        'gratuitos': {
            'titulo': 'Cursos Gratuitos',
            'slug': 'gratuitos',
            'descricao': 'Aprenda sem custos com os nossos parceiros educacionais. Desenvolvemos parcerias estratégicas para garantir que o conhecimento chegue a todos, independentemente da condição financeira.'
        },
        'novos': {
            'titulo': 'Cursos Recém-Chegados',
            'slug': 'novos',
            'descricao': 'As últimas novidades a chegar à nossa plataforma. Mantenha-se atualizado com as metodologias mais recentes e descubra formações acabadas de lançar pelos centros de excelência.'
        },
        'semana': {
            'titulo': 'Cursos da Semana',
            'slug': 'semana',
            'descricao': 'Cursos com início previsto para os próximos 7 dias. Não deixe para amanhã o que pode começar hoje: garanta já o seu lugar nestas turmas que estão prestes a arrancar.'
        },
        'tecnologia': {
            'titulo': 'Tecnologia e Programação',
            'slug': 'tecnologia',
            'descricao': 'Desenvolva as competências digitais do futuro. Numa era dominada pela tecnologia, dominar estas ferramentas é o passo certo para garantir evolução no mercado de trabalho atual.'
        },
        'negocios': {
            'titulo': 'Gestão e Negócios',
            'slug': 'negocios',
            'descricao': 'Potencialize a sua carreira e o seu espírito empreendedor. Aprenda com especialistas as melhores táticas de gestão, liderança e marketing para levar os seus resultados ao próximo nível.'
        },
        'linguas': {
            'titulo': 'Línguas e Comunicação',
            'slug': 'linguas',
            'descricao': 'Domine novos idiomas e conecte-se com o mundo globalizado. A fluência em línguas estrangeiras é o passaporte mais importante para alcançar oportunidades internacionais de sucesso.'
        },
        'populares': {
            'titulo': 'Mais Populares',
            'slug': 'populares',
            'descricao': 'Os cursos com maior procura na nossa plataforma. Descubra o que milhares de estudantes angolanos estão a aprender neste momento e junte-se a esta comunidade incrível.'
        }
    }

def filtrar_cursos_por_secao(queryset, secao_key):
    """
    Aplica filtros ao queryset de cursos baseado na secção solicitada.
    """
    agora = timezone.now()
    hoje = agora.date()
    
    # Filtro base: apenas cursos publicados e ativos
    qs = queryset.filter(publicado=True, ativo=True)
    
    if secao_key == 'destaque':
        return qs.filter(destaque=True)
    
    elif secao_key == 'desconto':
        return qs.filter(preco_promocional__gt=0)
    
    elif secao_key == 'promocao':
        return qs.filter(
            data_inicio_promocao__lte=agora,
            data_fim_promocao__gte=agora,
            preco_promocional__gt=0
        )
    
    elif secao_key == 'gratuitos':
        return qs.filter(Q(preco=0) | Q(is_gratuito=True))
    
    elif secao_key == 'novos':
        return qs.order_by('-data_criacao')
    
    elif secao_key == 'semana':
        proximos_7_dias = hoje + timedelta(days=7)
        return qs.filter(data_inicio__range=(hoje, proximos_7_dias)).order_by('data_inicio')
    
    elif secao_key == 'tecnologia':
        return qs.filter(Q(categoria__nome__icontains='Tecnologia') | Q(categoria__nome__icontains='Informática') | Q(categoria__nome__icontains='Programação'))
    
    elif secao_key == 'negocios':
        return qs.filter(Q(categoria__nome__icontains='Negócio') | Q(categoria__nome__icontains='Gestão') | Q(categoria__nome__icontains='Marketing'))
    
    elif secao_key == 'linguas':
        return qs.filter(Q(categoria__nome__icontains='Língua') | Q(categoria__nome__icontains='Idioma') | Q(categoria__nome__icontains='Inglês') | Q(categoria__nome__icontains='Francês'))
    
    elif secao_key == 'populares':
        return qs.annotate(num_inscricoes=Count('inscricoes')).order_by('-num_inscricoes', '-visualizacoes')
    
    return qs

from django.core.cache import cache

def get_home_sections_data():
    """
    Retorna uma lista de dicionários contendo os dados de cada secção para a Home.
    Utiliza cache para evitar múltiplas consultas pesadas em cada refresh.
    """
    cache_key = 'home_sections_data_v2'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return cached_data

    config = get_secoes_config()
    sections_order = ['destaque', 'novos', 'desconto', 'semana', 'gratuitos', 'tecnologia', 'negocios', 'linguas', 'populares']
    
    sections_data = []
    
    for key in sections_order:
        qs = filtrar_cursos_por_secao(Curso.objects.all(), key)
        # Otimização: Pegamos apenas o que precisamos e usamos select_related para evitar N+1
        cursos = list(qs.select_related('centro', 'categoria')[:15])
        
        if cursos:
            sections_data.append({
                'config': config[key],
                'cursos': cursos
            })
            
    # Cache por 15 minutos (900 segundos)
    cache.set(cache_key, sections_data, 900)
    return sections_data
