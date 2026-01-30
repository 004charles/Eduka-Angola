# usuarios/forms.py (crie este arquivo)
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from usuarios.models import Comentario

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['avaliacao', 'comentario', 'status_aluno']
        widgets = {
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Compartilhe sua experiência com este curso...'),
                'maxlength': 1000
            }),
            'avaliacao': forms.HiddenInput(),  # Será preenchido via JavaScript
            'status_aluno': forms.HiddenInput(),  # Será preenchido via formulário
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comentario'].label = _('Seu Comentário')
        self.fields['comentario'].required = True
        
    def clean_comentario(self):
        comentario = self.cleaned_data.get('comentario')
        if len(comentario.strip()) < 10:
            raise ValidationError(_('O comentário deve ter pelo menos 10 caracteres.'))
        return comentario

class RespostaForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['resposta']
        widgets = {
            'resposta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Digite sua resposta aqui...'),
                'maxlength': 1000
            })
        }