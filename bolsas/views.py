from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from cursos_app.models import Curso
from gestoreduka.models import ModuloPublico
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


def _bolsas_activas():
    return ModuloPublico.objects.filter(chave=ModuloPublico.BOLSAS, ativo=True).exists()


@require_http_methods(['GET', 'POST'])
def react_bolsas(request):
    """Página e candidatura React de Bolsas, disponível somente quando o módulo estiver activo."""
    if not _bolsas_activas():
        return JsonResponse({'detail': 'O módulo de Bolsas não está disponível neste momento.'}, status=404)

    if request.method == 'GET':
        candidaturas = []
        if request.user.is_authenticated and getattr(request.user, 'tipo_usuario', '') == 'ALUNO':
            aluno = getattr(request.user, 'aluno_profile', None)
            if aluno:
                candidaturas = [
                    {
                        'id': item.id,
                        'curso': item.curso_pretendido.titulo,
                        'status': item.get_status_display(),
                        'data': item.data_candidatura.isoformat(),
                        'feedback': item.feedback_admin,
                    }
                    for item in CandidaturaBolsa.objects.filter(aluno=aluno).select_related('curso_pretendido')[:8]
                ]
        cursos = Curso.objects.filter(publicado=True, ativo=True).order_by('titulo').values('id', 'titulo', 'moeda', 'preco')[:200]
        return JsonResponse({'titulo': 'Bolsas de estudo', 'descricao': 'Candidate-se a apoio para continuar a sua formação.', 'cursos': list(cursos), 'candidaturas': candidaturas})

    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Entre na sua conta de aluno para enviar uma candidatura.'}, status=401)
    if getattr(request.user, 'tipo_usuario', '') != 'ALUNO':
        return JsonResponse({'detail': 'Apenas alunos podem candidatar-se a bolsas.'}, status=403)
    aluno = getattr(request.user, 'aluno_profile', None)
    if not aluno:
        return JsonResponse({'detail': 'O perfil de aluno não está disponível.'}, status=403)
    form = CandidaturaBolsaForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse({'detail': 'Verifique os campos obrigatórios da candidatura.', 'errors': form.errors.get_json_data()}, status=400)
    candidatura = form.save(commit=False)
    candidatura.aluno = aluno
    candidatura.save()
    return JsonResponse({'ok': True, 'message': 'A candidatura foi enviada. A equipa responsável entrará em contacto após a análise.', 'candidatura': {'id': candidatura.id, 'status': candidatura.get_status_display()}}, status=201)
