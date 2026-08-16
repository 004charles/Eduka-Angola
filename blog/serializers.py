from django.conf import settings
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
    imagem_capa = serializers.SerializerMethodField()
    tags = TagBlogSerializer(many=True, read_only=True)

    def get_imagem_capa(self, obj):
        if not obj.imagem_capa:
            return None
        name = obj.imagem_capa.name
        if name.startswith('static/'):
            path = '/' + name
        else:
            path = f'{settings.MEDIA_URL}{name}'
        request = self.context.get('request')
        return request.build_absolute_uri(path) if request else path

    class Meta:
        model = Post
        fields = [
            'id', 'titulo', 'slug', 'categoria', 'tags', 'conteudo', 
            'resumo', 'imagem_capa', 'tipo_conteudo', 'video_url', 'duracao_video', 'publicado_em', 'visualizacoes'
        ]
