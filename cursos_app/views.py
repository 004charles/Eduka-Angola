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
from usuarios.decorators import aluno_logado_e_centros
from django.utils import timezone


from django.db.models import Count, Q, Prefetch

def home_cursos(request):
    agora = timezone.now()
    
    cursos_destaque = Curso.objects.filter(
        destaque=True, 
        publicado=True, 
        ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    categorias = Categoria.objects.prefetch_related(
        Prefetch(
            'curso',
            queryset=Curso.objects.filter(publicado=True, ativo=True),
            to_attr='cursos_ativos'
        )
    ).annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
    ).filter(num_cursos__gt=0)

    
    
    context = {
        'cursos_destaque': cursos_destaque,
        'categorias': categorias,  # <-- importante passar para o template
    }
    
    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            favoritos = Favorito.objects.filter(aluno=aluno).values_list('curso_id', flat=True)
            context.update({
                'aluno_logado': True,
                'favoritos': list(favoritos),
            })
        except Aluno.DoesNotExist:
            pass
    
    return render(request, 'home_cursos.html', context)



def inscrever_curso(request, curso_id):
    aluno_id = request.session.get('aluno')
    if not aluno_id:
        messages.error(request, "Você precisa estar logado como aluno para se inscrever.")
        return redirect('/auth/Login_aluno')

    curso = get_object_or_404(Curso, id=curso_id)
    aluno = get_object_or_404(Aluno, id=aluno_id)

    # Verificar se o curso está publicado
    if not curso.publicado:
        messages.error(request, "Este curso não está disponível para inscrições.")
        return redirect('curso_detalhe', id=curso.id)

    # Verificar se as inscrições estão abertas
    if not curso.inscricoes_abertas:
        messages.error(request, "As inscrições para este curso estão fechadas.")
        return redirect('curso_detalhe', id=curso.id)

    # Verificar se o curso tem turmas ativas
    if not curso.turmas_abertas.exists():
        messages.error(request, "Não há turmas disponíveis para este curso no momento.")
        return redirect('curso_detalhe', id=curso.id)

    # Verificar se o curso está lotado
    if curso.lotado:
        messages.error(request, "Este curso está lotado. Não há vagas disponíveis.")
        return redirect('curso_detalhe', id=curso.id)

    # Verificar se o aluno já está inscrito
    if Inscricao.objects.filter(aluno=aluno, curso=curso).exists():
        messages.warning(request, "Você já está inscrito neste curso.")
        return redirect('curso_detalhe', id=curso.id)

    # Criar a inscrição
    try:
        inscricao = Inscricao.objects.create(
            aluno=aluno,
            curso=curso,
            tipo_inscricao='ONLINE',
            status='P'  # Pendente
        )

        # Tentar enviar e-mail de confirmação
        try:
            link_curso = request.build_absolute_uri(
                reverse('curso_detalhe', kwargs={'id': curso.id})
            )
            inscricao.enviar_email_confirmacao(link_curso=link_curso)
        except Exception as e:
            messages.warning(request, f"Inscrição feita, mas houve um problema ao enviar o e-mail: {e}")

        messages.success(request, "Inscrição realizada com sucesso! Aguarde a aprovação do centro.")

    except Exception as e:
        messages.error(request, f"Erro ao realizar inscrição: {str(e)}")

    return redirect('curso_detalhe', id=curso.id)



def alterar_status_inscricao(request, inscricao_id, status):
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Você precisa estar logado como centro para alterar o status.")
        return redirect('login_gestor')

    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    
    # Verificar se o centro tem permissão para este curso
    if inscricao.curso.centro_id != centro_id:
        messages.error(request, "Você não tem permissão para alterar esta inscrição.")
        return redirect('painel_centro')

    if status in ['A', 'N', 'C']:  
        old_status = inscricao.status
        inscricao.status = status
        
        # Atualizar datas conforme o status
        if status == 'A' and not inscricao.data_confirmacao:
            inscricao.data_confirmacao = timezone.now()
        elif status == 'C' and not inscricao.data_cancelamento:
            inscricao.data_cancelamento = timezone.now()
        
        inscricao.save()

        # Atualizar vagas do curso se necessário
        if (status == 'A' and old_status != 'A') or (old_status == 'A' and status != 'A'):
            inscricao.curso.atualizar_vagas_globais()

        # Tentar enviar e-mail de notificação
        try:
            link_curso = request.build_absolute_uri(
                reverse('curso_detalhe', kwargs={'id': inscricao.curso.id})
            )
            inscricao.enviar_email_status(link_curso=link_curso)
        except Exception as e:
            messages.warning(request, f"Status alterado, mas houve problema ao enviar o e-mail: {e}")

        messages.success(request, f"Inscrição de {inscricao.aluno.nome} marcada como {inscricao.get_status_display()}.")
    else:
        messages.error(request, "Status inválido.")

    return redirect('gestao_inscricoes', curso_id=inscricao.curso.id)



def gestao_turmas(request, curso_id):
    """Página principal de gestão de turmas de um curso"""
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    try:
        curso = get_object_or_404(Curso, id=curso_id, centro_id=centro_id)
        turmas = curso.turmas.all().order_by('data_inicio', 'turno')
        
        # Estatísticas
        total_turmas = turmas.count()
        turmas_abertas = turmas.filter(status='ABERTA').count()
        turmas_em_andamento = turmas.filter(status='EM_ANDAMENTO').count()
        turmas_concluidas = turmas.filter(status='CONCLUIDA').count()
        
        context = {
            'centro': curso.centro,
            'curso': curso,
            'turmas': turmas,
            'total_turmas': total_turmas,
            'turmas_abertas': turmas_abertas,
            'turmas_em_andamento': turmas_em_andamento,
            'turmas_concluidas': turmas_concluidas,
            'active_tab': 'classes'
        }
        return render(request, 'gestor/turmas/gestao_turmas.html', context)
        
    except Exception as e:
        messages.error(request, f"Erro ao carregar gestão de turmas: {str(e)}")
        return redirect('painel_centro')

def criar_turma(request, curso_id):
    """View para criar uma nova turma"""
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    if request.method == 'POST':
        try:
            curso = get_object_or_404(Curso, id=curso_id, centro_id=centro_id)
            
            # Gerar código único para a turma
            turno = request.POST.get('turno')
            codigo = f"T{curso.id}_{turno[:3]}_{timezone.now().strftime('%H%M%S')}"
            
            # Processar dias da semana
            dias_semana = request.POST.getlist('dias_semana')
            dias_semana_str = ','.join(dias_semana)
            
            turma = Turma.objects.create(
                curso=curso,
                nome=request.POST.get('nome'),
                codigo=codigo,
                data_inicio=request.POST.get('data_inicio'),
                data_fim=request.POST.get('data_fim'),
                turno=turno,
                horario_inicio=request.POST.get('horario_inicio'),
                horario_fim=request.POST.get('horario_fim'),
                dias_semana=dias_semana_str,
                vagas_totais=int(request.POST.get('vagas_totais')),
                local=request.POST.get('local', ''),
                sala=request.POST.get('sala', ''),
                observacoes=request.POST.get('observacoes', ''),
                status='ABERTA'
            )
            
            # Associar instrutor se especificado
            instrutor_id = request.POST.get('instrutor_principal')
            if instrutor_id:
                instrutor = get_object_or_404(Instrutor, id=instrutor_id, centro=curso.centro)
                turma.instrutor_principal = instrutor
                turma.save()
            
            messages.success(request, 'Turma criada com sucesso!')
            return redirect('gestao_turmas', curso_id=curso.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar turma: {str(e)}')
    
    return redirect('gestao_turmas', curso_id=curso_id)

def editar_turma(request, turma_id):
    """View para editar uma turma existente"""
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    if request.method == 'POST':
        try:
            turma = get_object_or_404(Turma, id=turma_id, curso__centro_id=centro_id)
            
            # Processar dias da semana
            dias_semana = request.POST.getlist('dias_semana')
            dias_semana_str = ','.join(dias_semana)
            
            turma.nome = request.POST.get('nome', turma.nome)
            turma.data_inicio = request.POST.get('data_inicio', turma.data_inicio)
            turma.data_fim = request.POST.get('data_fim', turma.data_fim)
            turma.turno = request.POST.get('turno', turma.turno)
            turma.horario_inicio = request.POST.get('horario_inicio', turma.horario_inicio)
            turma.horario_fim = request.POST.get('horario_fim', turma.horario_fim)
            turma.dias_semana = dias_semana_str
            turma.vagas_totais = int(request.POST.get('vagas_totais', turma.vagas_totais))
            turma.local = request.POST.get('local', turma.local)
            turma.sala = request.POST.get('sala', turma.sala)
            turma.observacoes = request.POST.get('observacoes', turma.observacoes)
            turma.status = request.POST.get('status', turma.status)
            
            # Atualizar instrutor
            instrutor_id = request.POST.get('instrutor_principal')
            if instrutor_id:
                instrutor = get_object_or_404(Instrutor, id=instrutor_id, centro=turma.curso.centro)
                turma.instrutor_principal = instrutor
            else:
                turma.instrutor_principal = None
            
            turma.save()
            messages.success(request, 'Turma atualizada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar turma: {str(e)}')
    
    return redirect('gestao_turmas', curso_id=turma.curso.id)

def excluir_turma(request, turma_id):
    """View para excluir uma turma"""
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    if request.method == 'POST':
        try:
            turma = get_object_or_404(Turma, id=turma_id, curso__centro_id=centro_id)
            
            # Verificar se há inscrições na turma
            if turma.vagas_ocupadas > 0:
                messages.error(request, 'Não é possível excluir uma turma com alunos inscritos.')
                return redirect('gestao_turmas', curso_id=turma.curso.id)
            
            curso_id = turma.curso.id
            turma.delete()
            messages.success(request, 'Turma excluída com sucesso!')
            
            return redirect('gestao_turmas', curso_id=curso_id)
            
        except Exception as e:
            messages.error(request, f'Erro ao excluir turma: {str(e)}')
    
    return redirect('painel_centro')

def gestao_inscricoes(request, curso_id):
    """View para gerenciar inscrições de um curso"""
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    try:
        curso = get_object_or_404(Curso, id=curso_id, centro_id=centro_id)
        inscricoes = curso.inscricoes.select_related('aluno').all().order_by('-data_inscricao')
        
        # Filtros
        status_filter = request.GET.get('status')
        if status_filter:
            inscricoes = inscricoes.filter(status=status_filter)
        
        tipo_filter = request.GET.get('tipo')
        if tipo_filter:
            inscricoes = inscricoes.filter(tipo_inscricao=tipo_filter)
        
        # Estatísticas
        total_inscricoes = inscricoes.count()
        inscricoes_aceitas = inscricoes.filter(status='A').count()
        inscricoes_pendentes = inscricoes.filter(status='P').count()
        inscricoes_negadas = inscricoes.filter(status='N').count()
        inscricoes_canceladas = inscricoes.filter(status='C').count()
        
        context = {
            'centro': curso.centro,
            'curso': curso,
            'inscricoes': inscricoes,
            'total_inscricoes': total_inscricoes,
            'inscricoes_aceitas': inscricoes_aceitas,
            'inscricoes_pendentes': inscricoes_pendentes,
            'inscricoes_negadas': inscricoes_negadas,
            'inscricoes_canceladas': inscricoes_canceladas,
            'status_filter': status_filter,
            'tipo_filter': tipo_filter,
            'active_tab': 'enrollments'
        }
        return render(request, 'gestor/turmas/gestao_inscricoes.html', context)
        
    except Exception as e:
        messages.error(request, f"Erro ao carregar gestão de inscrições: {str(e)}")
        return redirect('painel_centro')

def inscrever_aluno_presencial(request, curso_id):
    """View para o gestor inscrever um aluno presencialmente"""
    centro_id = request.session.get('centro_id')
    if not centro_id:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    if request.method == 'POST':
        try:
            curso = get_object_or_404(Curso, id=curso_id, centro_id=centro_id)
            
            # Verificar se o curso está lotado
            if curso.lotado:
                messages.error(request, "Este curso está lotado. Não há vagas disponíveis.")
                return redirect('gestao_inscricoes', curso_id=curso_id)
            
            aluno_email = request.POST.get('aluno_email')
            aluno = get_object_or_404(Aluno, email=aluno_email)
            
            # Verificar se o aluno já está inscrito
            if Inscricao.objects.filter(aluno=aluno, curso=curso).exists():
                messages.warning(request, f"O aluno {aluno.nome} já está inscrito neste curso.")
                return redirect('gestao_inscricoes', curso_id=curso_id)
            
            # Criar inscrição presencial
            inscricao = Inscricao.objects.create(
                aluno=aluno,
                curso=curso,
                tipo_inscricao='PRESENCIAL',
                status='A',  # Aceita automaticamente
                forma_pagamento=request.POST.get('forma_pagamento', ''),
                valor_pago=request.POST.get('valor_pago') or 0,
                observacoes='Inscrição presencial realizada pelo gestor'
            )
            
            # Atualizar data de pagamento se valor foi pago
            if inscricao.valor_pago and inscricao.valor_pago > 0:
                inscricao.data_pagamento = timezone.now()
                inscricao.save()
            
            # Atualizar vagas do curso
            curso.atualizar_vagas_globais()
            
            # Tentar enviar e-mail
            try:
                link_curso = request.build_absolute_uri(
                    reverse('curso_detalhe', kwargs={'id': curso.id})
                )
                inscricao.enviar_email_status(link_curso=link_curso)
            except Exception as e:
                messages.warning(request, f"Inscrição realizada, mas houve problema ao enviar o e-mail: {e}")
            
            messages.success(request, f"Aluno {aluno.nome} inscrito presencialmente com sucesso!")
            
        except Aluno.DoesNotExist:
            messages.error(request, "Aluno não encontrado com este e-mail.")
        except Exception as e:
            messages.error(request, f"Erro ao inscrever aluno: {str(e)}")
    
    return redirect('gestao_inscricoes', curso_id=curso_id)


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


@aluno_logado_e_centros
def instrutor_detalhes(request, id):
    instrutor = get_object_or_404(Instrutor, id=id)
    
    cursos = Curso.objects.filter(instrutores=instrutor)
    
    context = {
        'instrutor': instrutor,
        'cursos': cursos
    }
    
    return render(request, 'curso_detalhe.html', context)

@aluno_logado_e_centros
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
        ).order_by('-destaque', 'data_inicio_curso') 

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

@aluno_logado_e_centros   
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

@aluno_logado_e_centros
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

@aluno_logado_e_centros
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

@aluno_logado_e_centros
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
        ).order_by('-destaque', 'data_inicio_curso')

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

@aluno_logado_e_centros
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
        'cursos_destaque':cursos_destaque,
        'cursos_video': cursos_video, 
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



