from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import ConviteCentro



def centro_dashboard(request):
    return render(request, 'centro_dashboard.html')


User = get_user_model()

def confirmar_cadastro(request, token):
    convite = get_object_or_404(ConviteCentro, token=token, usado=False)

    if request.method == "POST":
        senha = request.POST.get("senha")
        nome = request.POST.get("nome")

        user, created = User.objects.get_or_create(
            email=convite.centro.email,
            defaults={
                "nome": nome,
                "password": senha, 
            },
        )

        if not created:
            user.nome = nome
            user.set_password(senha)
            user.save()

        convite.centro.ativo = True
        convite.centro.save()

        convite.usado = True
        convite.save()

        messages.success(request, "Cadastro concluído! Agora você pode fazer login.")
        return redirect("login_gestor")

    return render(request, "confirmar_cadastro.html", {"convite": convite})


from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model

User = get_user_model()

def login_gestor(request):
    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")

        # autentica usando o campo USERNAME_FIELD (email)
        user = authenticate(request, username=email, password=senha)

        if user is not None:
            if user.is_active:  # garante que a conta está ativa
                login(request, user)
                messages.success(request, f"Bem-vindo, {user.get_full_name()}!")
                return redirect("centro_dashboard")  # redireciona para dashboard
            else:
                messages.error(request, "Sua conta está desativada. Contate o administrador.")
        else:
            messages.error(request, "E-mail ou senha inválidos.")

    return render(request, "login_gestor.html")
