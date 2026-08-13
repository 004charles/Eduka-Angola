from rest_framework import viewsets, filters, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
import uuid
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Curso, Categoria, Inscricao, Modulo, Favorito
from .serializers import CursoSerializer, CategoriaSerializer, ModuloSerializer, InscricaoSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite visualizar os cursos.
    """
    queryset = Curso.objects.filter(publicado=True, ativo=True).select_related('centro', 'categoria').order_by('-data_criacao')
    serializer_class = CursoSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'descricao', 'tags']
    ordering_fields = ['preco', 'data_criacao', 'visualizacoes']

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        destaque = self.request.query_params.get('destaque', None)
        if destaque is not None:
            queryset = queryset.filter(destaque=True)
        return queryset

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def ementa(self, request, pk=None):
        """Retorna o currículo/ementa detalhada (módulos e videoaulas) do curso"""
        curso = self.get_object()
        modulos = Modulo.objects.filter(curso=curso).prefetch_related('videos').order_by('ordem')
        serializer = ModuloSerializer(modulos, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def inscrever(self, request, pk=None):
        """Realiza inscrição inicial (pendente de pagamento) do aluno no curso"""
        curso = self.get_object()
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Apenas alunos podem se inscrever em cursos.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se já existe uma inscrição ativa ou pendente
        inscricao = Inscricao.objects.filter(aluno=aluno, curso=curso).exclude(status='C').first()
        if inscricao:
            return Response({
                'mensagem': 'Você já tem uma inscrição para este curso.',
                'inscricao': InscricaoSerializer(inscricao, context={'request': request}).data
            }, status=status.HTTP_200_OK)

        # Criar nova inscrição pendente
        codigo = str(uuid.uuid4()).split('-')[0].upper()
        inscricao = Inscricao.objects.create(
            aluno=aluno,
            curso=curso,
            status='P',
            codigo_inscricao=codigo,
            forma_pagamento=request.data.get('forma_pagamento', 'TRANSFERENCIA')
        )
        
        return Response({
            'mensagem': 'Inscrição iniciada com sucesso. Envie o comprovante de pagamento.',
            'inscricao': InscricaoSerializer(inscricao, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated], url_path='enviar-comprovante')
    def enviar_comprovante(self, request, pk=None):
        """Faz upload do comprovante de pagamento de uma inscrição pendente"""
        curso = self.get_object()
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Apenas alunos podem enviar comprovantes.'}, status=status.HTTP_400_BAD_REQUEST)

        inscricao = Inscricao.objects.filter(aluno=aluno, curso=curso, status='P').first()
        if not inscricao:
            return Response({'detail': 'Nenhuma inscrição pendente encontrada para este curso.'}, status=status.HTTP_404_NOT_FOUND)

        comprovante = request.FILES.get('comprovante')
        if not comprovante:
            return Response({'detail': 'Arquivo de comprovante é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        inscricao.comprovante_pagamento = comprovante
        inscricao.data_pagamento = timezone.now()
        inscricao.save()

        return Response({
            'mensagem': 'Comprovante enviado com sucesso. Aguarde validação da secretaria.',
            'inscricao': InscricaoSerializer(inscricao, context={'request': request}).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favoritar(self, request, pk=None):
        """Alterna (favorita/desfavorita) o curso para o aluno logado"""
        curso = self.get_object()
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Apenas alunos podem favoritar cursos.'}, status=status.HTTP_400_BAD_REQUEST)

        favorito, created = Favorito.objects.get_or_create(aluno=aluno, curso=curso)
        if not created:
            favorito.delete()
            return Response({'favorito': False, 'mensagem': 'Curso removido dos favoritos.'})
            
        return Response({'favorito': True, 'mensagem': 'Curso adicionado aos favoritos.'})

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite visualizar as categorias.
    """
    queryset = Categoria.objects.all().order_by('nome')
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]
