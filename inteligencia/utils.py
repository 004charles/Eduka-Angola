from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from cursos_app.models import Curso, Categoria
from .models import PontuacaoInteresse
from django.db.models import Q

def recomendar_cursos(aluno, limite=5):
    """
    Recomendação Híbrida: Interesses + Proximidade.
    """
    # 1. Obter categorias de interesse baseadas no histórico
    interesses = PontuacaoInteresse.objects.filter(aluno=aluno).order_by('-peso')
    categorias_ids = interesses.values_list('categoria_id', flat=True)
    
    # 2. Base de cursos ativos
    cursos = Curso.objects.filter(ativo=True, publicado=True)
    
    # 3. Filtrar por preferência de categoria
    if categorias_ids:
        cursos = cursos.filter(categoria_id__in=categorias_ids)
    
    # 4. Ajustar por proximidade se aluno tiver localização (apenas se PostGIS disponível)
    from django.conf import settings
    if hasattr(aluno, 'perfil') and aluno.perfil.localizacao and not getattr(settings, 'USE_SQLITE', False):
        user_loc = aluno.perfil.localizacao
        try:
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
