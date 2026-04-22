from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from .models import Curso, Categoria
from .serializers import CursoSerializer, CategoriaSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite visualizar os cursos.
    """
    queryset = Curso.objects.filter(publicado=True, ativo=True).order_by('-data_criacao')
    serializer_class = CursoSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'descricao', 'tags']
    ordering_fields = ['preco', 'data_criacao', 'visualizacoes']

    def get_queryset(self):
        queryset = super().get_queryset()
        destaque = self.request.query_params.get('destaque', None)
        if destaque is not None:
            queryset = queryset.filter(destaque=True)
        return queryset

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite visualizar as categorias.
    """
    queryset = Categoria.objects.all().order_by('nome')
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]
