from django.shortcuts import render, get_object_or_404
from estagio.models import Estagio, AreaEstagio
from django.db.models import Q

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
    
    context = {
        'estagio': estagio,
    }
    return render(request, 'estagio/detalhe_estagio.html', context)

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