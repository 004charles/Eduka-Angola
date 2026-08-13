from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import CentroDeFormacao, CentroSeguimento, Parceria, CandidaturaExterna
from .serializers import (
    CentroDeFormacaoSerializer, ParceriaSerializer,
    CandidaturaExternaSerializer, CandidaturaExternaCreateSerializer,
)
from cursos_app.serializers import CursoSerializer
from cursos_app.models import Curso

class CentroViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CentroDeFormacao.objects.filter(ativo=True).order_by('nome')
    serializer_class = CentroDeFormacaoSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(cache_page(60 * 10))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


    def get_queryset(self):
        queryset = super().get_queryset()
        provincia = self.request.query_params.get('provincia', None)
        cidade = self.request.query_params.get('cidade', None)
        if provincia:
            queryset = queryset.filter(provincia__iexact=provincia)
        if cidade:
            queryset = queryset.filter(cidade__iexact=cidade)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Obter os cursos desse centro específico
        cursos = Curso.objects.filter(centro=instance, publicado=True, ativo=True)
        cursos_serializer = CursoSerializer(cursos, many=True, context={'request': request})
        
        data = serializer.data
        data['cursos'] = cursos_serializer.data
        
        # Verificar se o aluno logado segue este centro
        data['seguindo'] = False
        if request.user.is_authenticated:
            try:
                aluno = request.user.aluno_profile
                data['seguindo'] = CentroSeguimento.objects.filter(aluno=aluno, centro=instance).exists()
            except AttributeError:
                pass
                
        return Response(data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def seguir(self, request, pk=None):
        centro = self.get_object()
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Apenas alunos podem seguir centros.'}, status=status.HTTP_400_BAD_REQUEST)

        seguimento, created = CentroSeguimento.objects.get_or_create(aluno=aluno, centro=centro)
        if not created:
            # Já existia, então deixa de seguir (unfollow)
            seguimento.delete()
            return Response({'seguindo': False, 'mensagem': f'Você deixou de seguir {centro.nome}.'})
        
        return Response({'seguindo': True, 'mensagem': f'Você começou a seguir {centro.nome}.'})


class ParceriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Parceria.objects.filter(ativa=True, parceiro_externo=True).order_by('-total_candidatos')
    serializer_class = ParceriaSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(nome_empresa__icontains=search)
        return queryset


class CandidaturaExternaViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CandidaturaExternaCreateSerializer
        return CandidaturaExternaSerializer

    def list(self, request):
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Perfil de aluno não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)
        
        candidaturas = CandidaturaExterna.objects.filter(aluno=aluno).select_related('parceria', 'curso')
        serializer = CandidaturaExternaSerializer(candidaturas, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Perfil de aluno não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            candidatura = CandidaturaExterna.objects.get(pk=pk, aluno=aluno)
        except CandidaturaExterna.DoesNotExist:
            return Response({'detail': 'Candidatura não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CandidaturaExternaSerializer(candidatura)
        return Response(serializer.data)

    def create(self, request):
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Perfil de aluno não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CandidaturaExternaCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            parceria = Parceria.objects.get(pk=data['parceria'], ativa=True, aceita_candidaturas=True)
        except Parceria.DoesNotExist:
            return Response({'detail': 'Parceria não encontrada ou não aceita candidaturas.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            curso = Curso.objects.get(pk=data['curso'], publicado=True, ativo=True)
        except Curso.DoesNotExist:
            return Response({'detail': 'Curso não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        # Handle file uploads
        doc = request.FILES.get('documento_inscricao')
        comprovativo = request.FILES.get('comprovativo_pagamento')

        candidatura = CandidaturaExterna(
            parceria=parceria,
            aluno=aluno,
            curso=curso,
            nome_completo=data['nome_completo'],
            email=data['email'],
            telefone=data['telefone'],
            bi=data.get('bi', ''),
            documento_inscricao=doc,
            comprovativo_pagamento=comprovativo,
        )
        candidatura.save()

        return Response(
            CandidaturaExternaSerializer(candidatura).data,
            status=status.HTTP_201_CREATED
        )
