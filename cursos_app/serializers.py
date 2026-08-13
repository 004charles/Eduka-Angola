from rest_framework import serializers
from .models import Curso, Categoria, Instrutor, Modulo, Video, Inscricao
from gestoreduka.serializers import CentroDeFormacaoSerializer

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug', 'imagem']

class CursoSerializer(serializers.ModelSerializer):
    centro = CentroDeFormacaoSerializer(read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    rating = serializers.FloatField(source='get_media_avaliacoes', read_only=True)
    image_url = serializers.CharField(source='get_imagem_url', read_only=True)
    preco_formatado = serializers.SerializerMethodField()

    class Meta:
        model = Curso
        fields = [
            'id', 'titulo', 'descricao_curta', 'preco', 'preco_promocional', 
            'preco_formatado', 'destaque', 'categoria', 'centro', 'rating', 
            'image_url', 'slug'
        ]

    def get_preco_formatado(self, obj):
        if obj.is_gratuito:
            return "Gratuito"
        return f"{obj.preco:,.2f} Kz".replace(",", ".")

class VideoSerializer(serializers.ModelSerializer):
    fonte_video = serializers.CharField(read_only=True)

    class Meta:
        model = Video
        fields = ['id', 'titulo', 'descricao', 'fonte_video', 'duracao', 'ordem', 'liberado']

class ModuloSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = Modulo
        fields = ['id', 'titulo', 'ordem', 'descricao', 'videos']

class InscricaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inscricao
        fields = [
            'id', 'aluno', 'curso', 'status', 'tipo_inscricao', 
            'codigo_inscricao', 'forma_pagamento', 'valor_pago', 
            'data_pagamento', 'comprovante_pagamento'
        ]
        read_only_fields = ['codigo_inscricao', 'status', 'aluno', 'curso']


class InscricaoListaSerializer(serializers.ModelSerializer):
    curso = CursoSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Inscricao
        fields = [
            'id', 'curso', 'data_inscricao', 'status', 'status_display',
            'forma_pagamento', 'valor_pago', 'comprovante_pagamento'
        ]


