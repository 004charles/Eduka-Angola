from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Estagio, InscricaoEstagio
from .serializers import EstagioSerializer, InscricaoEstagioSerializer

class EstagioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para visualização de vagas de estágio e candidaturas dos alunos.
    """
    queryset = Estagio.objects.filter(ativo=True).select_related('centro_formacao', 'area').order_by('-data_publicacao')
    serializer_class = EstagioSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'descricao', 'requisitos', 'cidade', 'provincia']

    @method_decorator(cache_page(60 * 10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 10))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def candidatar(self, request, pk=None):
        estagio = self.get_object()
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Apenas alunos podem se candidatar a vagas de estágio.'}, status=status.HTTP_400_BAD_REQUEST)

        if not estagio.esta_aceitando_inscricoes:
            return Response({'detail': 'Esta vaga não está aceitando candidaturas.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se já existe candidatura
        if InscricaoEstagio.objects.filter(estagio=estagio, aluno=aluno).exists():
            return Response({'detail': 'Você já se candidatou a esta vaga.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InscricaoEstagioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save(aluno=aluno, estagio=estagio)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
