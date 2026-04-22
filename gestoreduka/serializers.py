from rest_framework import serializers
from .models import CentroDeFormacao, PerfilCentroDeFormacao

class PerfilCentroSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilCentroDeFormacao
        fields = ['imagem', 'slug', 'verificado']

class CentroDeFormacaoSerializer(serializers.ModelSerializer):
    perfil = PerfilCentroSerializer(read_only=True)
    
    class Meta:
        model = CentroDeFormacao
        fields = ['id', 'nome', 'email', 'telefone', 'cidade', 'provincia', 'perfil']
