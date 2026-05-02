# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.measure import D
from cursos_app.models import Curso, Categoria
from .models import PontuacaoInteresse
from django.db.models import Q

def recomendar_cursos(aluno, limite=5):
    """
    Recomendação Híbrida: Interesses + Proximidade.
    """
    # 1. Obter categorias de interesse baseadas no histórico
    interesses_historico = PontuacaoInteresse.objects.filter(aluno=aluno).order_by('-peso')
    categorias_historico_ids = list(interesses_historico.values_list('categoria_id', flat=True))
    
    # 2. Obter categorias declaradas no perfil (Onboarding)
    categorias_declaradas_ids = []
    if hasattr(aluno, 'perfil'):
        categorias_declaradas_ids = list(aluno.perfil.interesses.values_list('id', flat=True))
    
    # Unificar categorias, priorizando as declaradas
    todas_categorias_ids = list(dict.fromkeys(categorias_declaradas_ids + categorias_historico_ids))
    
    # 2. Base de cursos ativos
    cursos = Curso.objects.filter(ativo=True, publicado=True)
    
    # 3. Filtrar por preferência de categoria
    if todas_categorias_ids:
        # Usar Case/When para ordenar por prioridade das categorias se necessário, 
        # ou apenas filtrar e manter a ordem de visualizações
        cursos = cursos.filter(categoria_id__in=todas_categorias_ids)
    
    # 4. Ajustar por proximidade se aluno tiver localização (apenas se PostGIS disponível)
    from django.conf import settings
    if hasattr(aluno, 'perfil') and aluno.perfil.localizacao and not getattr(settings, 'USE_SQLITE', False):
        user_loc = aluno.perfil.localizacao
        try:
            from django.contrib.gis.db.models.functions import Distance
            cursos = cursos.annotate(
                dist=Distance('centro__localizacao', user_loc)
            ).order_by('dist', '-visualizacoes')
        except Exception:
            # Fallback em caso de erro na query espacial
            cursos = cursos.order_by('-visualizacoes')
    else:
        cursos = cursos.order_by('-visualizacoes')
    
    return cursos[:limite]

def atualizar_pontuacao_interesse(aluno):
    """
    Analisa VisualizacaoInteligente e atualiza PontuacaoInteresse.
    """
    from .models import VisualizacaoInteligente
    from django.db.models import Count
    
    visitas = VisualizacaoInteligente.objects.filter(aluno=aluno).values('categoria').annotate(total=Count('id'))
    
    for visita in visitas:
        if visita['categoria']:
            pontuacao, _ = PontuacaoInteresse.objects.get_or_create(
                aluno=aluno,
                categoria_id=visita['categoria']
            )
            # Regra simples: 1 visualização = 1.0 peso
            pontuacao.peso = float(visita['total'])
            pontuacao.save()
