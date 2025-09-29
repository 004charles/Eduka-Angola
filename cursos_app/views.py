from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .models import Curso, Instrutor, Categoria, Inscricao, Aluno
from cursos_app.models import Favorito, CentroDeFormacao
from usuarios.models import Comentario, CentroSeguimento
from core.models import Galeria
from cursovideoapp.models import Curso_video

def inscrever_curso(request, curso_id):
    aluno_id = request.session.get('aluno')
    if not aluno_id:
        messages.error(request, "Você precisa estar logado como aluno para se inscrever.")
        return redirect('/auth/Login_aluno')

    curso = get_object_or_404(Curso, id=curso_id)
    aluno = get_object_or_404(Aluno, id=aluno_id)

    inscricao, created = Inscricao.objects.get_or_create(aluno=aluno, curso=curso)

    if not created:
        messages.warning(request, "Você já está inscrito neste curso.")
    else:
        try:
            link_curso = request.build_absolute_uri(
                reverse('curso_detalhe', kwargs={'id': curso.id})
            )
            inscricao.enviar_email_confirmacao(link_curso=link_curso)
        except Exception as e:
            messages.warning(request, f"Inscrição feita, mas houve um problema ao enviar o e-mail: {e}")

        messages.success(request, "Inscrição realizada com sucesso! Aguarde aprovação.")

    return redirect('curso_detalhe', id=curso.id)


def alterar_status_inscricao(request, inscricao_id, status):
    centro_id = request.session.get('centro')
    if not centro_id:
        messages.error(request, "Você precisa estar logado como centro para alterar o status.")
        return redirect('/auth/Login_centro')

    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    if inscricao.curso.centro_id != centro_id:
        messages.error(request, "Você não tem permissão para alterar esta inscrição.")
        return redirect('painel_centro')

    if status in ['A', 'N']:  
        inscricao.status = status
        inscricao.save()

        try:
            link_curso = request.build_absolute_uri(
                reverse('curso_detalhe', kwargs={'id': inscricao.curso.id})
            )
            inscricao.enviar_email_status(link_curso=link_curso)
        except Exception as e:
            messages.warning(request, f"Status alterado, mas houve problema ao enviar o e-mail: {e}")

        messages.success(request, f"Inscrição marcada como {inscricao.get_status_display()}.")
    else:
        messages.error(request, "Status inválido.")

    return redirect('painel_centro')



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

    comentarios = Comentario.objects.select_related('aluno__perfil').filter(
        curso=curso
    ).order_by('-data_comentario')

    centro = curso.centro

    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')


    cursos_relacionados = Curso.objects.filter(centro=centro).exclude(id=curso.id)
    cursos_relacionados_lista = Curso.objects.filter(categoria=curso.categoria).exclude(id=curso.id)
    imagem = Galeria.objects.all()[:6]

    video_preview = None
    if modulos:
        modulo = modulos.first()
        video_preview = modulo.videos.filter(liberado=True).order_by('ordem').first()

    context.update({
        'curso': curso,
        'modulos': modulos,
        'comentarios': comentarios,
        'centro': centro,
        'categoria': categorias,
        'cursos_relacionados': cursos_relacionados,
        'cursos_relacionados_lista': cursos_relacionados_lista,
        'video_preview': video_preview,
        'imagem': imagem,
    })

    return render(request, 'curso_detalhe.html', context)



def instrutor_detalhes(request, id):
    instrutor = get_object_or_404(Instrutor, id=id)
    
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

    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except Aluno.DoesNotExist:
            pass

    centro = get_object_or_404(CentroDeFormacao, id=centro_id)

    # Cursos por categoria
    categorias = Categoria.objects.filter(
        curso__centro=centro,
        curso__publicado=True
    ).annotate(
        num_cursos=Count('curso')
    ).distinct().order_by('nome')

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

    # Instrutores do centro
    instrutores = Instrutor.objects.filter(
        centro_de_formacao=centro, 
        ativo=True
    ).select_related('perfil').order_by('nome')

    context.update({
        'centro': centro,
        'cursos_por_categoria': cursos_por_categoria,
        'instrutores': instrutores,
    })

    return render(request, 'cursos_por_centro.html', context)

def instrutores_do_centro(request, centro_id):
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

    centro = get_object_or_404(CentroDeFormacao, id=centro_id)
    instrutores = Instrutor.objects.filter(
        centro_de_formacao=centro, 
        ativo=True
    ).prefetch_related('perfil').order_by('nome')

    context.update({
        'centro': centro,
        'instrutores': instrutores,
    })

    return render(request, 'cursos_porcentro.html', context)

def cursos_por_categoria(request, slug):
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

    
    imagens = Galeria.objects.all()[:6]
    categoria = get_object_or_404(Categoria, slug=slug)

    cursos = Curso.objects.filter(
        categoria=categoria,
        publicado=True,
        ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    context.update({
        'categoria': categoria,
        'cursos': cursos,
        'imagens': imagens,
    })

    return render(request, 'curso_categoria.html', context)

def pagina_categoria(request):
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

    categorias = Categoria.objects.annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
    )

    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

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

    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    # Lista simples de cursos para animação
    cursos_animacao = Curso.objects.filter(
    publicado=True
    ).values_list('titulo', flat=True)

    # Atualiza o contexto com os dados
    context.update({
        'categorias_com_cursos': categorias_com_cursos,
        'cursos_animacao': cursos_animacao
    })

    return render(request, 'todo_curso.html', context)
    
def ficha_inscricao(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    aluno = None
    aluno_id = request.session.get('aluno')
    if aluno_id:
        aluno = get_object_or_404(Aluno, id=aluno_id)

    contexto = {
        'curso': curso,
        'aluno': aluno,
    }

    return render(request, 'cursos_app/ficha.html', contexto)


def lista_centros(request):
    centros = CentroDeFormacao.objects.filter(ativo=True)
    return render(request, 'core/index.html', {'centros': centros})


def buscar_cursos(request):
    termo = request.GET.get('q', '').strip()
    centro_id = request.GET.get('centro')
    categoria_id = request.GET.get('categoria')
    nivel = request.GET.get('nivel')
    idioma = request.GET.get('idioma')
    turno = request.GET.get('turno')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    
    # --- Cursos de Centros ---
    cursos = Curso.objects.filter(ativo=True, publicado=True)
    
    if termo:
        cursos = cursos.filter(
            Q(titulo__icontains=termo) | 
            Q(descricao__icontains=termo) |
            Q(centro__nome__icontains=termo)
        )
    
    if centro_id:
        cursos = cursos.filter(centro_id=centro_id)
        
    if categoria_id:
        cursos = cursos.filter(categoria_id=categoria_id)
        
    if nivel in ['B', 'I', 'A']:
        cursos = cursos.filter(nivel=nivel)
        
    if idioma in ['PT', 'EN', 'ES', 'FR', 'OUTRO']:
        cursos = cursos.filter(idioma=idioma)
        
    if turno in ['M', 'T', 'N', 'I']:
        cursos = cursos.filter(turno=turno)
        
    if preco_min:
        try:
            cursos = cursos.filter(preco__gte=float(preco_min))
        except ValueError:
            pass
            
    if preco_max:
        try:
            cursos = cursos.filter(preco__lte=float(preco_max))
        except ValueError:
            pass
    
    ordenar_por = request.GET.get('ordenar_por', 'data_inicio')
    ordem = request.GET.get('ordem', 'asc')
    
    if ordem == 'desc':
        ordenar_por = f'-{ordenar_por}'
    
    cursos = cursos.order_by(ordenar_por)
    
    # --- Cursos em Vídeo ---
    cursos_video = Curso_video.objects.all()
    
    if termo:
        cursos_video = cursos_video.filter(
            Q(titulo__icontains=termo) | 
            Q(descricao__icontains=termo) |
            Q(instrutor__icontains=termo)
        )
    
    if categoria_id:
        cursos_video = cursos_video.filter(categoria_id=categoria_id)
    
    cursos_video = cursos_video.order_by('-data_publicacao')
    
    # --- Destaques ---
    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')
    
    cursos_destaque_video = Curso_video.objects.filter(destaque=True)

    context = {
        'cursos': cursos,
        'cursos_video': cursos_video,  # ✅ adicionados
        'termo_busca': termo,
        'centros': CentroDeFormacao.objects.filter(ativo=True),
        'categorias': Categoria.objects.all(),
        'filtros': {
            'centro': centro_id,
            'categoria': categoria_id,
            'nivel': nivel,
            'idioma': idioma,
            'turno': turno,
            'preco_min': preco_min,
            'preco_max': preco_max,
        }
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

    return render(request, 'resultados_busca.html', context)
