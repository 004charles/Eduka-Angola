from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Curso_video, Aula, Exercicio, ResultadoExercicio
from .serializers import CursoVideoSerializer, AulaSerializer, ExercicioSerializer, ResultadoExercicioSerializer

class CursoVideoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Curso_video.objects.all().select_related('instrutor', 'categoria').prefetch_related('aulas').order_by('-data_publicacao')
    serializer_class = CursoVideoSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class ExercicioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Exercicio.objects.all()
    serializer_class = ExercicioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _check_enrollment(self, exercicio):
        """Verifica se o aluno está inscrito no curso ao qual o exercício pertence."""
        try:
            aula = exercicio.aula
            curso = aula.curso
            aluno = self.request.user.aluno_profile
            if not curso.aluno_tem_acesso(aluno):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Precisa estar inscrito neste curso para aceder aos exercícios.')
        except AttributeError:
            pass

    def get_object(self):
        obj = super().get_object()
        self._check_enrollment(obj)
        return obj

    @action(detail=True, methods=['post'])
    def submeter(self, request, pk=None):
        exercicio = self.get_object()
        self._check_enrollment(exercicio)
        
        # MEDIUM-16 FIX: Limitar submissões (max 5 por exercício por hora)
        from django.core.cache import cache
        cache_key = f'exercicio_submit:{exercicio.pk}:{request.user.pk}'
        submissions = cache.get(cache_key, 0)
        if submissions >= 5:
            from rest_framework.exceptions import Throttled
            raise Throttled('Demasiadas submissões. Tente novamente mais tarde.')
        cache.set(cache_key, submissions + 1, timeout=3600)
        
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


from .models import ProgressoAula, NotaAula
from .serializers import ProgressoAulaSerializer, NotaAulaSerializer

class AulaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Aula.objects.all()
    serializer_class = AulaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _check_enrollment(self, aula):
        """Verifica se o aluno está inscrito no curso ao qual a aula pertence."""
        try:
            curso = aula.curso
            aluno = self.request.user.aluno_profile
            if not curso.aluno_tem_acesso(aluno):
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied('Precisa estar inscrito neste curso para aceder às aulas.')
        except AttributeError:
            pass

    def get_object(self):
        obj = super().get_object()
        self._check_enrollment(obj)
        return obj

    @action(detail=True, methods=['post'])
    def progresso(self, request, pk=None):
        aula = self.get_object()
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Apenas alunos possuem progresso de estudo.'}, status=status.HTTP_400_BAD_REQUEST)

        concluida = request.data.get('concluida', False)
        tempo_assistido = request.data.get('tempo_assistido', 0)

        progresso, created = ProgressoAula.objects.update_or_create(
            aluno=aluno,
            aula=aula,
            defaults={
                'concluida': concluida,
                'tempo_assistido': int(tempo_assistido)
            }
        )
        return Response(ProgressoAulaSerializer(progresso).data)

    @action(detail=True, methods=['post'])
    def nota(self, request, pk=None):
        aula = self.get_object()
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Apenas alunos podem fazer anotações de estudo.'}, status=status.HTTP_400_BAD_REQUEST)

        conteudo = request.data.get('conteudo', '').strip()
        if not conteudo:
            return Response({'detail': 'Conteúdo da nota é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        nota, created = NotaAula.objects.update_or_create(
            aluno=aluno,
            aula=aula,
            defaults={'conteudo': conteudo}
        )
        return Response(NotaAulaSerializer(nota).data)

