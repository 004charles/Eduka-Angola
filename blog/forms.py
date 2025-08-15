from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Comentario

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('nome', 'email', 'mensagem')
        labels = {
            'nome': _('Nome'),
            'email': _('E-mail'),
            'mensagem': _('Mensagem'),
        }
        widgets = {
            'mensagem': forms.Textarea(attrs={'rows': 4}),
        }