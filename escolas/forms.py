from django import forms
from .models import Escola, PerfilEscola


class EscolaAdminForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = [
            'nome', 'tipo_rede', 'provincia', 'municipio', 'endereco',
            'categorias', 'telefone', 'email', 'site', 'mensalidade_base',
            'ativa'
        ]
        widgets = {
            'categorias': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.CheckboxInput, forms.ClearableFileInput, forms.FileInput)):
                field.widget.attrs.setdefault('class', 'form-control')
            if field.required:
                field.widget.attrs.setdefault('required', 'required')


class PerfilEscolaAdminForm(forms.ModelForm):
    class Meta:
        model = PerfilEscola
        fields = [
            'logo', 'banner', 'video_banner', 'video_banner_url', 
            'descricao', 'foto_historia', 'missao', 'foto_missao', 'visao', 'foto_visao',
            'ano_fundacao', 'diretor', 'facebook', 'instagram', 'linkedin',
            'whatsapp', 'verificada', 'inscricoes_abertas', 'prazo_inscricoes',
            'requisitos_inscricao', 'infraestruturas'
        ]
        widgets = {
            'infraestruturas': forms.CheckboxSelectMultiple(),
            'descricao': forms.Textarea(attrs={'rows': 8, 'class': 'pf-input', 'placeholder': 'Conte a história da escola, quando foi fundada, qual a sua missão...'}),
            'missao': forms.Textarea(attrs={'rows': 5, 'class': 'pf-input', 'placeholder': 'Descreva o propósito e os objectivos fundamentais da escola...'}),
            'visao': forms.Textarea(attrs={'rows': 5, 'class': 'pf-input', 'placeholder': 'Descreva aonde a escola quer chegar e qual é o seu ideal de futuro...'}),
            'requisitos_inscricao': forms.Textarea(attrs={'rows': 5, 'class': 'pf-input', 'placeholder': 'Ex: Cópia do BI, 4 Fotografias tipo passe, Certidão de Habilitações...'}),
            'video_banner_url': forms.URLInput(attrs={'class': 'pf-input', 'placeholder': 'https://exemplo.com/video.mp4'}),
            'facebook': forms.URLInput(attrs={'placeholder': 'https://facebook.com/sua-escola'}),
            'instagram': forms.URLInput(attrs={'placeholder': 'https://instagram.com/sua-escola'}),
            'linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/company/sua-escola'}),
            'whatsapp': forms.TextInput(attrs={'placeholder': '+244 923 123 456'}),
            'diretor': forms.TextInput(attrs={'class': 'pf-input', 'placeholder': 'Nome completo do(a) diretor(a)'}),
            'ano_fundacao': forms.NumberInput(attrs={'class': 'pf-input', 'placeholder': 'Ex: 1985', 'min': '1900', 'max': '2030'}),
            'prazo_inscricoes': forms.DateInput(attrs={'class': 'pf-input', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.CheckboxInput, forms.ClearableFileInput, forms.FileInput)):
                field.widget.attrs.setdefault('class', 'pf-input')
            if field.required and field_name not in ['logo', 'banner', 'foto_historia', 'foto_missao', 'foto_visao', 'facebook', 'instagram', 'linkedin', 'whatsapp', 'prazo_inscricoes', 'video_banner', 'video_banner_url']:
                field.widget.attrs.setdefault('required', 'required')
