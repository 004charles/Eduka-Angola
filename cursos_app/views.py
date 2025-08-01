from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Curso, Instrutor, Categoria
from cursos_app.models import Aluno
from usuarios.models import Comentario
from django.shortcuts import redirect
from cursos_app.models import CentroDeFormacao
from .models import Curso, Categoria
from django.views.decorators.http import require_POST
from django.db.models import Count, Q


@require_POST
def adicionar_favorito(request, curso_id):
    if 'aluno' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'Não autenticado'}, status=403)
    
    try:
        curso = Curso.objects.get(id=curso_id)
        aluno = Aluno.objects.get(id=request.session['aluno'])
        
        favorito, created = Favorito.objects.get_or_create(
            aluno=aluno,
            curso=curso
        )
        
        if created:
            return JsonResponse({'status': 'added', 'message': 'Curso adicionado aos favoritos'})
        else:
            favorito.delete()
            return JsonResponse({'status': 'removed', 'message': 'Curso removido dos favoritos'})
            
    except Curso.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Curso não encontrado'}, status=404)
    except Aluno.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Aluno não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



def home_cursos(request):
    return render(request, 'home_cursos.html')

def curso_detalhe(request, id):
    if 'aluno' not in request.session:
        return redirect('/auth/curso_detalhe?status=4')

    # Inicializa o contexto
    context = {
        'aluno_logado': False,
    }

    try:
        aluno = Aluno.objects.get(id=request.session['aluno'])
        context.update({
            'aluno_logado': True,
            'aluno_nome': aluno.nome,
        })
    except Aluno.DoesNotExist:
        pass

    # Obtém o curso com centro e instrutores
    curso = get_object_or_404(
        Curso.objects.select_related('centro')
                    .prefetch_related('instrutores'),
        id=id,
        publicado=True
    )

    categorias = Categoria.objects.annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
    )

    modulos = curso.modulos.all()

    # Comentários com perfil dos alunos
    comentarios = Comentario.objects.select_related('aluno__perfil').filter(
        curso=curso
    ).order_by('-data_comentario')

    centro = curso.centro

    # Cursos do mesmo centro e da mesma categoria
    cursos_relacionados = Curso.objects.filter(centro=centro).exclude(id=curso.id)
    cursos_relacionados_lista = Curso.objects.filter(categoria=curso.categoria).exclude(id=curso.id)

    # Vídeo de preview
    video_preview = None
    if modulos:
        modulo = modulos.first()
        video_preview = modulo.videos.filter(liberado=True).order_by('ordem').first()

    # Atualiza o contexto com os dados do curso
    context.update({
        'curso': curso,
        'modulos': modulos,
        'comentarios': comentarios,
        'centro': centro,
        'categoria': categorias,
        'cursos_relacionados': cursos_relacionados,
        'cursos_relacionados_lista': cursos_relacionados_lista,
        'video_preview': video_preview,
    })

    return render(request, 'curso_detalhe.html', context)




def instrutor_detalhes(request, id):
    instrutor = get_object_or_404(Instrutor, id=id)
    
    # Obtém os cursos ministrados por esse instrutor
    cursos = Curso.objects.filter(instrutores=instrutor)
    
    context = {
        'instrutor': instrutor,
        'cursos': cursos
    }
    
    return render(request, 'curso_detalhe.html', context)


def cursos_por_centro(request, centro_id):
    context = {
        'aluno_logado': False,
    }

    # Verifica se o aluno está logado
    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except Aluno.DoesNotExist:
            pass

    # Obtém o centro de formação
    centro = get_object_or_404(CentroDeFormacao, id=centro_id)

    # Categorias com cursos publicados neste centro
    categorias = Categoria.objects.filter(
        curso__centro=centro,
        curso__publicado=True
    ).annotate(
        num_cursos=Count('curso')
    ).distinct().order_by('nome')

    # Organiza os cursos por categoria
    cursos_por_categoria = []
    for categoria in categorias:
        cursos = centro.cursos.filter(
            categoria=categoria,
            publicado=True
        ).order_by('-destaque', 'data_inicio')

        cursos_por_categoria.append({
            'categoria': categoria,
            'cursos': cursos,
            'total_cursos': categoria.num_cursos
        })

    # Atualiza o contexto com os dados do centro e cursos
    context.update({
        'centro': centro,
        'cursos_por_categoria': cursos_por_categoria,
    })

    return render(request, 'cursos_por_centro.html', context)

def cursos_por_categoria(request, slug):
    context = {
        'aluno_logado': False,
    }

    # Verifica se o aluno está logado
    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except Aluno.DoesNotExist:
            pass

    # Obtém a categoria pelo slug
    
    categoria = get_object_or_404(Categoria, slug=slug)

    # Busca os cursos da categoria
    cursos = Curso.objects.filter(
        categoria=categoria,
        publicado=True,
        ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    # Atualiza o contexto com os dados da categoria
    context.update({
        'categoria': categoria,
        'cursos': cursos,
    })

    return render(request, 'curso_categoria.html', context)

def pagina_categoria(request):
    context = {
        'aluno_logado': False,
    }

    # Verifica se o aluno está logado
    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except Aluno.DoesNotExist:
            pass

    # Busca as categorias com contagem de cursos ativos e publicados
    categorias = Categoria.objects.annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
    )

    # Atualiza o contexto com as categorias
    context.update({
        'categoria': categorias,
    })

    return render(request, 'core/categoria.html', context)


def todo_curso(request):
    context = {
        'aluno_logado': False,
    }

    # Verifica se o aluno está logado
    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except Aluno.DoesNotExist:
            pass

    # Monta lista de categorias com cursos publicados
    categorias_com_cursos = []
    for categoria in Categoria.objects.filter(curso__publicado=True).distinct():
        cursos = Curso.objects.filter(
            categoria=categoria,
            publicado=True
        ).order_by('-destaque', 'data_inicio')

        if cursos.exists():
            categorias_com_cursos.append({
                'categoria': categoria,
                'cursos': cursos,
                'total_cursos': cursos.count()
            })

    # Atualiza o contexto com os dados
    context.update({
        'categorias_com_cursos': categorias_com_cursos,
    })

    return render(request, 'todo_curso.html', context)
    
def ficha_inscricao(request):
    return render(request, 'cursos_app/ficha.html')