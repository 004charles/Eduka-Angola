from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CandidaturaBolsaForm
from .models import CandidaturaBolsa

@login_required
def candidatar_bolsa(request):
    """
    View para processar a candidatura de um aluno a uma bolsa.
    """
    if request.user.tipo_usuario != 'ALUNO':
        messages.error(request, "Apenas alunos podem candidatar-se a bolsas.")
        return redirect('index')

    try:
        aluno = request.user.aluno_profile
    except AttributeError:
        messages.error(request, "Perfil de aluno não encontrado.")
        return redirect('index')

    if request.method == 'POST':
        form = CandidaturaBolsaForm(request.POST, request.FILES)
        if form.is_valid():
            candidatura = form.save(commit=False)
            candidatura.aluno = aluno
            candidatura.save()
            messages.success(request, "Sua candidatura foi enviada com sucesso! Nossa equipe analisará e entrará em contato.")
            return redirect('index')
        else:
            messages.error(request, "Houve um erro no preenchimento do formulário. Verifique os dados e tente novamente.")
    else:
        form = CandidaturaBolsaForm()

    return render(request, 'bolsas/candidatar.html', {'form': form})
