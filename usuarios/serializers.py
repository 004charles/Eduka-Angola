from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Aluno, PerfilAluno
from cursos_app.models import Categoria

User = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nome', 'email', 'tipo_usuario']

class PerfilAlunoSerializer(serializers.ModelSerializer):
    foto_perfil_url = serializers.CharField(source='get_foto_perfil_url', read_only=True)
    
    class Meta:
        model = PerfilAluno
        fields = [
            'onboarding_completo', 'nivel_conhecimento', 'biografia', 
            'telefone', 'linkedin', 'github', 'foto_perfil_url',
            'foto_de_perfil', 'foto_de_capa', 'bilhete_frente', 'bilhete_verso',
            'localizacao', 'interesses'
        ]
        read_only_fields = ['onboarding_completo']

class AlunoSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    perfil = PerfilAlunoSerializer(read_only=True)
    
    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'usuario', 'perfil']

class AlunoRegisterSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este e-mail já está cadastrado.")
        return value

    def create(self, validated_data):
        # Criar Usuario
        user = User.objects.create_user(
            email=validated_data['email'],
            nome=validated_data['nome'],
            password=validated_data['password'],
            tipo_usuario='ALUNO'
        )
        
        # Criar Aluno (PerfilAluno é criado automaticamente via sinal post_save)
        aluno = Aluno.objects.create(
            usuario=user,
            nome=validated_data['nome']
        )
        
        return aluno

class AlunoOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilAluno
        fields = ['nivel_conhecimento', 'interesses']

    def update(self, instance, validated_data):
        instance.nivel_conhecimento = validated_data.get('nivel_conhecimento', instance.nivel_conhecimento)
        if 'interesses' in validated_data:
            instance.interesses.set(validated_data['interesses'])
        instance.onboarding_completo = True
        instance.save()
        return instance

# Serializers para Certificados (Mobile)
class CertificadoVideoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    curso_titulo = serializers.CharField(source='curso.titulo')
    data_emissao = serializers.DateTimeField()
    codigo_verificacao = serializers.CharField()
    nota_final = serializers.DecimalField(max_digits=5, decimal_places=2)
    status = serializers.CharField()

class CertificadoCursoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    curso_titulo = serializers.CharField(source='inscricao.curso.titulo')
    data_emissao = serializers.DateTimeField()
    codigo_verificacao = serializers.CharField()

