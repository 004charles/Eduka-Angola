from django.shortcuts import render, get_object_or_404, redirect
from estagio.models import Estagio, AreaEstagio, InscricaoEstagio
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def estagios_por_area(request, area_slug=None):
    if area_slug:
        area = AreaEstagio.objects.get(slug=area_slug)
        estagios_recomendados = Estagio.objects.filter(
            area=area,
            ativo=True,
            destaque=True
        )[:8]
    else:
        estagios_recomendados = Estagio.objects.filter(
            ativo=True,
            destaque=True
        )[:8]
    
    context = {
        'estagios_recomendados': estagios_recomendados,
    }
    return render(request, 'seu_template.html', context)

def estagio_detalhe(request, slug):
    estagio = get_object_or_404(Estagio, slug=slug, ativo=True)
    
    # Incrementar visualizações
    estagio.visualizacoes += 1
    estagio.save()
    
    ja_candidatou = False
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        aluno = getattr(request.user, 'aluno_profile', None)
        if aluno:
            ja_candidatou = InscricaoEstagio.objects.filter(estagio=estagio, aluno=aluno).exists()
            
    context = {
        'estagio': estagio,
        'ja_candidatou': ja_candidatou,
    }
    return render(request, 'estagio/detalhe_estagio.html', context)

@login_required
def candidatar_estagio(request, slug):
    if request.method == 'POST':
        estagio = get_object_or_404(Estagio, slug=slug, ativo=True)
        aluno = getattr(request.user, 'aluno_profile', None)
        
        if not aluno:
            messages.error(request, "Apenas alunos podem se candidatar a vagas de estágio.")
            return redirect('estagio:estagio_detalhe', slug=slug)
            
        if InscricaoEstagio.objects.filter(estagio=estagio, aluno=aluno).exists():
            messages.warning(request, "Você já se candidatou a este estágio.")
            return redirect('estagio:estagio_detalhe', slug=slug)
            
        carta_motivacao = request.POST.get('carta_motivacao', '')
        curriculo = request.FILES.get('curriculo')
        
        InscricaoEstagio.objects.create(
            estagio=estagio,
            aluno=aluno,
            carta_motivacao=carta_motivacao,
            curriculo=curriculo
        )
        
        messages.success(request, "Sua candidatura foi enviada com sucesso! O centro entrará em contacto.")
        return redirect('estagio:estagio_detalhe', slug=slug)
        
    return redirect('estagio:lista_estagios')

def lista_estagios(request):
    q = request.GET.get('q', '')
    area_id = request.GET.get('area', '')
    modalidade = request.GET.get('modalidade', '')
    
    estagios = Estagio.objects.filter(ativo=True).order_by('-data_publicacao')
    
    if q:
        estagios = estagios.filter(
            Q(titulo__icontains=q) | 
            Q(descricao__icontains=q) | 
            Q(centro_formacao__nome__icontains=q)
        )
        
    if area_id:
        estagios = estagios.filter(area_id=area_id)
        
    if modalidade:
        estagios = estagios.filter(modalidade=modalidade)
        
    areas = AreaEstagio.objects.filter(ativa=True)
    
    context = {
        'estagios': estagios,
        'areas': areas,
        'q': q,
        'area_selecionada': area_id,
        'modalidade_selecionada': modalidade,
        'modalidades': Estagio.MODALIDADE,
    }
    return render(request, 'estagio/lista_estagios.html', context)