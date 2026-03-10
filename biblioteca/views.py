from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Livro, CategoriaLivro, Biblioteca
from usuarios.models import Usuario



def biblioteca(request):
    """
    Lista todos os livros disponíveis na biblioteca com opções de filtragem.
    """
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
    """
    Exibe informações detalhadas de um livro específico.
    """
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
    """
    Filtra a coleção da biblioteca por uma categoria específica.
    """
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
    """
    Pesquisa livros por título ou autor.
    """
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


# --- Library Authentication & Registration ---

def login_biblioteca(request):
    """
    Renderiza a página de login específica para bibliotecas.
    """
    return render(request, 'login_biblioteca.html')

def registro_biblioteca(request):
    """
    Renderiza a página de registro de biblioteca.
    """
    return render(request, 'cadastro_biblioteca.html')

def valida_cadastro_biblioteca(request):
    """
    Processa o formulário de registro de biblioteca. Cria Usuario e perfil de Biblioteca.
    """
    if request.method != 'POST':
        return redirect('login_biblioteca')
    
    try:
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        telefone = request.POST.get('telefone')
        codigo_registro = request.POST.get('codigo_registro', '').strip()
        tipo = request.POST.get('tipo')

        if not all([nome, email, senha, confirmar_senha, tipo]):
            return redirect('/biblioteca/login/?status=1')

        if len(senha) < 8:
            return redirect('/biblioteca/login/?status=2')

        if senha != confirmar_senha:
            return redirect('/biblioteca/login/?status=5')

        if Usuario.objects.filter(email=email).exists():
            return redirect('/biblioteca/login/?status=3')

        if codigo_registro and Biblioteca.objects.filter(codigo_registro=codigo_registro).exists():
            return redirect('/biblioteca/login/?status=7')

        # Create Usuario
        usuario = Usuario.objects.create_user(
            email=email,
            nome=nome,
            password=senha,
            tipo_usuario='BIBLIOTECA'
        )

        # Create Biblioteca profile
        biblioteca_obj = Biblioteca.objects.create(
            usuario=usuario,
            nome=nome,
            telefone=telefone,
            codigo_registro=codigo_registro if codigo_registro else None,
            tipo=tipo
        )

        enviar_email_boas_vindas_biblioteca(nome, email, tipo)
        return redirect('/biblioteca/login/?status=0')
    
    except Exception as e:
        print(f"Erro inesperado no cadastro de biblioteca: {e}")
        return redirect('/biblioteca/login/?status=4')

def enviar_email_boas_vindas_biblioteca(nome, email, tipo):
    """
    Sends a welcome email upon successful library registration.
    """
    assunto = f"Bem-vindo à EdukAngola, {nome}!"
    tipo_map = {
        'PUBLICA': 'Pública',
        'ESCOLAR': 'Escolar',
        'UNIVERSITARIA': 'Universitária',
        'ESPECIALIZADA': 'Especializada',
        'COMUNITARIA': 'Comunitária'
    }
    tipo_display = tipo_map.get(tipo, tipo)
    
    contexto = {
        'nome': nome,
        'tipo': tipo_display,
        'plataforma': 'EdukAngola',
        'cor_primaria': '#333333',
        'cor_secundaria': '#000000',
    }
    
    html_content = render_to_string('boas_vindas_biblioteca.html', contexto)
    text_content = strip_tags(html_content)
    
    email_msg = EmailMultiAlternatives(
        subject=assunto,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    email_msg.attach_alternative(html_content, "text/html")
    
    try:
        email_msg.send()
    except Exception as e:
        print(f"Erro ao enviar e-mail para biblioteca: {e}")

def valida_login_biblioteca(request):
    """
    Lida com a autenticação de bibliotecas usando o sistema central.
    """
    if request.method != 'POST':
        return redirect('login_biblioteca')
    
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    
    if not email or not senha:
        return redirect('/biblioteca/login/?status=1')
    
    try:
        user = authenticate(request, username=email, password=senha)
        
        if user is not None:
            if user.tipo_usuario != 'BIBLIOTECA':
                return redirect('/biblioteca/login/?status=1')
            
            if not user.is_active:
                return redirect('/biblioteca/login/?status=2')
                
            login(request, user)
            return redirect('conta_biblioteca')
        else:
            return redirect('/biblioteca/login/?status=1')
            
    except Exception as e:
        print(f"Erro no login da biblioteca: {e}")
        return redirect('/biblioteca/login/?status=3')

