from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Post, Categoria, Tag
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import models

def lista_posts(request):
    query = request.GET.get('q')
    posts = Post.objects.filter(status='publicado').select_related('categoria').prefetch_related('tags')
    
    if query:
        posts = posts.filter(
            Q(titulo__icontains=query) |
            Q(conteudo__icontains=query) |
            Q(categoria__nome__icontains=query) |
            Q(tags__nome__icontains=query)
        ).distinct()
    
    # Paginação
    paginator = Paginator(posts, 4)  # 6 posts por página
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Dados para sidebar
    posts_recentes = Post.objects.filter(status='publicado').order_by('-publicado_em')[:6]
    tags_mais_utilizadas = Tag.objects.annotate(num_posts=models.Count('posts')).order_by('-num_posts')[:10]
    
    context = {
        'posts': posts,
        'request': request,
        'posts_recentes': posts_recentes,
        'tags_mais_utilizadas': tags_mais_utilizadas,
        'query': query
    }
    return render(request, 'lista_posts.html', context)

def detalhe_post(request, slug):
    post = get_object_or_404(Post, slug=slug, status='publicado')

    # Contador de visualizações
    post.visualizacoes += 1
    post.save(update_fields=['visualizacoes'])

    comentarios = post.comentarios.filter(aprovado=True)
    relacionados = Post.objects.filter(
        categoria=post.categoria, status='publicado'
    ).exclude(id=post.id)[:3]

    return render(request, 'blog/detalhe_post.html', {
        'post': post,
        'request': request,
        'comentarios': comentarios,
        'relacionados': relacionados
    })


def posts_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    posts = categoria.posts.filter(status='publicado')
    return render(request, 'blog/posts_por_categoria.html', {'categoria': categoria, 'posts': posts})


def posts_por_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.filter(status='publicado')
    return render(request, 'blog/posts_por_tag.html', {'tag': tag, 'posts': posts})


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
