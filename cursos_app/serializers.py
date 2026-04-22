from rest_framework import serializers
from .models import Curso, Categoria, Instrutor
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
