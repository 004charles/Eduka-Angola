from rest_framework import serializers
from .models import CentroDeFormacao, PerfilCentroDeFormacao, Parceria, CandidaturaExterna

class PerfilCentroSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilCentroDeFormacao
        fields = ['imagem', 'slug', 'verificado']

class CentroDeFormacaoSerializer(serializers.ModelSerializer):
    perfil = PerfilCentroSerializer(read_only=True)
    
    class Meta:
        model = CentroDeFormacao
        fields = ['id', 'nome', 'email', 'telefone', 'cidade', 'provincia', 'perfil']

class ParceriaSerializer(serializers.ModelSerializer):
    centro_nome = serializers.CharField(source='centro.nome', read_only=True)
    
    class Meta:
        model = Parceria
        fields = [
            'id', 'centro', 'centro_nome', 'nome_empresa', 'logo', 'website',
            'tipo_parceria', 'descricao', 'localizacao', 'contacto',
            'parceiro_externo', 'aceita_candidaturas', 'total_candidatos', 'ativa',
        ]

class CandidaturaExternaSerializer(serializers.ModelSerializer):
    parceria_nome = serializers.CharField(source='parceria.nome_empresa', read_only=True)
    curso_nome = serializers.CharField(source='curso.titulo', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = CandidaturaExterna
        fields = [
            'id', 'parceria', 'parceria_nome', 'aluno', 'curso', 'curso_nome',
            'nome_completo', 'email', 'telefone', 'bi',
            'documento_inscricao', 'comprovativo_pagamento',
            'status', 'status_display', 'observacoes', 'resposta_admin',
            'data_criacao', 'data_atualizacao',
        ]
        read_only_fields = ['aluno', 'status', 'resposta_admin', 'data_criacao', 'data_atualizacao']

class CandidaturaExternaCreateSerializer(serializers.Serializer):
    parceria = serializers.IntegerField()
    curso = serializers.IntegerField()
    nome_completo = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    telefone = serializers.CharField(max_length=20)
    bi = serializers.CharField(max_length=30, required=False, allow_blank=True)
