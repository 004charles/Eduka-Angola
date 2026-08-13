from rest_framework import serializers
from .models import Post, Categoria, Tag

class CategoriaBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'slug', 'descricao']

class TagBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'nome', 'slug']

class PostSerializer(serializers.ModelSerializer):
    categoria = CategoriaBlogSerializer(read_only=True)
    tags = TagBlogSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'titulo', 'slug', 'categoria', 'tags', 'conteudo', 
            'resumo', 'imagem_capa', 'publicado_em', 'visualizacoes'
        ]
