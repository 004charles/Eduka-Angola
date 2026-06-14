# forms.py
from django import forms
from django.utils import timezone
from cursos_app.models import Curso, Categoria, Instrutor
from .models import AnuncioCentro

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
        self.fields['moeda'].help_text = 'Selecione a unidade monetária de cobrança'
        self.fields['preco'].help_text = 'Valor do curso na moeda selecionada. Use 0 para gratuito'
        self.fields['preco_inscricao'].help_text = 'Valor da taxa de inscrição (opcional)'
        self.fields['carga_horaria'].help_text = 'Número de horas do curso'

    class Meta:
        model = Curso
        fields = [
            'titulo', 'descricao', 'descricao_curta', 'nivel', 'idioma', 'categoria',
            'certificado', 'instrutores', 'carga_horaria', 'duracao', 
            'moeda', 'preco', 'preco_inscricao', 'mensalidade', 'tipo_cobranca_inscricao', 'preco_promocional', 
            'data_inicio_promocao', 'data_fim_promocao',
            'modalidade', 'publicado', 'imagem', 'destaque', 'documento_requerido'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'kt-input',
                'placeholder': 'Ex: Curso Completo de Python para Iniciantes',
                'maxlength': '200'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'kt-input',
                'rows': 4,
                'placeholder': 'Descreva detalhadamente o conteúdo, objetivos e benefícios do curso...'
            }),
            'descricao_curta': forms.TextInput(attrs={
                'class': 'kt-input',
                'placeholder': 'Descrição resumida para cards e listagens (máx. 300 caracteres)',
                'maxlength': '300'
            }),
            'nivel': forms.Select(attrs={
                'class': 'kt-select'
            }),
            'idioma': forms.Select(attrs={
                'class': 'kt-select'
            }),
            'categoria': forms.Select(attrs={
                'class': 'kt-select'
            }),
            'modalidade': forms.Select(attrs={
                'class': 'kt-select'
            }),
            'duracao': forms.Select(attrs={
                'class': 'kt-select'
            }),
            'moeda': forms.Select(attrs={
                'class': 'kt-select'
            }),
            'documento_requerido': forms.Select(attrs={
                'class': 'kt-select'
            }),
            'carga_horaria': forms.NumberInput(attrs={
                'class': 'kt-input',
                'placeholder': 'Ex: 40',
                'min': '1',
                'max': '1000'
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'kt-input',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
            'preco_inscricao': forms.NumberInput(attrs={
                'class': 'kt-input',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
            'mensalidade': forms.NumberInput(attrs={
                'class': 'kt-input',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
            'tipo_cobranca_inscricao': forms.Select(attrs={
                'class': 'kt-select'
            }),
            'preco_promocional': forms.NumberInput(attrs={
                'class': 'kt-input',
                'placeholder': '0.000',
                'step': '0.001',
                'min': '0'
            }),
            'data_inicio_promocao': forms.DateTimeInput(attrs={
                'class': 'kt-input',
                'type': 'datetime-local',
            }),
            'data_fim_promocao': forms.DateTimeInput(attrs={
                'class': 'kt-input',
                'type': 'datetime-local',
            }),
            'instrutores': forms.SelectMultiple(attrs={
                'class': 'kt-select',
                'size': '4'
            }),
            'certificado': forms.CheckboxInput(attrs={
                'class': 'kt-checkbox',
                'style': 'width: 18px; height: 18px;'
            }),
            'destaque': forms.CheckboxInput(attrs={
                'class': 'kt-checkbox',
                'style': 'width: 18px; height: 18px;'
            }),
            'publicado': forms.CheckboxInput(attrs={
                'class': 'kt-checkbox',
                'style': 'width: 18px; height: 18px;'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'kt-input',
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
            'moeda': 'Moeda do Curso *',
            'preco': 'Preço Normal *',
            'preco_inscricao': 'Taxa de Inscrição',
            'mensalidade': 'Valor da Mensalidade (opcional)',
            'tipo_cobranca_inscricao': 'O que cobrar online?',
            'preco_promocional': 'Preço Promocional',
            'data_inicio_promocao': 'Início da Promoção',
            'data_fim_promocao': 'Fim da Promoção',
            'modalidade': 'Modalidade *',
            'duracao': 'Duração do Curso *',
            'publicado': 'Publicar Curso?',
            'imagem': 'Imagem de Capa',
            'destaque': 'Destacar este curso?',
            'documento_requerido': 'Documento Requerido para Inscrição *'
        }

    def clean(self):
        cleaned_data = super().clean()
        data_inicio_promocao = cleaned_data.get('data_inicio_promocao')
        data_fim_promocao = cleaned_data.get('data_fim_promocao')
        preco = cleaned_data.get('preco')
        preco_promocional = cleaned_data.get('preco_promocional')
        carga_horaria = cleaned_data.get('carga_horaria')

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
        if carga_horaria and carga_horaria <= 0:
            raise forms.ValidationError({
                'carga_horaria': 'A carga horária deve ser maior que zero.'
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

class AnuncioForm(forms.ModelForm):
    class Meta:
        model = AnuncioCentro
        fields = ['titulo', 'conteudo', 'imagem', 'ativo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'kt-input',
                'placeholder': 'Título impactante do anúncio/comunicado'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'kt-input',
                'rows': 5,
                'placeholder': 'Escreva aqui o conteúdo da novidade que quer partilhar com os seus seguidores...'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'kt-input',
                'accept': 'image/*'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'kt-checkbox',
                'style': 'width: 18px; height: 18px;'
            })
        }
        labels = {
            'titulo': 'Título do Anúncio *',
            'conteudo': 'Conteúdo da Mensagem *',
            'imagem': 'Imagem de Destaque (opcional)',
            'ativo': 'Publicar agora?'
        }

from cursovideoapp.models import Curso_video, Aula

class CursoVideoForm(forms.ModelForm):
    class Meta:
        model = Curso_video
        fields = [
            'titulo', 'descricao', 'categoria', 'is_pago', 'preco', 
            'capa', 'destaque'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'kt-input', 'placeholder': 'Título do Curso'}),
            'descricao': forms.Textarea(attrs={'class': 'kt-input', 'rows': 4}),
            'categoria': forms.Select(attrs={'class': 'kt-select'}),
            'is_pago': forms.CheckboxInput(attrs={'class': 'kt-checkbox', 'style': 'width: 18px; height: 18px;'}),
            'preco': forms.NumberInput(attrs={'class': 'kt-input', 'step': '0.001', 'min': '0'}),
            'capa': forms.FileInput(attrs={'class': 'kt-input', 'accept': 'image/*'}),
            'destaque': forms.CheckboxInput(attrs={'class': 'kt-checkbox', 'style': 'width: 18px; height: 18px;'}),
        }

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['titulo', 'video_url', 'descricao', 'ordem']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'kt-input', 'placeholder': 'Deixe em branco para usar o título do YouTube/Vimeo'}),
            'video_url': forms.URLInput(attrs={'class': 'kt-input', 'placeholder': 'https://youtube.com/watch?v=...'}),
            'descricao': forms.Textarea(attrs={'class': 'kt-input', 'rows': 3}),
            'ordem': forms.NumberInput(attrs={'class': 'kt-input', 'min': '0'}),
        }
