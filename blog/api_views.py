from rest_framework import viewsets, filters, permissions
from .models import Post
from .serializers import PostSerializer

class PostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para visualização pública dos artigos/posts do blog.
    """
    queryset = Post.objects.filter(status='publicado').select_related('categoria').prefetch_related('tags').order_by('-publicado_em')
    serializer_class = PostSerializer
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['titulo', 'conteudo', 'resumo']

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

