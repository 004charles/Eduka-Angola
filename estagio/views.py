from django.shortcuts import render
from estagio.models import Estagio, AreaEstagio
from ckeditor.fields import RichTextField

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


from django.shortcuts import render, get_object_or_404
from .models import Estagio

def estagio_detalhe(request, slug):
    estagio = get_object_or_404(Estagio, slug=slug, ativo=True)
    
    # Incrementar visualizações
    estagio.visualizacoes += 1
    estagio.save()
    
    context = {
        'estagio': estagio,
    }
    return render(request, 'estagio/detalhe_estagio.html', context)