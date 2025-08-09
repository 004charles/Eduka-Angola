from django.shortcuts import render, redirect
from cursos_app.models import Curso, Categoria, Aluno, Favorito
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Count, Q
from django.utils import timezone
from gestoreduka.models import CentroDeFormacao
from datetime import timedelta
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.conf import settings
from usuarios.models import CentroSeguimento, PerfilAluno
from django.utils import timezone
from datetime import timedelta

def index(request):
    agora = timezone.now()
    proximos_dias = agora + timedelta(days=7)

    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    cursos_recentes = list(
        Curso.objects.filter(publicado=True, ativo=True)
        .order_by('-data_inicio')[:20]
    )

    todos_cursos = Curso.objects.filter(publicado=True, ativo=True).order_by('-data_inicio')
    cursos_zigue1 = todos_cursos[::2]
    cursos_zigue2 = todos_cursos[1::2]

    cursos_gratuitos = Curso.objects.filter(
        preco=0, publicado=True, ativo=True
    ).order_by('-data_inicio')[:10]

    cursos_proximos = Curso.objects.filter(
        publicado=True,
        ativo=True,
        data_inicio__gte=agora,
        data_inicio__lte=proximos_dias
    ).order_by('data_inicio')

    categorias = Categoria.objects.annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
    )
    primeiros_alunos = PerfilAluno.objects.filter(
    foto_de_perfil__isnull=False
).exclude(foto_de_perfil='').order_by('aluno__data_cadastro')[:3]

    centros = CentroDeFormacao.objects.filter(ativo=True)

    context = {
        'cursos_destaque': cursos_destaque,
        'cursos_recentes': cursos_recentes,
        'cursos_gratuitos': cursos_gratuitos,
        'cursos_proximos': cursos_proximos,
        'cursos_zigue1': cursos_zigue1,
        'cursos_zigue2': cursos_zigue2,
        'categoria': categorias,
        'centros': centros,
        'primeiros_alunos': primeiros_alunos,
        'DEBUG': settings.DEBUG,
        'aluno_logado': False,
        'favoritos': [],
        'centros_seguidos': [],
    }

    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            favoritos = Favorito.objects.filter(aluno=aluno).values_list('curso_id', flat=True)
            centros_seguidos = list(
                CentroSeguimento.objects.filter(aluno=aluno).values_list('centro_id', flat=True)
            )
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
                'favoritos': list(favoritos),
                'centros_seguidos': centros_seguidos,
            })
        except Aluno.DoesNotExist:
            pass

    return render(request, 'core/index.html', context)

def erro_404_view(request, exception):
    context = {
        'aluno_logado': False,
    }

    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except Aluno.DoesNotExist:
            pass

    return render(request, '404.html', context, status=404)


def sobre(request):
    context = {
        'aluno_logado': False,
    }

    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except Aluno.DoesNotExist:
            pass

    return render(request, 'core/sobre.html', context)