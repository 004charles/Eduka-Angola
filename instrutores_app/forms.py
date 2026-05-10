from django import forms
from django.contrib.auth import get_user_model
from cursos_app.models import Instrutor
from cursovideoapp.models import Curso_video
from django.utils.translation import gettext_lazy as _

Usuario = get_user_model()

class InstrutorSignupForm(forms.ModelForm):
    nome_completo = forms.CharField(
        label=_("Nome Completo"),
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Seu nome completo', 'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_("E-mail Profissional"),
        widget=forms.EmailInput(attrs={'placeholder': 'seu@email.com', 'class': 'form-control'})
    )
    password = forms.CharField(
        label=_("Senha"),
        widget=forms.PasswordInput(attrs={'placeholder': 'Mínimo 8 caracteres', 'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        label=_("Confirmar Senha"),
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita sua senha', 'class': 'form-control'})
    )
    area_especializacao = forms.ChoiceField(
        choices=Instrutor.TIPO_CHOICES_ESPECIALIZACAO,
        label=_("Área de Especialização"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    biografia = forms.CharField(
        label=_("Biografia Resumida"),
        widget=forms.Textarea(attrs={'placeholder': 'Conte um pouco sobre sua experiência...', 'class': 'form-control', 'rows': 4})
    )

    class Meta:
        model = Instrutor
        fields = ['area_especializacao', 'biografia']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError(_("Este e-mail já está em uso."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(_("As senhas não coincidem."))
        return cleaned_data

    def save(self, commit=True):
        # Criar o usuário desativado
        user = Usuario.objects.create_user(
            email=self.cleaned_data['email'],
            nome=self.cleaned_data['nome_completo'],
            password=self.cleaned_data['password'],
            tipo_usuario='INSTRUTOR',
            is_active=False  # Pendente de aprovação
        )
        
        # Criar o perfil de instrutor
        instrutor = super().save(commit=False)
        instrutor.usuario = user
        instrutor.nome = user.nome
        instrutor.email = user.email
        
        if commit:
            instrutor.save()
        return instrutor

class CursoVideoForm(forms.ModelForm):
    class Meta:
        model = Curso_video
        fields = ['titulo', 'categoria', 'capa', 'descricao', 'is_pago', 'preco']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Django Masterclass'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'O que os alunos vão aprender?'}),
            'capa': forms.FileInput(attrs={'class': 'form-control'}),
            'is_pago': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
        }
from cursovideoapp.models import Curso_video, Aula, MaterialAula

class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['titulo', 'video_url', 'descricao', 'ordem']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da aula'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL do Vídeo (YouTube, etc)'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcional: descrição da aula'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class MaterialAulaForm(forms.ModelForm):
    class Meta:
        model = MaterialAula
        fields = ['titulo', 'arquivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PDF da Aula, Arquivo ZIP'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

from cursovideoapp.models import MaterialCurso

class MaterialCursoForm(forms.ModelForm):
    class Meta:
        model = MaterialCurso
        fields = ['titulo', 'arquivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Apostila Completa, Guia do Curso'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
        }

from cursovideoapp.models import AvisoCurso

class AvisoCursoForm(forms.ModelForm):
    class Meta:
        model = AvisoCurso
        fields = ['titulo', 'mensagem']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assunto do aviso'}),
            'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escreva o comunicado para os alunos...'}),
        }

class InstrutorProfileForm(forms.ModelForm):
    class Meta:
        model = Instrutor
        fields = ['nome', 'titulo', 'area_especializacao', 'biografia', 'foto', 'foto_capa', 'facebook', 'twitter', 'instagram', 'linkedin']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Especialista em UI/UX'}),
            'area_especializacao': forms.Select(attrs={'class': 'form-control'}),
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
            'foto_capa': forms.FileInput(attrs={'class': 'form-control'}),
            'facebook': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://facebook.com/...'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://twitter.com/...'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/...'}),
        }
