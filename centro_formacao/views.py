from django.shortcuts import render
from django.db.models import Count
from gestoreduka.models import CentroDeFormacao


def home_centro(request):
    query = request.GET.get('q', '')
    provincia = request.GET.get('provincia', '')

    centros = CentroDeFormacao.objects.filter(ativo=True).select_related(
        'perfil'
    ).annotate(
        total_cursos=Count('cursos', distinct=True)
    ).order_by('-perfil__destaque', '-perfil__total_seguidores')

    if query:
        centros = centros.filter(nome__icontains=query)

    if provincia:
        centros = centros.filter(provincia__icontains=provincia)

    # Obter lista de províncias únicas para o filtro
    provincias = CentroDeFormacao.objects.filter(
        ativo=True, provincia__isnull=False
    ).exclude(provincia='').values_list('provincia', flat=True).distinct().order_by('provincia')

    context = {
        'centros': centros,
        'provincias': provincias,
        'query': query,
        'provincia_selecionada': provincia,
        'total_centros': centros.count(),
    }
    return render(request, 'home_centro.html', context)