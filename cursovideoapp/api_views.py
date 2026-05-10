from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Curso_video, Aula, Exercicio, ResultadoExercicio
from .serializers import CursoVideoSerializer, AulaSerializer, ExercicioSerializer, ResultadoExercicioSerializer

class CursoVideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Curso_video.objects.all().order_by('-data_publicacao')
    serializer_class = CursoVideoSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

class ExercicioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercicio.objects.all()
    serializer_class = ExercicioSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def submeter(self, request, pk=None):
        exercicio = self.get_object()
        respostas = request.data.get('respostas', [])
        aluno = request.user.aluno_profile
        
        # Lógica de correção (similar à view web)
        total = exercicio.questoes.count()
        acertos = 0
        
        for r in respostas:
            questao_id = r.get('questao_id')
            alternativa_id = r.get('alternativa_id')
            # ... lógica simplificada para API ...
            # Validar se alternativa_id é correta para questao_id
            from .models import Alternativa
            alt = Alternativa.objects.filter(id=alternativa_id, questao_id=questao_id, is_correta=True).exists()
            if alt:
                acertos += 1
        
        pontuacao = (acertos / total * 100) if total > 0 else 0
        
        resultado, created = ResultadoExercicio.objects.update_or_create(
            aluno=aluno,
            exercicio=exercicio,
            defaults={'pontuacao': pontuacao, 'acertos': acertos, 'total_questoes': total}
        )
        
        return Response(ResultadoExercicioSerializer(resultado).data)
