from datetime import timedelta

from django.conf import settings
from django.shortcuts import render, redirect
from django.db.models import Count, Q, Prefetch, Value, F
from django.db.models.functions import Coalesce
from django.utils import timezone

from cursos_app.models import Curso, Categoria, Favorito
from usuarios.models import Aluno, PerfilAluno
from usuarios.decorators import aluno_logado_e_centros

from blog.models import Post
from gestoreduka.models import CentroDeFormacao, CentroSeguimento
from cursovideoapp.models import Curso_video, FavoritoCursoVideo
from estagio.models import Estagio

from .models import Galeria, SobreNos
from inteligencia.utils import recomendar_cursos
from avaliacoes.utils import get_centro_da_semana


def index(request):
    """
    Página inicial do portal Edukangola.
    Exibe cursos em destaque, vídeos, posts do blog, estágios e recomendações personalizadas.
    """
    agora = timezone.now()
    proximos_dias = agora + timedelta(days=30)

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
    sobre_nos = SobreNos.objects.last()  

    # Todos os cursos publicados e ativos, ordenados
    todos_cursos = Curso.objects.filter(publicado=True, ativo=True).order_by('-data_inicio_inscricoes')
    cursos_zigue1 = todos_cursos[::2]
    cursos_zigue2 = todos_cursos[1::2]

    # Cursos gratuitos
    cursos_gratuitos = Curso.objects.filter(
        preco=0, publicado=True, ativo=True
    ).order_by('-data_inicio_inscricoes')[:10]

    # Cursos pagos
    cursos_pagos = Curso.objects.filter(
        preco__gt=0, publicado=True, ativo=True
    ).order_by('-data_inicio_inscricoes')[:10]

    # Cursos em promoção
    cursos_promocao = Curso.objects.filter(
        publicado=True, ativo=True,
        preco_promocional__isnull=False
    ).order_by('-data_inicio_inscricoes')[:10]

    # Cursos mais inscritos
    cursos_mais_inscritos = Curso.objects.filter(
        publicado=True, ativo=True
    ).annotate(
        num_inscricoes=Count('inscricoes')
    ).order_by('-num_inscricoes')[:10]

    # Galeria de imagens
    imagens = Galeria.objects.all()[:6]

    # Cursos próximos (a começar nos próximos 30 dias)
    cursos_proximos = Curso.objects.filter(
        publicado=True,
        ativo=True,
        data_inicio__gte=agora,
        data_inicio__lte=proximos_dias
    ).order_by('data_inicio')

    # Cursos para iniciantes (Nível Básico)
    cursos_iniciante = Curso.objects.filter(
        publicado=True,
        ativo=True,
        nivel='B'
    ).select_related('centro').order_by('-visualizacoes')[:10]

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

    # Centros ativos, priorizando os com destaque na home via plano
    centros = CentroDeFormacao.objects.filter(ativo=True).annotate(
        priority_home=Coalesce('assinatura__plano__destaque_home', Value(False))
    ).order_by('-priority_home', 'nome')
    
    # Centro da Semana (IA + Plano)
    centro_semana = get_centro_da_semana()

    # Recomendações de IA
    cursos_recomendados = []
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            cursos_recomendados = recomendar_cursos(aluno, limite=8)
        except AttributeError:
            pass

    # Montagem do contexto
    context = {
        'cursos_destaque': cursos_destaque,
        'cursos_recentes': cursos_recentes,
        'cursos_gratuitos': cursos_gratuitos,
        'cursos_pagos': cursos_pagos,
        'cursos_promocao': cursos_promocao,
        'cursos_mais_inscritos': cursos_mais_inscritos,
        'cursos_proximos': cursos_proximos,
        'cursos_zigue1': cursos_zigue1,
        'cursos_destaque_video': cursos_destaque_video,
        'cursos_iniciante': cursos_iniciante,
        'cursos_zigue2': cursos_zigue2,
        'categorias': categorias,
        'cursos': cursos,
        'posts': posts,
        'centros': centros,
        'imagens': imagens,
        'primeiros_alunos': primeiros_alunos,
        'DEBUG': settings.DEBUG,
        'aluno_logado': request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO',
        'favoritos': [],
        'centros_seguidos': [],
        'sobre': sobre_nos,
        'estagios': estagios,
        'centro_semana': centro_semana,
        'cursos_recomendados': cursos_recomendados
    }

    # Se houver aluno logado
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            favoritos = Favorito.objects.filter(aluno=aluno).values_list('curso_id', flat=True)
            # Add video favorites
            favoritos_video = FavoritoCursoVideo.objects.filter(aluno=aluno).values_list('curso_id', flat=True)
            
            centros_seguidos = list(
                CentroSeguimento.objects.filter(aluno=aluno).values_list('centro_id', flat=True)
            )
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
                'favoritos': list(favoritos),
                'favoritos_video': list(favoritos_video),
                'centros_seguidos': centros_seguidos,
            })
        except AttributeError:
            pass

    return render(request, 'core/index.html', context)




#-------------------------fim homes-----------------------------------------


def erro_404_view(request, exception):
    """
    Exibe uma página personalizada para erros 404 (Página não encontrada).
    """
    context = {
        'aluno_logado': False,
    }

    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except AttributeError:
            pass

    return render(request, '404.html', context, status=404)

def erro_500_view(request):
    """
    Página de erro genérica para falhas internas do servidor (Erro 500).
    """
    """
    Custom 500 error handler.
    """
    context = {}
    return render(request, '500.html', context, status=500)


def sobre(request):
    """
    Apresenta informações sobre a plataforma Edukangola e sua missão.
    """
    imagens = Galeria.objects.all()[:6]

    context = {
        'aluno_logado': False,
        'imagens': imagens,
    }

    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except AttributeError:
            pass

    return render(request, 'core/sobre.html', context)


def privacidade(request):
    """
    Página com os termos de privacidade e uso dos dados dos usuários.
    """
    imagens = Galeria.objects.all()[:6]

    context = {
        'aluno_logado': False,
        'imagens': imagens,

    }
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except AttributeError:
            pass

    return render(request, 'core/privacidade.html', context)