from django.shortcuts import render, redirect
from cursos_app.models import Curso, Categoria, Aluno, Favorito
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Count, Q
from django.db.models import Prefetch, Q, Count
from django.utils import timezone
from .models import Galeria
from blog.models import Post
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
from cursovideoapp.models import Curso_video
from .models import SobreNos
from estagio.models import Estagio


def index(request):
    agora = timezone.now()
    proximos_dias = agora + timedelta(days=7)

    # Cursos em destaque
    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    # Cursos de vídeo
    cursos = Curso_video.objects.all()[:5]
    cursos_destaque_video = Curso_video.objects.filter(destaque=True)

    # Posts do blog
    posts = Post.objects.filter(status='publicado') \
        .select_related('categoria') \
        .prefetch_related('tags')

    # Cursos recentes (ordenados pela data de início das inscrições)
    cursos_recentes = list(
        Curso.objects.filter(publicado=True, ativo=True)
        .order_by('-data_inicio_inscricoes')[:20]
    )

    # Estágios ativos
    estagios = Estagio.objects.filter(ativo=True).select_related('area', 'centro_formacao')

    # Sobre nós
    sobre = SobreNos.objects.last()  

    # Todos os cursos publicados e ativos, ordenados
    todos_cursos = Curso.objects.filter(publicado=True, ativo=True).order_by('-data_inicio_inscricoes')
    cursos_zigue1 = todos_cursos[::2]
    cursos_zigue2 = todos_cursos[1::2]

    # Cursos gratuitos
    cursos_gratuitos = Curso.objects.filter(
        preco=0, publicado=True, ativo=True
    ).order_by('-data_inicio_inscricoes')[:10]

    # Galeria de imagens
    imagens = Galeria.objects.all()[:6]

    # Cursos próximos (a começar nos próximos 7 dias)
    cursos_proximos = Curso.objects.filter(
        publicado=True,
        ativo=True,
        data_inicio_inscricoes__gte=agora,
        data_inicio_inscricoes__lte=proximos_dias
    ).order_by('data_inicio_inscricoes')

    # Categorias com cursos publicados e ativos
    categorias = Categoria.objects.prefetch_related(
        Prefetch(
            'curso',
            queryset=Curso.objects.filter(publicado=True, ativo=True).select_related('centro'),
            to_attr='cursos_ativos'
        )
    ).annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
    ).filter(num_cursos__gt=0)

    # Primeiros alunos com foto de perfil
    primeiros_alunos = PerfilAluno.objects.filter(
        foto_de_perfil__isnull=False
    ).exclude(foto_de_perfil='').order_by('aluno__data_cadastro')[:3]

    # Centros ativos
    centros = CentroDeFormacao.objects.filter(ativo=True)

    # Montagem do contexto
    context = {
        'cursos_destaque': cursos_destaque,
        'cursos_recentes': cursos_recentes,
        'cursos_gratuitos': cursos_gratuitos,
        'cursos_proximos': cursos_proximos,
        'cursos_zigue1': cursos_zigue1,
        'cursos_destaque_video': cursos_destaque_video,
        'cursos_zigue2': cursos_zigue2,
        'categorias': categorias,
        'cursos': cursos,
        'posts': posts,
        'centros': centros,
        'imagens': imagens,
        'primeiros_alunos': primeiros_alunos,
        'DEBUG': settings.DEBUG,
        'aluno_logado': False,
        'favoritos': [],
        'centros_seguidos': [],
        'sobre': sobre,
        'estagios': estagios
    }

    # Se houver aluno logado na sessão
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
    imagens = Galeria.objects.all()[:6]

    context = {
        'aluno_logado': False,
        'imagens': imagens,
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


def privacidade(request):
    imagens = Galeria.objects.all()[:6]

    context = {
        'aluno_logado': False,
        'imagens': imagens,

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

    return render(request, 'core/privacidade.html', context)