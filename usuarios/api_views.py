from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Aluno, PerfilAluno
from .serializers import (
    AlunoSerializer, AlunoRegisterSerializer, 
    AlunoOnboardingSerializer, PerfilAlunoSerializer,
    CertificadoVideoSerializer, CertificadoCursoSerializer
)
from cursovideoapp.models import Certificado
from cursos_app.models import CertificadoCurso

class AlunoViewSet(viewsets.GenericViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    
    def get_permissions(self):
        if self.action in ['register', 'esqueci_senha', 'redefinir_senha']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = AlunoRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        aluno = serializer.save()
        
        # Gerar tokens JWT para o usuário recém-registrado
        refresh = RefreshToken.for_user(aluno.usuario)
        
        return Response({
            'aluno': AlunoSerializer(aluno, context={'request': request}).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='onboarding')
    def onboarding(self, request):
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Usuário não possui perfil de aluno.'}, status=status.HTTP_400_BAD_REQUEST)
            
        perfil = aluno.perfil
        serializer = AlunoOnboardingSerializer(perfil, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'sucesso': True,
            'mensagem': 'Onboarding concluído com sucesso.',
            'perfil': PerfilAlunoSerializer(perfil, context={'request': request}).data
        })

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Usuário não possui perfil de aluno.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'GET':
            serializer = AlunoSerializer(aluno, context={'request': request})
            return Response(serializer.data)
            
        elif request.method in ['PUT', 'PATCH']:
            perfil = aluno.perfil
            serializer = PerfilAlunoSerializer(perfil, data=request.data, partial=(request.method == 'PATCH'), context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Se o nome também for alterado
            nome = request.data.get('nome')
            if nome:
                aluno.nome = nome
                aluno.save()
                aluno.usuario.nome = nome
                aluno.usuario.save()

            return Response(AlunoSerializer(aluno, context={'request': request}).data)

    @action(detail=False, methods=['get'], url_path='certificados')
    def certificados(self, request):
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Usuário não possui perfil de aluno.'}, status=status.HTTP_400_BAD_REQUEST)

        certificados_video = Certificado.objects.filter(aluno=aluno, status='EMITIDO')
        certificados_curso = CertificadoCurso.objects.filter(inscricao__aluno=aluno, inscricao__status='A')

        serializer_video = CertificadoVideoSerializer(certificados_video, many=True)
        serializer_curso = CertificadoCursoSerializer(certificados_curso, many=True)

        return Response({
            'cursos_video': serializer_video.data,
            'cursos_presenciais_online': serializer_curso.data
        })

    @action(detail=False, methods=['get'], url_path='favoritos')
    def favoritos(self, request):
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Usuário não possui perfil de aluno.'}, status=status.HTTP_400_BAD_REQUEST)

        from cursos_app.models import Favorito
        from cursos_app.serializers import CursoSerializer

        favoritos = Favorito.objects.filter(aluno=aluno).select_related('curso')
        cursos = [f.curso for f in favoritos if f.curso.publicado and f.curso.ativo]
        serializer = CursoSerializer(cursos, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='inscricoes')
    def inscricoes(self, request):
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return Response({'detail': 'Usuário não possui perfil de aluno.'}, status=status.HTTP_400_BAD_REQUEST)

        from cursos_app.models import Inscricao
        from cursos_app.serializers import InscricaoListaSerializer

        inscricoes = Inscricao.objects.filter(aluno=aluno).order_by('-data_inscricao')
        serializer = InscricaoListaSerializer(inscricoes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='esqueci-senha')
    def esqueci_senha(self, request):
        from django.core.cache import cache as _cache
        
        # Rate limiting: 3 tentativas por minuto por IP
        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', '')
        rl_key = f"ratelimit:esqueci_senha:{ip}"
        if _cache.get(rl_key, 0) >= 3:
            return Response(
                {'error': 'Demasiadas tentativas. Aguarde alguns minutos.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        _cache.set(rl_key, _cache.get(rl_key, 0) + 1, 60)
        
        email = request.data.get('email', '').strip()
        if not email:
            return Response({'error': 'E-mail é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Resposta genérica sempre (sem enumeração de email)
        if Aluno.objects.filter(usuario__email=email).exists():
            from .views import enviar_codigo_verificacao
            try:
                enviar_codigo_verificacao(email, 'RECUPERACAO')
            except Exception:
                pass
        
        return Response({'success': True, 'message': 'Se existir uma conta com este e-mail, enviámos um código de recuperação.'})

    @action(detail=False, methods=['post'], url_path='redefinir-senha')
    def redefinir_senha(self, request):
        from django.utils import timezone
        from datetime import timedelta
        
        email = request.data.get('email', '').strip()
        codigo = request.data.get('codigo', '').strip()
        nova_senha = request.data.get('senha', '').strip()
        confirmar_senha = request.data.get('confirmar_senha', '').strip()
        
        if not email or not codigo or not nova_senha or not confirmar_senha:
            return Response({'error': 'Todos os campos (email, codigo, senha, confirmar_senha) são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if nova_senha != confirmar_senha:
            return Response({'error': 'As senhas não coincidem.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(nova_senha) < 8:
            return Response({'error': 'A senha deve ter pelo menos 8 caracteres.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from .models import CodigoVerificacao, Usuario
            
            # CRIT-13 FIX: Verificar expiração do código (janela de 10 minutos)
            verificacao = CodigoVerificacao.objects.filter(
                email=email,
                codigo=codigo,
                tipo='RECUPERACAO',
                criado_em__gte=timezone.now() - timedelta(minutes=10),
            ).order_by('-criado_em').first()
            
            if not verificacao:
                # Verificar se o código existe mas expirou
                codigo_expirado = CodigoVerificacao.objects.filter(
                    email=email, codigo=codigo, tipo='RECUPERACAO'
                ).exists()
                if codigo_expirado:
                    return Response({'error': 'Código expirado. Solicite um novo código.'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'error': 'Código inválido.'}, status=status.HTTP_400_BAD_REQUEST)
            
            usuario = Usuario.objects.get(email=email)
            usuario.set_password(nova_senha)
            usuario.save()
            
            # Limpar todos os códigos de recuperação deste email
            CodigoVerificacao.objects.filter(email=email, tipo='RECUPERACAO').delete()
            return Response({'success': True, 'message': 'Senha redefinida com sucesso!'})
        except CodigoVerificacao.DoesNotExist:
            return Response({'error': 'Código inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

