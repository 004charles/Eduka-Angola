from rest_framework import viewsets, permissions, status
import re
import secrets
import uuid
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import CentroDeFormacao, CentroSeguimento, Parceria, CandidaturaExterna, CandidaturaCentro, PerfilCentroDeFormacao
from .serializers import (
    CentroDeFormacaoSerializer, ParceriaSerializer,
    CandidaturaExternaSerializer, CandidaturaExternaCreateSerializer,
)
from cursos_app.serializers import CursoSerializer
from cursos_app.models import Curso
from core.email_utils import enviar_email_brevo
from planos.models import Plano


def _normalizar_nif(value):
    return re.sub(r'[^A-Za-z0-9]', '', str(value or '')).upper()


def _email_mascarado(email):
    local, _, domain = email.partition('@')
    return f"{local[:2]}{'*' * max(1, len(local) - 2)}@{domain}"


class CentroCandidaturaRequestSerializer(drf_serializers.Serializer):
    email = drf_serializers.EmailField()
    nif = drf_serializers.CharField(max_length=18, min_length=3)

    def validate_nif(self, value):
        value = _normalizar_nif(value)
        if len(value) < 3:
            raise drf_serializers.ValidationError('Indique um NIF válido.')
        return value


class CentroCandidaturaVerifySerializer(CentroCandidaturaRequestSerializer):
    codigo = drf_serializers.RegexField(r'^\d{6}$')


class CentroCandidaturaCompleteSerializer(CentroCandidaturaRequestSerializer):
    candidatura_id = drf_serializers.IntegerField(required=False)
    convite = drf_serializers.UUIDField(required=False)
    nome_centro = drf_serializers.CharField(max_length=100)
    nome_gestor = drf_serializers.CharField(max_length=100)
    senha = drf_serializers.CharField(min_length=8, write_only=True)
    confirm_senha = drf_serializers.CharField(min_length=8, write_only=True)
    telefone = drf_serializers.CharField(max_length=20, required=False, allow_blank=True)
    endereco = drf_serializers.CharField(max_length=255, required=False, allow_blank=True)
    cidade = drf_serializers.CharField(max_length=100, required=False, allow_blank=True)
    provincia = drf_serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs['senha'] != attrs['confirm_senha']:
            raise drf_serializers.ValidationError({'confirm_senha': 'As palavras-passe não coincidem.'})
        return attrs

class CentroPlanosView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        planos = Plano.objects.filter(ativo=True).order_by('preco')
        return Response([
            {
                'id': plano.id,
                'nome': plano.nome,
                'descricao': plano.descricao,
                'preco': str(plano.preco),
                'moeda': 'AOA',
                'limite_cursos': plano.limite_cursos,
                'limite_cursos_video': plano.limite_cursos_video,
                'selo_verificacao': plano.selo_verificacao,
                'destaque_home': plano.destaque_home,
                'acesso_relatorios': plano.acesso_relatorios,
                'permite_inscricao_manual': plano.permite_inscricao_manual,
                'permite_gerar_certificado': plano.permite_gerar_certificado,
                'permite_cursos_video': plano.permite_cursos_video,
            }
            for plano in planos
        ])


class CentroCandidaturaRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CentroCandidaturaRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip().lower()
        nif = serializer.validated_data['nif']

        if CentroDeFormacao.objects.filter(email__iexact=email).exists() or CentroDeFormacao.objects.filter(nif=nif).exists():
            return Response({'detail': 'Já existe um centro registado com este email ou NIF.'}, status=status.HTTP_409_CONFLICT)

        codigo = f'{secrets.randbelow(1000000):06d}'
        agora = timezone.now()
        candidatura, _ = CandidaturaCentro.objects.update_or_create(
            email=email,
            nif=nif,
            status__in=['PENDENTE', 'VERIFICADA'],
            defaults={
                'codigo_hash': make_password(codigo),
                'link_token': uuid.uuid4(),
                'link_criado_em': agora,
                'link_expira_em': agora + timedelta(hours=24),
                'link_usado': False,
                'codigo_criado_em': agora,
                'codigo_expira_em': agora + timedelta(minutes=15),
                'tentativas': 0,
                'verificado_em': None,
                'status': 'PENDENTE',
            },
        )

        enviado = enviar_email_brevo(
            to_email=email,
            subject='Complete o cadastro do seu centro no Edukangola',
            html_content=f'<p>Recebemos um pedido para cadastrar um centro no Edukangola.</p><p><a href="{getattr(settings, "SITE_DOMAIN", "http://127.0.0.1:8000").rstrip("/")}/para-centros/?convite={candidatura.link_token}">Clique aqui para continuar o cadastro</a>.</p><p>Por segurança, este link é pessoal e válido durante 24 horas.</p>',
            text_content=f'Para continuar o cadastro do centro no Edukangola, abra este link: {getattr(settings, "SITE_DOMAIN", "http://127.0.0.1:8000").rstrip("/")}/para-centros/?convite={candidatura.link_token}. O link é pessoal e válido durante 24 horas.',
        )
        if not enviado:
            return Response({'detail': 'Não foi possível enviar o link agora. Tente novamente.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({'candidatura_id': candidatura.id, 'email_mascarado': _email_mascarado(email), 'expira_em_segundos': 86400})


class CentroCandidaturaVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CentroCandidaturaVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip().lower()
        nif = serializer.validated_data['nif']
        candidatura = CandidaturaCentro.objects.filter(email=email, nif=nif, status='PENDENTE').order_by('-data_criacao').first()
        if not candidatura:
            return Response({'detail': 'Pedido de candidatura não encontrado ou já verificado.'}, status=status.HTTP_400_BAD_REQUEST)
        if candidatura.codigo_expira_em <= timezone.now():
            candidatura.status = 'EXPIRADA'
            candidatura.save(update_fields=['status', 'data_atualizacao'])
            return Response({'detail': 'O código expirou. Solicite um novo código.'}, status=status.HTTP_400_BAD_REQUEST)
        if candidatura.tentativas >= 5:
            return Response({'detail': 'Número máximo de tentativas atingido. Solicite um novo código.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        if not check_password(serializer.validated_data['codigo'], candidatura.codigo_hash):
            candidatura.tentativas += 1
            candidatura.save(update_fields=['tentativas', 'data_atualizacao'])
            return Response({'detail': 'Código inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        candidatura.status = 'VERIFICADA'
        candidatura.verificado_em = timezone.now()
        candidatura.save(update_fields=['status', 'verificado_em', 'data_atualizacao'])
        return Response({'candidatura_id': candidatura.id, 'verificado': True})


class CentroCandidaturaConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.query_params.get('convite')
        candidatura = CandidaturaCentro.objects.filter(link_token=token, link_usado=False).first()
        if not candidatura:
            return Response({'detail': 'Este convite não existe ou já foi utilizado.'}, status=status.HTTP_404_NOT_FOUND)
        if candidatura.link_expira_em <= timezone.now():
            candidatura.status = 'EXPIRADA'
            candidatura.save(update_fields=['status', 'data_atualizacao'])
            return Response({'detail': 'Este convite expirou. Solicite um novo link.'}, status=status.HTTP_410_GONE)
        candidatura.status = 'VERIFICADA'
        candidatura.verificado_em = timezone.now()
        candidatura.save(update_fields=['status', 'verificado_em', 'data_atualizacao'])
        return Response({'candidatura_id': candidatura.id, 'email': candidatura.email, 'nif': candidatura.nif, 'convite': str(candidatura.link_token), 'verificado': True})


class CentroCandidaturaCompleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CentroCandidaturaCompleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data['email'].strip().lower()
        nif = data['nif']
        from usuarios.models import Usuario

        with transaction.atomic():
            candidatura_query = CandidaturaCentro.objects.select_for_update().filter(
                email=email, nif=nif, status='VERIFICADA', link_usado=False
            )
            if data.get('convite'):
                candidatura_query = candidatura_query.filter(link_token=data['convite'])
            elif data.get('candidatura_id'):
                candidatura_query = candidatura_query.filter(id=data['candidatura_id'])
            candidatura = candidatura_query.first()
            if not candidatura:
                return Response({'detail': 'Verifique o email antes de concluir o cadastro.'}, status=status.HTTP_400_BAD_REQUEST)
            if Usuario.objects.filter(email__iexact=email).exists() or CentroDeFormacao.objects.filter(nif=nif).exists():
                return Response({'detail': 'Já existe uma conta ou centro com estes dados.'}, status=status.HTTP_409_CONFLICT)
            usuario = Usuario.objects.create_user(email=email, nome=data['nome_gestor'], password=data['senha'], tipo_usuario='GESTOR', is_active=True)
            centro = CentroDeFormacao.objects.create(
                usuario=usuario, nome=data['nome_centro'], email=email, nif=nif,
                telefone=data.get('telefone', ''), endereco=data.get('endereco', ''),
                cidade=data.get('cidade', ''), provincia=data.get('provincia', ''), ativo=True,
            )
            PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
            candidatura.centro = centro
            candidatura.status = 'CONCLUIDA'
            candidatura.link_usado = True
            candidatura.save(update_fields=['centro', 'status', 'link_usado', 'data_atualizacao'])
        return Response({'centro_id': centro.id, 'mensagem': 'Cadastro concluído. Já pode entrar no GestorEduka.'}, status=status.HTTP_201_CREATED)


class CentroViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CentroDeFormacao.objects.filter(ativo=True).select_related('perfil').annotate(
        total_cursos_publicos=Count('cursos', filter=Q(cursos__publicado=True, cursos__ativo=True), distinct=True)
    ).order_by('-total_cursos_publicos', 'nome')
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
