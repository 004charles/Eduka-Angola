from django.utils import timezone
from .models import AvaliacaoHibridaCentro
from gestoreduka.models import CentroDeFormacao
from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Coalesce

def get_centro_da_semana():
    """
    Seleciona o centro da semana baseado em:
    (Plano Priority * 0.5) + (Trust Score * 0.5)
    """
    centros = CentroDeFormacao.objects.filter(ativo=True)
    
    # Anotando com o peso do plano se existir
    destaque = centros.annotate(
        plano_weight=Coalesce('assinatura__plano__prioridade_busca', 0, output_field=FloatField()),
        ia_score=Coalesce('avaliacao_hibrida__score_confianca', 0.0, output_field=FloatField())
    ).annotate(
        final_rank=ExpressionWrapper(
            (F('plano_weight') * 5.0) + F('ia_score'), 
            output_field=FloatField()
        )
    ).order_by('-final_rank').first()
    
    return destaque

def recalcular_metricas_centros():
    """
    Agrega dados reais para a avaliação híbrida.
    """
    from cursos_app.models import Inscricao
    from django.db.models import Avg
    
    for centro in CentroDeFormacao.objects.all():
        avaliacao, _ = AvaliacaoHibridaCentro.objects.get_or_create(centro=centro)
        
        # 1. Média de alunos (Ratings)
        # Buscando de Comentario (avaliacoes/models.py)
        from .models import Comentario
        media = Comentario.objects.filter(curso__centro=centro).aggregate(Avg('avaliacao'))['avaliacao__avg'] or 0.0
        avaliacao.media_alunos = media
        
        # 2. Taxa de Conclusão (Simulada ou baseada em ProgressoAula se disponível)
        # Por enquanto, baseada em Inscricoes vs Status 'Finalizado' (se existir)
        # Vamos olhar Inscricao STATUS_CHOICES: ('P', 'A', 'N', 'C')
        # Precisamos de um status 'CONCLUIDO' ou similar.
        # No cursovideoapp/models.py tem ProgressoAula.concluida.
        
        total_inscritos = Inscricao.objects.filter(curso__centro=centro).count()
        if total_inscritos > 0:
            # Simplificação: Taxa baseada em inscritos confirmados
            confirmados = Inscricao.objects.filter(curso__centro=centro, status='A').count()
            avaliacao.taxa_conclusao = (confirmados / total_inscritos) * 100
        
        avaliacao.calcular_score_final()
