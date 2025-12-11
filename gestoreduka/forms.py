# forms.py
from django import forms
from cursos_app.models import Curso, Categoria, Instrutor

# forms.py
from django import forms
from django.utils import timezone
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
            ).order_by('nome')
            
            # Categorias - todas disponíveis (não filtradas por centro)
            self.fields['categoria'].queryset = Categoria.objects.all().order_by('nome')
        else:
            self.fields['instrutores'].queryset = Instrutor.objects.none()
            self.fields['categoria'].queryset = Categoria.objects.all().order_by('nome')

        # Adicionar placeholders e help texts
        self.fields['titulo'].help_text = 'Máximo 200 caracteres'
        self.fields['preco'].help_text = 'Valor em Kz. Use 0 para curso gratuito'
        self.fields['data_inicio_inscricoes'].help_text = 'Data e hora de início das inscrições'
        self.fields['data_fim_inscricoes'].help_text = 'Data de término das inscrições (opcional)'
        self.fields['vagas_minimas'].help_text = 'Número mínimo de alunos para o curso acontecer'

    class Meta:
        model = Curso
        fields = [
            'titulo', 'descricao', 'descricao_curta', 'nivel', 'idioma', 'categoria',
            'certificado', 'instrutores', 'carga_horaria', 'preco', 'preco_inscricao',
            'preco_promocional', 'data_inicio_promocao', 'data_fim_promocao',
            'vagas_minimas', 'data_inicio_inscricoes', 'data_fim_inscricoes',
            'modalidade', 'publicado', 'imagem', 'requisitos', 'objetivo_geral',
            'publico_alvo', 'destaque', 'permite_parcelamento', 'max_parcelas', 'tags'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'placeholder': 'Ex: Curso Completo de Python para Iniciantes',
                'maxlength': '200'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'rows': 4,
                'placeholder': 'Descreva detalhadamente o conteúdo, objetivos e benefícios do curso...'
            }),
            'descricao_curta': forms.TextInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'placeholder': 'Descrição resumida para cards e listagens (máx. 300 caracteres)',
                'maxlength': '300'
            }),
            'nivel': forms.Select(attrs={
                'class': 'form-select py-12 px-16 rounded-12 border border-gray-100'
            }),
            'idioma': forms.Select(attrs={
                'class': 'form-select py-12 px-16 rounded-12 border border-gray-100'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select py-12 px-16 rounded-12 border border-gray-100'
            }),
            'modalidade': forms.Select(attrs={
                'class': 'form-select py-12 px-16 rounded-12 border border-gray-100'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'placeholder': 'Ex: 40',
                'min': '1',
                'max': '1000'
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
            'preco_inscricao': forms.NumberInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
            'preco_promocional': forms.NumberInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
            'vagas_minimas': forms.NumberInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'placeholder': 'Ex: 10',
                'min': '1',
                'max': '1000'
            }),
            'data_inicio_inscricoes': forms.DateTimeInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'type': 'datetime-local',
            }),
            'data_fim_inscricoes': forms.DateTimeInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'type': 'datetime-local',
            }),
            'data_inicio_promocao': forms.DateTimeInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'type': 'datetime-local',
            }),
            'data_fim_promocao': forms.DateTimeInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'type': 'datetime-local',
            }),
            'requisitos': forms.Textarea(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'rows': 3,
                'placeholder': 'Ex: Conhecimentos básicos de informática, Idade mínima: 16 anos...'
            }),
            'objetivo_geral': forms.Textarea(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'rows': 3,
                'placeholder': 'Descreva os objetivos gerais do curso...'
            }),
            'publico_alvo': forms.Textarea(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'rows': 3,
                'placeholder': 'Descreva o público-alvo do curso...'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'placeholder': 'Ex: python, programação, iniciantes, web development'
            }),
            'max_parcelas': forms.NumberInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'min': '1',
                'max': '24'
            }),
            'instrutores': forms.SelectMultiple(attrs={
                'class': 'form-select py-12 px-16 rounded-12 border border-gray-100',
                'size': '4'
            }),
            'certificado': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 18px; height: 18px;'
            }),
            'destaque': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 18px; height: 18px;'
            }),
            'publicado': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 18px; height: 18px;'
            }),
            'permite_parcelamento': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 18px; height: 18px;'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'form-control py-12 px-16 rounded-12 border border-gray-100',
                'accept': 'image/*'
            })
        }
        labels = {
            'titulo': 'Título do Curso *',
            'descricao': 'Descrição Detalhada *',
            'descricao_curta': 'Descrição Curta *',
            'nivel': 'Nível do Curso *',
            'idioma': 'Idioma *',
            'categoria': 'Categoria *',
            'certificado': 'Oferece Certificado?',
            'instrutores': 'Instrutores *',
            'carga_horaria': 'Carga Horária (horas) *',
            'preco': 'Preço Normal (Kz) *',
            'preco_inscricao': 'Taxa de Inscrição (Kz)',
            'preco_promocional': 'Preço Promocional (Kz)',
            'data_inicio_promocao': 'Início da Promoção',
            'data_fim_promocao': 'Fim da Promoção',
            'vagas_minimas': 'Vagas Mínimas *',
            'data_inicio_inscricoes': 'Início das Inscrições *',
            'data_fim_inscricoes': 'Fim das Inscrições',
            'modalidade': 'Modalidade *',
            'publicado': 'Publicar Curso?',
            'imagem': 'Imagem de Capa',
            'requisitos': 'Pré-requisitos',
            'objetivo_geral': 'Objetivo Geral',
            'publico_alvo': 'Público-Alvo',
            'destaque': 'Destacar este curso?',
            'permite_parcelamento': 'Permitir Parcelamento?',
            'max_parcelas': 'Máximo de Parcelas',
            'tags': 'Tags (Palavras-chave)'
        }

    def clean(self):
        cleaned_data = super().clean()
        data_inicio_inscricoes = cleaned_data.get('data_inicio_inscricoes')
        data_fim_inscricoes = cleaned_data.get('data_fim_inscricoes')
        data_inicio_promocao = cleaned_data.get('data_inicio_promocao')
        data_fim_promocao = cleaned_data.get('data_fim_promocao')
        preco = cleaned_data.get('preco')
        preco_promocional = cleaned_data.get('preco_promocional')
        
        # Validação de datas de inscrição
        if data_inicio_inscricoes and data_fim_inscricoes:
            if data_fim_inscricoes <= data_inicio_inscricoes:
                raise forms.ValidationError({
                    'data_fim_inscricoes': 'A data de fim das inscrições deve ser posterior à data de início.'
                })
        
        # Validação de datas de promoção
        if data_inicio_promocao and data_fim_promocao:
            if data_fim_promocao <= data_inicio_promocao:
                raise forms.ValidationError({
                    'data_fim_promocao': 'A data de fim da promoção deve ser posterior à data de início.'
                })
        
        # Validação de preço promocional
        if preco_promocional and preco:
            if preco_promocional >= preco:
                raise forms.ValidationError({
                    'preco_promocional': 'O preço promocional deve ser menor que o preço normal.'
                })
        
        # Validação de carga horária
        carga_horaria = cleaned_data.get('carga_horaria')
        if carga_horaria and carga_horaria <= 0:
            raise forms.ValidationError({
                'carga_horaria': 'A carga horária deve ser maior que zero.'
            })
        
        # Validação de vagas mínimas
        vagas_minimas = cleaned_data.get('vagas_minimas')
        if vagas_minimas and vagas_minimas <= 0:
            raise forms.ValidationError({
                'vagas_minimas': 'O número de vagas mínimas deve ser maior que zero.'
            })
        
        # Validação de preços
        if preco is not None and preco < 0:
            raise forms.ValidationError({
                'preco': 'O preço não pode ser negativo.'
            })
        
        preco_inscricao = cleaned_data.get('preco_inscricao')
        if preco_inscricao is not None and preco_inscricao < 0:
            raise forms.ValidationError({
                'preco_inscricao': 'A taxa de inscrição não pode ser negativa.'
            })
        
        return cleaned_data

    def clean_instrutores(self):
        instrutores = self.cleaned_data.get('instrutores')
        if not instrutores:
            raise forms.ValidationError('Selecione pelo menos um instrutor.')
        return instrutores

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if titulo and len(titulo.strip()) < 5:
            raise forms.ValidationError('O título deve ter pelo menos 5 caracteres.')
        return titulo.strip()

    def clean_descricao(self):
        descricao = self.cleaned_data.get('descricao')
        if descricao and len(descricao.strip()) < 20:
            raise forms.ValidationError('A descrição deve ter pelo menos 20 caracteres.')
        return descricao.strip()

    def clean_descricao_curta(self):
        descricao_curta = self.cleaned_data.get('descricao_curta')
        if descricao_curta and len(descricao_curta.strip()) < 10:
            raise forms.ValidationError('A descrição curta deve ter pelo menos 10 caracteres.')
        return descricao_curta.strip()