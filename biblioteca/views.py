from django.shortcuts import render
from biblioteca.models import Livro, CategoriaLivro
from django.db.models import Count



def biblioteca(request):
    """View para livros em destaque"""
    # Filtra livros disponíveis e ordena por popularidade
    livros_destaque = Livro.objects.filter(
        status='disponivel',
        estoque__gt=0
    ).select_related('autor', 'biblioteca_proprietaria').prefetch_related('categorias')[:8]

    categorias = CategoriaLivro.objects.annotate(
        total_livros=Count('livros')
    ).filter(total_livros__gt=0).order_by('-total_livros')[:10] 


    livros_principais = Livro.objects.mais_populares(limite=8)
    livros_promocao = Livro.objects.em_promocao(limite=6)
    livros_recentes = Livro.objects.mais_recentes(limite=6)
    livros_melhor_avaliados = Livro.objects.melhor_avaliados(limite=6)
    livros_gratuitos = Livro.objects.gratuitos(limite=4)

    
    context = {
        'livros_destaque': livros_destaque,
        'categorias': categorias,
        'livros_principais': livros_principais,
        'livros_promocao': livros_promocao,
        'livros_recentes': livros_recentes,
        'livros_melhor_avaliados': livros_melhor_avaliados,
        'livros_gratuitos': livros_gratuitos,
    }
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Se for requisição AJAX, retorna JSON
        livros_data = []
        for livro in livros_destaque:
            livros_data.append({
                'id': livro.id,
                'titulo': livro.titulo,
                'autor': livro.autor.nome,
                'capa_url': livro.capa.url if livro.capa else '',
                'preco': str(livro.preco_atual),
                'preco_original': str(livro.preco) if livro.em_promocao else None,
                'desconto_percentual': livro.desconto_percentual if livro.em_promocao else 0,
                'avaliacao_media': livro.avaliacao_media,
                'total_avaliacoes': livro.total_avaliacoes,
                'e_gratuito': livro.e_gratuito,
                'tem_amostra': livro.tem_amostra,
                'url_detalhes': f"/livros/{livro.id}/",
            })
        return JsonResponse({'livros': livros_data})
    
    return render(request, 'biblioteca.html', context)

def livro_detalhes(request, livro_id):
    """Detalhes de um livro específico"""
    livro = get_object_or_404(
        Livro.objects.select_related('autor', 'biblioteca_proprietaria')
                     .prefetch_related('categorias'),
        id=livro_id,
        status='disponivel'
    )
    
    # Incrementa visualizações
    livro.visualizacoes += 1
    livro.save(update_fields=['visualizacoes'])
    
    # Livros relacionados (mesma categoria)
    livros_relacionados = Livro.objects.filter(
        categorias__in=livro.categorias.all(),
        status='disponivel'
    ).exclude(id=livro.id).distinct()[:4]
    
    context = {
        'livro': livro,
        'livros_relacionados': livros_relacionados,
    }
    return render(request, 'biblioteca/livro_detalhes.html', context)

def livros_por_categoria(request, categoria_id):
    """Lista livros por categoria"""
    categoria = get_object_or_404(CategoriaLivro, id=categoria_id, ativo=True)
    livros = Livro.objects.filter(
        categorias=categoria,
        status='disponivel',
        estoque__gt=0
    ).select_related('autor', 'biblioteca_proprietaria')
    
    context = {
        'categoria': categoria,
        'livros': livros,
    }
    return render(request, 'biblioteca/livros_categoria.html', context)

def pesquisar_livros(request):
    """Pesquisa de livros"""
    query = request.GET.get('q', '')
    livros = Livro.objects.filter(
        status='disponivel',
        estoque__gt=0
    )
    
    if query:
        livros = livros.filter(
            models.Q(titulo__icontains=query) |
            models.Q(autor__nome__icontains=query) |
            models.Q(descricao__icontains=query)
        )
    
    context = {
        'livros': livros,
        'query': query,
    }
    return render(request, 'biblioteca/pesquisa.html', context)

