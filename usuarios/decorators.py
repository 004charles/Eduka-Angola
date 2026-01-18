from django.shortcuts import get_object_or_404, redirect
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from gestoreduka.models import CentroDeFormacao
from usuarios.models import Aluno, PerfilAluno





def aluno_logado_e_centros(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'aluno' not in request.session:
            return redirect('/auth/Login_aluno?status=4')

        aluno = get_object_or_404(Aluno, id=request.session['aluno'])
        perfil, created = PerfilAluno.objects.get_or_create(aluno=aluno)

        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')

        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)
                perfil.localizacao = Point(lng, lat, srid=4326)
                perfil.save()
            except ValueError:
                pass

        centros = []
        if perfil.localizacao:
            centros = (
                CentroDeFormacao.objects
                .filter(
                    ativo=True,
                    localizacao__distance_lte=(perfil.localizacao, D(km=10))
                )
                .annotate(distancia=Distance('localizacao', perfil.localizacao))
                .order_by('distancia')
            )

        request.aluno_obj = aluno
        request.perfil = perfil
        request.centros = centros

        return view_func(request, *args, **kwargs)

    return _wrapped_view
