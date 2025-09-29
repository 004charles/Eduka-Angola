from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Post, Categoria, Tag
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import models
from core.models import Galeria
from usuarios.models import Aluno
from cursos_app.models import Favorito
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib import messages
from .forms import ComentarioForm
from usuarios.models import CentroSeguimento
from django.shortcuts import render, redirect
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Post, Comentario, ReacaoComentario
from .forms import ComentarioForm
from cursos_app.models import Curso
from django.shortcuts import render
from django.db.models import Q, Count
from django.core.paginator import Paginator

def lista_posts(request):
    query = request.GET.get('q')

    # Lista de posts filtrados
    posts = Post.objects.filter(status='publicado') \
        .select_related('categoria') \
        .prefetch_related('tags')

    imagens = Galeria.objects.all()[:6]


    if query:
        posts = posts.filter(
            Q(titulo__icontains=query) |
            Q(conteudo__icontains=query) |
            Q(categoria__nome__icontains=query) |
            Q(tags__nome__icontains=query)
        ).distinct()

    # Paginação
    paginator = Paginator(posts, 4)  # 4 posts por página
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    # Dados para sidebar
    posts_recentes = Post.objects.filter(status='publicado').order_by('-publicado_em')[:6]
    tags_mais_utilizadas = Tag.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:10]

    # Contexto base
    context = {
        'posts': posts,
        'request': request,
        'posts_recentes': posts_recentes,
        'tags_mais_utilizadas': tags_mais_utilizadas,
        'query': query,
        'imagens': imagens,
        'aluno_logado': False,
        'favoritos': [],
        'centros_seguidos': []
    }

    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            favoritos = Favorito.objects.filter(aluno=aluno).values_list('curso_id', flat=True)
            centros_seguidos = CentroSeguimento.objects.filter(aluno=aluno).values_list('centro_id', flat=True)

            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
                'favoritos': list(favoritos),
                'centros_seguidos': list(centros_seguidos),
            })
        except Aluno.DoesNotExist:
            pass

    return render(request, 'lista_posts.html', context)

from django.shortcuts import render, get_object_or_404
from django.db.models import F
from django.utils import timezone

def detalhe_post(request, slug):
    post = get_object_or_404(Post, slug=slug, status='publicado')

    # Incrementa visualizações
    Post.objects.filter(id=post.id).update(visualizacoes=F('visualizacoes') + 1)
    post.refresh_from_db(fields=['visualizacoes'])

    imagens = Galeria.objects.all()[:6]


    aluno_logado = False
    aluno = None

    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            aluno_logado = True
        except Aluno.DoesNotExist:
            pass

    # PROCESSA ENVIO DE COMENTÁRIO
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.post = post
            comentario.aprovado = True  # ou False se quiser moderação

            # Se o aluno estiver logado, sobrescreve nome e email
            if aluno_logado:
                comentario.nome = aluno.nome
                comentario.email = aluno.email

            # Define parent se for resposta
            parent_id = request.POST.get('parent')
            if parent_id:
                try:
                    comentario.parent = Comentario.objects.get(id=parent_id)
                except Comentario.DoesNotExist:
                    pass

            comentario.save()
            messages.success(request, _('Seu comentário foi enviado!'))
            return redirect('blog:detalhe_post', slug=slug)
    else:
        form = ComentarioForm()

    # Busca comentários apenas deste post
    comentarios = Comentario.objects.filter(
        post=post,
        aprovado=True,
        parent__isnull=True
    ).prefetch_related('reacoes', 'respostas')

    for comentario in comentarios:
        comentario.reacoes_dict = {
            tipo: comentario.reacoes.filter(tipo=tipo).count()
            for tipo, _ in Comentario.REACOES_CHOICES
        }

    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    relacionados = Post.objects.filter(
        categoria=post.categoria, status='publicado'
    ).exclude(id=post.id)[:3]

    context = {
        'post': post,
        'comentarios': comentarios,
        'relacionados': relacionados,
        'form': form,
        'reacoes_choices': Comentario.REACOES_CHOICES,
        'aluno_logado': aluno_logado,
        'imagens': imagens,
        'favoritos': [],
        'centros_seguidos': [],
        'cursos_destaque': cursos_destaque
    }

    if aluno_logado:
        favoritos = Favorito.objects.filter(aluno=aluno).values_list('curso_id', flat=True)
        centros_seguidos = CentroSeguimento.objects.filter(aluno=aluno).values_list('centro_id', flat=True)
        context.update({
            'aluno_nome': aluno.nome,
            'aluno_email': aluno.email,
            'favoritos': list(favoritos),
            'centros_seguidos': list(centros_seguidos),
        })

    return render(request, 'detalhe_post.html', context)


def comentar_post(request, slug):
    post = get_object_or_404(Post, slug=slug, status='publicado')

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.post = post
            comentario.aprovado = True  

            parent_id = request.POST.get('parent')
            if parent_id:
                try:
                    comentario.parent = Comentario.objects.get(id=parent_id, post=post)
                except Comentario.DoesNotExist:
                    comentario.parent = None

            if 'aluno' in request.session:
                try:
                    aluno = Aluno.objects.get(id=request.session['aluno'])
                    comentario.nome = aluno.nome
                    comentario.email = aluno.email
                except Aluno.DoesNotExist:
                    pass

            comentario.save()
            messages.success(request, _('Seu comentário foi enviado com sucesso!'))
        else:
            messages.error(request, _('Erro ao enviar comentário. Verifique os campos.'))

    return redirect('blog:detalhe_post', slug=post.slug)

from django.http import JsonResponse

def reagir_comentario(request, comentario_id, tipo):
    comentario = get_object_or_404(Comentario, id=comentario_id)

    if 'aluno' not in request.session:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Você precisa estar logado para reagir.'}, status=403)
        messages.error(request, _('Você precisa estar logado para reagir.'))
        return redirect('blog:detalhe_post', slug=comentario.post.slug)

    aluno = get_object_or_404(Aluno, id=request.session['aluno'])

    reacao, created = ReacaoComentario.objects.get_or_create(
        comentario=comentario,
        usuario=aluno,
        tipo=tipo
    )

    if not created:
        reacao.delete()
        message = 'Reação removida.'
        status = 'removed'
    else:
        message = 'Reação adicionada!'
        status = 'added'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': status,
            'message': message,
            'total_reactions': comentario.reacoes.count(),
            'reaction_type': tipo
        })

    messages.success(request, _(message))
    return redirect('blog:detalhe_post', slug=comentario.post.slug)




def posts_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    posts = categoria.posts.filter(status='publicado')
    return render(request, 'posts_por_categoria.html', {'categoria': categoria, 'posts': posts})


def posts_por_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.filter(status='publicado')
    return render(request, 'posts_por_tag.html', {'tag': tag, 'posts': posts})


def buscar_posts(request):
    termo = request.GET.get('q', '')
    posts = []
    if termo:
        posts = Post.objects.filter(
            Q(titulo__icontains=termo) |
            Q(conteudo__icontains=termo) |
            Q(categoria__nome__icontains=termo)
        ).filter(status='publicado').distinct()
    return render(request, 'blog/buscar_posts.html', {'termo': termo, 'posts': posts})

def privacidade(request):
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

    return render(request, 'core/privacidade.html', context)