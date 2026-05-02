from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance
# from django.contrib.gis.measure import D
from django.core.exceptions import ObjectDoesNotExist
from gestoreduka.models import CentroDeFormacao
from usuarios.models import Aluno, PerfilAluno





def aluno_logado_e_centros(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
            return redirect(f'/auth/login_aluno/?status=4&next={request.path}')

        # Tentativa de obter ou criar o perfil de Aluno caso falte
        try:
            aluno = request.user.aluno_profile
        except (AttributeError, Aluno.DoesNotExist, ObjectDoesNotExist):
            # Se é um usuário do tipo ALUNO mas não tem o objeto Aluno, criamos agora
            aluno, created = Aluno.objects.get_or_create(
                usuario=request.user,
                defaults={
                    'nome': request.user.nome or request.user.email,
                    'ativo': True
                }
            )
        
        if not aluno:
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

        # Prioridade 1: Onboarding (Interesses e Nível)
        if not perfil.onboarding_completo and request.path != reverse('aluno_onboarding'):
            return redirect('aluno_onboarding')

        # Restrição de Documentos Removida a pedido do utilizador
        pass

        return view_func(request, *args, **kwargs)

    return _wrapped_view
