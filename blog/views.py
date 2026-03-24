from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, F
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from .models import Post, Categoria, Tag, Comentario, ReacaoComentario
from .forms import ComentarioForm

from core.models import Galeria
from usuarios.models import Aluno
from gestoreduka.models import CentroSeguimento
from cursos_app.models import Favorito, Curso


def lista_posts(request):
    """
    Lista todos os artigos do blog com suporte a pesquisa, filtragem e paginação.
    """
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

    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            favoritos = Favorito.objects.filter(aluno=aluno).values_list('curso_id', flat=True)
            centros_seguidos = CentroSeguimento.objects.filter(aluno=aluno).values_list('centro_id', flat=True)

            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
                'favoritos': list(favoritos),
                'centros_seguidos': list(centros_seguidos),
            })
        except AttributeError:
            pass

    return render(request, 'lista_posts.html', context)


def detalhe_post(request, slug):
    """
    Exibe o conteúdo completo de um artigo, seus comentários e posts relacionados.
    """
    post = get_object_or_404(Post, slug=slug, status='publicado')

    # Incrementa visualizações
    Post.objects.filter(id=post.id).update(visualizacoes=F('visualizacoes') + 1)
    post.refresh_from_db(fields=['visualizacoes'])

    imagens = Galeria.objects.all()[:6]


    aluno_logado = request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO'
    aluno = None

    if aluno_logado:
        try:
            aluno = request.user.aluno_profile
        except AttributeError:
            aluno_logado = False

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
                comentario.email = request.user.email

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
            'aluno_email': request.user.email,
            'favoritos': list(favoritos),
            'centros_seguidos': list(centros_seguidos),
        })

    return render(request, 'detalhe_post.html', context)


def comentar_post(request, slug):
    """
    Processa a submissão de um novo comentário em um artigo do blog.
    """
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

            if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
                try:
                    aluno = request.user.aluno_profile
                    comentario.aluno = aluno
                    comentario.nome = aluno.nome
                    comentario.email = request.user.email
                except AttributeError:
                    pass

            comentario.save()
            messages.success(request, _('Seu comentário foi enviado com sucesso!'))
        else:
            messages.error(request, _('Erro ao enviar comentário. Verifique os campos.'))

    return redirect('blog:detalhe_post', slug=post.slug)

from django.http import JsonResponse

def reagir_comentario(request, comentario_id, tipo):
    """
    Permite que usuários logados reajam (curtir, etc.) a comentários.
    """
    comentario = get_object_or_404(Comentario, id=comentario_id)

    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Você precisa estar logado para reagir.'}, status=403)
        messages.error(request, _('Você precisa estar logado para reagir.'))
        return redirect('blog:detalhe_post', slug=comentario.post.slug)

    try:
        aluno = request.user.aluno_profile
    except AttributeError:
        return redirect('blog:detalhe_post', slug=comentario.post.slug)

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
    """
    Filtra e exibe artigos pertencentes a uma categoria específica.
    """
    categoria = get_object_or_404(Categoria, slug=slug)
    posts = categoria.posts.filter(status='publicado')
    return render(request, 'posts_por_categoria.html', {'categoria': categoria, 'posts': posts})


def posts_por_tag(request, slug):
    """
    Filtra e exibe artigos que possuem uma tag específica.
    """
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.filter(status='publicado')
    return render(request, 'posts_por_tag.html', {'tag': tag, 'posts': posts})


def buscar_posts(request):
    """
    Realiza a busca de artigos baseada em um termo fornecido pelo usuário.
    """
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