from rest_framework import serializers
from django.db.models import Q
from cursos_app.models import Curso
from .models import CentroDeFormacao, PerfilCentroDeFormacao, Parceria, CandidaturaExterna

class PerfilCentroSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilCentroDeFormacao
        fields = ['imagem', 'slug', 'verificado']

class CentroDeFormacaoSerializer(serializers.ModelSerializer):
    perfil = PerfilCentroSerializer(read_only=True)
    logo_url = serializers.SerializerMethodField()
    banner_url = serializers.SerializerMethodField()
    verificado = serializers.SerializerMethodField()
    total_cursos = serializers.IntegerField(source='total_cursos_publicos', read_only=True)
    modalidades = serializers.SerializerMethodField()
    pais_nome = serializers.SerializerMethodField()
    localizacao = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    is_internacional = serializers.SerializerMethodField()

    def _arquivo_url(self, obj, field):
        perfil = getattr(obj, 'perfil', None)
        arquivo = getattr(perfil, field, None) if perfil else None
        if not arquivo:
            return ''
        try:
            request = self.context.get('request')
            return request.build_absolute_uri(arquivo.url) if request else arquivo.url
        except (ValueError, AttributeError):
            return ''

    def get_logo_url(self, obj):
        return self._arquivo_url(obj, 'imagem')

    def get_banner_url(self, obj):
        return self._arquivo_url(obj, 'banner')

    def get_verificado(self, obj):
        perfil = getattr(obj, 'perfil', None)
        return bool(perfil and perfil.verificado)

    def get_modalidades(self, obj):
        choices = dict(Curso.MODALIDADE_CHOICES)
        return [choices.get(code, code) for code in obj.cursos.filter(publicado=True, ativo=True).values_list('modalidade', flat=True).distinct()]

    def get_pais_nome(self, obj):
        return obj.get_pais_display()

    def get_localizacao(self, obj):
        return ', '.join(item for item in [obj.cidade, obj.provincia, obj.get_pais_display()] if item)

    def get_latitude(self, obj):
        ponto = getattr(obj, 'localizacao', None)
        return ponto.y if hasattr(ponto, 'y') else None

    def get_longitude(self, obj):
        ponto = getattr(obj, 'localizacao', None)
        return ponto.x if hasattr(ponto, 'x') else None

    def get_is_internacional(self, obj):
        return obj.pais != 'AO'

    class Meta:
        model = CentroDeFormacao
        fields = ['id', 'nome', 'email', 'telefone', 'pais', 'pais_nome', 'cidade', 'provincia', 'endereco', 'localizacao', 'latitude', 'longitude', 'is_internacional', 'perfil', 'logo_url', 'banner_url', 'verificado', 'total_cursos', 'modalidades']

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
