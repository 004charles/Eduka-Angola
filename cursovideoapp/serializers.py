from rest_framework import serializers
from .models import Curso_video, Aula, Exercicio, Questao, Alternativa, ResultadoExercicio

class AlternativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alternativa
        fields = ['id', 'texto', 'is_correta']

class QuestaoSerializer(serializers.ModelSerializer):
    alternativas = AlternativaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Questao
        fields = ['id', 'texto', 'explicacao', 'alternativas']

class ExercicioSerializer(serializers.ModelSerializer):
    questoes = QuestaoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Exercicio
        fields = ['id', 'aula', 'titulo', 'descricao', 'questoes']

class AulaSerializer(serializers.ModelSerializer):
    exercicio = ExercicioSerializer(read_only=True)
    
    class Meta:
        model = Aula
        fields = ['id', 'titulo', 'video_url', 'ordem', 'duracao_segundos', 'descricao', 'exercicio']

class CursoVideoSerializer(serializers.ModelSerializer):
    aulas = AulaSerializer(many=True, read_only=True)
    rating = serializers.FloatField(source='get_media_avaliacoes', read_only=True)
    
    class Meta:
        model = Curso_video
        fields = [
            'id', 'titulo', 'descricao', 'instrutor', 'categoria', 
            'data_publicacao', 'capa', 'slug', 'is_pago', 'preco', 
            'rating', 'aulas'
        ]

class ResultadoExercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultadoExercicio
        fields = ['id', 'aluno', 'exercicio', 'pontuacao', 'acertos', 'total_questoes', 'data_conclusao']
