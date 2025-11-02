# forms.py
from django import forms
from cursos_app.models import Curso, Categoria, Instrutor

class CursoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.centro = kwargs.pop('centro', None)
        super().__init__(*args, **kwargs)
        
        if self.centro:
            # Filtrar instrutores apenas do centro logado
            self.fields['instrutores'].queryset = Instrutor.objects.filter(
                centro_de_formacao=self.centro, 
                ativo=True
            )
        else:
            self.fields['instrutores'].queryset = Instrutor.objects.none()
        
        self.fields['categoria'].queryset = Categoria.objects.all()

    class Meta:
        model = Curso
        fields = [
            'titulo', 'descricao', 'nivel', 'idioma', 'categoria',
            'certificado', 'instrutores', 'carga_horaria', 'preco',
            'vagas', 'data_inicio', 'data_termino', 'turno', 'imagem',
            'requisitos', 'video_apresentacao', 'destaque'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control py-11',
                'placeholder': 'Nome do curso',
                'maxlength': '200'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control py-11',
                'rows': 4,
                'placeholder': 'Descrição completa do curso'
            }),
            'nivel': forms.Select(attrs={
                'class': 'form-select py-9'
            }),
            'idioma': forms.Select(attrs={
                'class': 'form-select py-9'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select py-9'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'form-control py-11',
                'placeholder': 'Carga horária em horas',
                'min': '1'
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'form-control py-11',
                'placeholder': 'Valor do curso',
                'step': '0.001',
                'min': '0'
            }),
            'vagas': forms.NumberInput(attrs={
                'class': 'form-control py-11',
                'placeholder': 'Número de vagas disponíveis',
                'min': '1'
            }),
            'data_inicio': forms.DateTimeInput(attrs={
                'class': 'form-control py-11',
                'type': 'datetime-local'
            }),
            'data_termino': forms.DateInput(attrs={
                'class': 'form-control py-11',
                'type': 'date'
            }),
            'turno': forms.Select(attrs={
                'class': 'form-select py-9'
            }),
            'requisitos': forms.Textarea(attrs={
                'class': 'form-control py-11',
                'rows': 3,
                'placeholder': 'Pré-requisitos para o curso'
            }),
            'video_apresentacao': forms.URLInput(attrs={
                'class': 'form-control py-11',
                'placeholder': 'URL do vídeo de apresentação'
            }),
            'instrutores': forms.SelectMultiple(attrs={
                'class': 'form-select py-9',
                'multiple': 'multiple'
            }),
            'certificado': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'destaque': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }