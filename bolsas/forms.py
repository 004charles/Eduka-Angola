from django import forms
from .models import CandidaturaBolsa

class CandidaturaBolsaForm(forms.ModelForm):
    class Meta:
        model = CandidaturaBolsa
        fields = ['curso_pretendido', 'justificativa', 'renda_familiar', 'documento_comprovativo']
        widgets = {
            'curso_pretendido': forms.Select(attrs={'class': 'form-select rbt-radius'}),
            'justificativa': forms.Textarea(attrs={'class': 'form-control rbt-radius', 'rows': 4, 'placeholder': 'Explique por que você merece esta bolsa...'}),
            'renda_familiar': forms.NumberInput(attrs={'class': 'form-control rbt-radius', 'placeholder': 'Ex: 50000'}),
            'documento_comprovativo': forms.FileInput(attrs={'class': 'form-control rbt-radius'}),
        }
