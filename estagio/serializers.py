from rest_framework import serializers
from .models import Estagio, AreaEstagio, InscricaoEstagio
from gestoreduka.serializers import CentroDeFormacaoSerializer

class AreaEstagioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaEstagio
        fields = ['id', 'nome', 'slug', 'descricao', 'icone']

class EstagioSerializer(serializers.ModelSerializer):
    centro_formacao = CentroDeFormacaoSerializer(read_only=True)
    area = AreaEstagioSerializer(read_only=True)
    tipo_remuneracao_display = serializers.CharField(source='get_tipo_remuneracao_display', read_only=True)
    modalidade_display = serializers.CharField(source='get_modalidade_display', read_only=True)
    vagas_restantes = serializers.IntegerField(read_only=True)
    esta_aceitando_inscricoes = serializers.BooleanField(read_only=True)

    class Meta:
        model = Estagio
        fields = [
            'id', 'titulo', 'slug', 'descricao', 'resumo', 'centro_formacao',
            'area', 'tipo_remuneracao', 'tipo_remuneracao_display', 'valor_remuneracao',
            'beneficios', 'modalidade', 'modalidade_display', 'duracao_meses',
            'carga_horaria_semanal', 'vagas_disponiveis', 'vagas_preenchidas',
            'vagas_restantes', 'local_trabalho', 'cidade', 'provincia',
            'requisitos', 'competencias_desejadas', 'data_inicio', 'data_fim',
            'data_publicacao', 'data_limite_inscricao', 'esta_aceitando_inscricoes',
            'imagem_principal'
        ]

class InscricaoEstagioSerializer(serializers.ModelSerializer):
    class Meta:
        model = InscricaoEstagio
        fields = ['id', 'estagio', 'aluno', 'curriculo', 'carta_motivacao', 'data_inscricao', 'status', 'observacoes']
        read_only_fields = ['estagio', 'aluno', 'status', 'observacoes']
