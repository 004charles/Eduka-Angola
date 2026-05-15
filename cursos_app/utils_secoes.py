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
            'descricao': 'Os cursos mais recomendados pelos nossos centros.'
        },
        'desconto': {
            'titulo': 'Cursos com Desconto',
            'slug': 'desconto',
            'descricao': 'Aproveite as melhores ofertas para o seu bolso.'
        },
        'promocao': {
            'titulo': 'Cursos em Promoção',
            'slug': 'promocao',
            'descricao': 'Ofertas por tempo limitado. Não perca!'
        },
        'gratuitos': {
            'titulo': 'Cursos Gratuitos',
            'slug': 'gratuitos',
            'descricao': 'Aprenda sem custos com os nossos parceiros.'
        },
        'novos': {
            'titulo': 'Cursos Recém-Chegados',
            'slug': 'novos',
            'descricao': 'As últimas novidades na nossa plataforma.'
        },
        'semana': {
            'titulo': 'Cursos da Semana',
            'slug': 'semana',
            'descricao': 'Cursos com início previsto para os próximos 7 dias.'
        },
        'tecnologia': {
            'titulo': 'Tecnologia e Programação',
            'slug': 'tecnologia',
            'descricao': 'Desenvolva as competências digitais do futuro.'
        },
        'negocios': {
            'titulo': 'Gestão e Negócios',
            'slug': 'negocios',
            'descricao': 'Potencialize a sua carreira e o seu empreendimento.'
        },
        'linguas': {
            'titulo': 'Línguas e Comunicação',
            'slug': 'linguas',
            'descricao': 'Domine novos idiomas e conecte-se com o mundo.'
        },
        'populares': {
            'titulo': 'Mais Populares',
            'slug': 'populares',
            'descricao': 'Os cursos com maior procura na nossa plataforma.'
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
    cache_key = 'home_sections_data'
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
