from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Curso, Instrutor, Categoria
from usuarios.models import Comentario
from cursos_app.models import CentroDeFormacao
from .models import Curso, Categoria
from django.db.models import Count, Q


def home_cursos(request):
    return render(request, 'home_cursos.html')

def curso_detalhe(request, id):
    curso = get_object_or_404(
        Curso.objects.select_related('centro')
                     .prefetch_related('instrutores'),
        id=id,
        publicado=True
    )

    modulos = curso.modulos.all()

    # Comentários com perfis dos alunos
    comentarios = Comentario.objects.select_related('aluno__perfil').filter(
        curso=curso
    ).order_by('-data_comentario')

    centro = curso.centro  # Pega o centro do curso atual

    # Cursos do mesmo centro (exceto o atual)
    cursos_relacionados = Curso.objects.filter(centro=centro).exclude(id=curso.id)
    cursos_relacionados_lista = Curso.objects.filter(categoria=curso.categoria).exclude(id=curso.id)


    # Pega o vídeo de preview do primeiro módulo, se houver
    video_preview = None
    if modulos:
        modulo = modulos.first()
        video_preview = modulo.videos.filter(liberado=True).order_by('ordem').first()

    context = {
        'curso': curso,
        'modulos': modulos,
        'comentarios': comentarios,
        'centro': centro,
        'cursos_relacionados': cursos_relacionados,
        'cursos_relacionados_lista': cursos_relacionados_lista,
        'video_preview': video_preview,  # Adiciona o vídeo de preview
    }

    return render(request, 'curso_detalhe.html', context)




def instrutor_detalhes(request, id):
    # Obtém o instrutor com base no id
    instrutor = get_object_or_404(Instrutor, id=id)
    
    # Obtém os cursos ministrados por esse instrutor
    cursos = Curso.objects.filter(instrutores=instrutor)
    
    context = {
        'instrutor': instrutor,
        'cursos': cursos
    }
    
    return render(request, 'curso_detalhe.html', context)

def cursos_por_centro(request, centro_id):
    centro = get_object_or_404(CentroDeFormacao, id=centro_id)
    cursos = centro.cursos.all()
    return render(request, 'cursos_por_centro.html', {'centro': centro, 'cursos': cursos})


def cursos_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    cursos = Curso.objects.filter(
        categoria=categoria,
        publicado=True,
        ativo=True
    ).select_related('centro').prefetch_related('instrutores')
    
    context = {
        'categoria': categoria,
        'cursos': cursos,
    }
    return render(request, 'curso_categoria.html', context)


def pagina_categoria(request):
    categoria = Categoria.objects.annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True)))
    
    context = {
        'categoria':categoria,
    }
    return render(request, 'core/categoria.html', context)