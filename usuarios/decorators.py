from django.shortcuts import get_object_or_404, redirect
# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.measure import D
from gestoreduka.models import CentroDeFormacao
from usuarios.models import Aluno, PerfilAluno





def aluno_logado_e_centros(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
            return redirect('/auth/login_aluno/?status=4')

        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            return redirect('/auth/login_aluno/?status=4')

        perfil, created = PerfilAluno.objects.get_or_create(aluno=aluno)

        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')

        if latitude and longitude:
            try:
                lat = float(latitude)
                lng = float(longitude)
                from django.contrib.gis.geos import Point
                perfil.localizacao = Point(lng, lat, srid=4326)
                perfil.save()
            except ValueError:
                pass

        centros = []
        if perfil.localizacao:
            from django.conf import settings
            if not getattr(settings, 'USE_SQLITE', False):
                try:
                        from django.contrib.gis.measure import D
                        from django.contrib.gis.db.models.functions import Distance
                        centros = (
                        CentroDeFormacao.objects
                        .filter(
                            ativo=True,
                            localizacao__distance_lte=(perfil.localizacao, D(km=10))
                        )
                        .annotate(distancia=Distance('localizacao', perfil.localizacao))
                        .order_by('distancia')
                    )
                except Exception:
                    centros = CentroDeFormacao.objects.filter(ativo=True).order_by('nome')
            else:
                centros = CentroDeFormacao.objects.filter(ativo=True).order_by('nome')

        request.aluno_obj = aluno
        request.perfil = perfil
        request.centros = centros

        return view_func(request, *args, **kwargs)

    return _wrapped_view
