from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Skill, Vaga, Empresa, CandidaturaVaga
from .utils import get_skill_gap, sugerir_cursos_para_gap

@login_required
def candidatar_vaga(request, slug):
    """
    Processa a candidatura de um aluno a uma vaga.
    """
    if request.method == 'POST':
        vaga = get_object_or_404(Vaga, slug=slug)
        aluno = getattr(request.user, 'aluno_profile', None)
        
        if not aluno:
            messages.error(request, "Apenas alunos podem se candidatar a vagas.")
            return redirect('carreira:job_detail', slug=slug)
            
        # Verificar se já se candidatou
        if CandidaturaVaga.objects.filter(vaga=vaga, aluno=aluno).exists():
            messages.warning(request, "Você já se candidatou a esta vaga.")
            return redirect('carreira:job_detail', slug=slug)
            
        mensagem = request.POST.get('mensagem', '')
        
        candidatura = CandidaturaVaga.objects.create(
            vaga=vaga,
            aluno=aluno,
            mensagem=mensagem
        )
        
        messages.success(request, "Candidatura enviada com sucesso! Boa sorte.")
        return redirect('carreira:job_detail', slug=slug)
        
    return redirect('carreira:job_board')

def job_board(request):
    """
    Listagem de vagas de emprego.
    """
    vagas = Vaga.objects.filter(status='ABERTA').select_related('empresa').prefetch_related('competencias_exigidas')
    
    tipo = request.GET.get('tipo')
    if tipo:
        vagas = vagas.filter(tipo=tipo)
        
    context = {
        'vagas': vagas,
    }
    return render(request, 'carreira/job_board.html', context)

def job_detail(request, slug):
    """
    Detalhes de uma vaga específica com análise de match.
    """
    vaga = get_object_or_404(Vaga, slug=slug)
    aluno = getattr(request.user, 'aluno_profile', None)
    
    ja_candidatou = False
    skill_gap = []
    sugestoes = {}
    
    if aluno:
        ja_candidatou = CandidaturaVaga.objects.filter(vaga=vaga, aluno=aluno).exists()
        skill_gap = get_skill_gap(aluno, vaga)
        sugestoes = sugerir_cursos_para_gap(aluno, skill_gap)
    
    context = {
        'vaga': vaga,
        'ja_candidatou': ja_candidatou,
        'skill_gap': skill_gap,
        'sugestoes': sugestoes,
    }
    return render(request, 'carreira/job_detail.html', context)
