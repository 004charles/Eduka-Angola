from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Escola, CursoEnsinoMedio
# from inteligencia.ai_utils import orientacao_escolar_ia

def onboarding_escolar(request):
    """
    Formulário/Wizard inicial para quem não sabe qual escola escolher.
    """
    if request.method == 'POST':
        # Capturar dados do form
        gostos = request.POST.get('gostos', '')
        notas = request.POST.get('notas', '')
        provincia = request.POST.get('provincia', 'Luanda')
        orcamento = request.POST.get('orcamento', 'Pública')
        nivel = request.POST.get('nivel', '9_classe')

        perfil_dict = {
            'nivel': nivel,
            'gostos': gostos,
            'notas': notas,
            'provincia': provincia,
            'orcamento': orcamento
        }

        # Listar os cursos disponíveis naquela província para contextualizar a IA
        cursos_disponiveis = CursoEnsinoMedio.objects.filter(escola__provincia__icontains=provincia).values_list('nome', flat=True).distinct()
        cursos_str = ", ".join(list(cursos_disponiveis)[:20]) if cursos_disponiveis else "Diversos cursos do Ensino Médio"

        # Chamar a Eduka AI
        resultado_ia = orientacao_escolar_ia(perfil_dict, cursos_str)

        # Salvar na sessão para a página de resultados
        request.session['resultado_orientacao_escolar'] = resultado_ia
        request.session['orientacao_provincia'] = provincia
        
        return redirect('resultado_orientacao')

    return render(request, 'escolas/onboarding.html')


def resultado_orientacao(request):
    """
    Mostra o veredito da IA e as escolas recomendadas na base de dados.
    """
    resultado_ia = request.session.get('resultado_orientacao_escolar')
    provincia = request.session.get('orientacao_provincia', '')

    if not resultado_ia:
        return redirect('onboarding_escolar')

    keywords = resultado_ia.get('keywords', [])
    
    # Query inteligente: Escolas na província que oferecem cursos correspondentes às keywords
    query = Q()
    for kw in keywords:
        query |= Q(cursos__nome__icontains=kw)

    escolas_recomendadas = Escola.objects.filter(ativa=True, provincia__icontains=provincia).filter(query).distinct()[:6]

    # Se a IA sugerir algo que não temos, mostramos as melhores da província de qualquer forma
    if not escolas_recomendadas.exists():
        escolas_recomendadas = Escola.objects.filter(ativa=True, provincia__icontains=provincia).distinct()[:6]

    context = {
        'ia': resultado_ia,
        'escolas': escolas_recomendadas,
        'provincia': provincia
    }
    return render(request, 'escolas/resultado_ia.html', context)


def lista_escolas(request):
    """
    Diretório geral de escolas.
    """
    escolas = Escola.objects.filter(ativa=True).prefetch_related('cursos', 'perfil')
    
    # Simples busca
    q = request.GET.get('q')
    if q:
        escolas = escolas.filter(Q(nome__icontains=q) | Q(municipio__icontains=q) | Q(cursos__nome__icontains=q)).distinct()

    context = {
        'escolas': escolas
    }
    return render(request, 'escolas/lista_escolas.html', context)


def perfil_escola(request, pk):
    """
    Página pública com o perfil completo da escola.
    """
    escola = get_object_or_404(Escola.objects.prefetch_related('cursos', 'galeria', 'perfil'), pk=pk, ativa=True)
    return render(request, 'escolas/perfil_escola.html', {'escola': escola})
