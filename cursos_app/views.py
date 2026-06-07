import random
import string
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q, Prefetch, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import HttpResponse
try:
    from weasyprint import HTML
except (ImportError, OSError):
    HTML = None

from django.contrib.staticfiles import finders

from cursos_app.forms import AvaliacaoForm
from .utils import (
    enviar_email_inscricao, processar_simulacao_pagamento, atribuir_turma_automatica
)
from .utils_secoes import filtrar_cursos_por_secao, get_secoes_config
from cursos_app.models import (
    Curso,
    Categoria,
    Instrutor,
    Inscricao,
    Favorito,
    Turma,
    PreRequisitoCurso,
)

from usuarios.models import Aluno
from usuarios.decorators import aluno_logado_e_centros
from gestoreduka.models import (
    CentroDeFormacao, GaleriaImagem, CentroSeguimento, 
    Evento, Parceria, Equipe
)
from avaliacoes.models import Comentario
from cursovideoapp.models import Curso_video






@login_required(login_url='login_aluno')
def inscrever_curso(request, curso_id):
    """View para inscrição em curso com simulação de pagamento"""
    curso = get_object_or_404(Curso, id=curso_id, publicado=True, ativo=True)
    
    # Verificar se aluno está logado e é ALUNO
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        messages.error(request, "Você precisa estar logado como aluno.")
        return redirect('login_aluno')
    
    try:
        aluno = request.user.aluno_profile
    except AttributeError:
        messages.error(request, "Perfil de aluno não encontrado.")
        return redirect('login_aluno')

    # Verificar se já está inscrito
    inscricao_existente = Inscricao.objects.filter(aluno=aluno, curso=curso).first()
    if inscricao_existente:
        messages.info(request, "Você já está inscrito neste curso.")
        return redirect('curso_detalhe', id=curso_id)
    
    # Verificar se há vagas disponíveis
    if curso.lotado:
        messages.error(request, "Este curso não possui mais vagas disponíveis.")
        return redirect('curso_detalhe', id=curso_id)
    
    # Verificar se possui turmas ativas
    if not curso.possui_turmas_ativas:
        messages.error(request, "Este curso não possui turmas ativas planejadas de momento.")
        return redirect('curso_detalhe', id=curso_id)
    
    # Verificar se as inscrições estão abertas
    if not curso.inscricoes_abertas:
        messages.error(request, "As inscrições para este curso estão encerradas.")
        return redirect('curso_detalhe', id=curso_id)
    
    # Obter turmas disponíveis para exibição
    turmas_disponiveis = curso.turmas.filter(status='ABERTA', vagas_disponiveis__gt=0)
    turma_disponivel = curso.get_turma_menos_lotada()
    
    if request.method == 'POST':
        import random
        codigo_gerado = str(random.randint(100000000, 999999999))
        
        # Validar turma selecionada
        turma_id = request.POST.get('turma_escolhida')
        if not turma_id:
            messages.error(request, "Por favor, selecione a turma e horário desejados.")
            return redirect('ficha_inscricao', curso_id=curso.id)
            
        from .models import Turma
        turma_escolhida = get_object_or_404(Turma, id=turma_id, curso=curso, status='ABERTA')
        if turma_escolhida.vagas_disponiveis <= 0:
            messages.error(request, "Esta turma já não possui vagas disponíveis. Por favor, selecione outra.")
            return redirect('ficha_inscricao', curso_id=curso.id)
            
        # Validar e obter documento exigido se aplicável
        documento_file = None
        if curso.documento_requerido != 'NENHUM':
            documento_file = request.FILES.get('documento_inscricao')
            if not documento_file:
                messages.error(request, f"O envio do documento '{curso.get_documento_requerido_display()}' é obrigatório para a inscrição.")
                return redirect('ficha_inscricao', curso_id=curso.id)
        
        # Criar inscrição
        inscricao = Inscricao.objects.create(
            aluno=aluno,
            curso=curso,
            turma_escolhida=turma_escolhida,
            documento_inscricao=documento_file,
            status='P',
            tipo_inscricao='ONLINE',
            codigo_simulacao=codigo_gerado,
            observacoes=f"Inscrição realizada em {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        )
        
        # Se for curso gratuito, confirmar automaticamente
        if curso.is_gratuito:
            inscricao.forma_pagamento = 'SIMULADO'
            inscricao.valor_pago = 0
            inscricao.data_pagamento = timezone.now()
            inscricao.status = 'A'
            inscricao.data_confirmacao = timezone.now()
            inscricao.save()
            
            messages.success(request, "Inscrição realizada com sucesso! Curso gratuito confirmado.")
            return redirect('painel_curso', curso_id=curso_id)
            
        from cursos_app.utils import enviar_email_inscricao
        try:
            enviar_email_inscricao(inscricao, tipo='pendente')
        except Exception:
            pass
        
        messages.success(request, "Inscrição iniciada. Prossiga com o pagamento para confirmar a sua vaga.")
        return redirect('tela_pagamento_inscricao', inscricao_id=inscricao.id)
        
@login_required(login_url='login_aluno')
def tela_pagamento_inscricao(request, inscricao_id):
    """View para intermediar o pagamento após a inscrição"""
    inscricao = get_object_or_404(Inscricao, id=inscricao_id, aluno=request.user.aluno_profile)
    curso = inscricao.curso
    
    if request.method == 'POST':
        try:
            from django.urls import reverse
            from pagamentos.services import get_payment_service, PagamentoException
            servico = get_payment_service()
            
            # Criar transação real
            pagamento = servico.criar_pagamento(
                usuario=request.user,
                tipo_pagamento='INSCRICAO',
                valor=curso.preco_atual,
                moeda='AOA',
                curso=curso,
                url_sucesso=request.build_absolute_uri(reverse('pagamento_sucesso')),
                url_cancelamento=request.build_absolute_uri(reverse('pagamento_cancelado')),
                metadados={'inscricao_id': str(inscricao.id)}
            )
            
            if pagamento and pagamento.url_pagamento:
                # Redirecionar diretamente para o checkout da Prontu!
                return redirect(pagamento.url_pagamento)
            else:
                messages.error(request, "Não foi possível gerar o link de pagamento. Por favor, tente novamente.")
                return redirect('tela_pagamento_inscricao', inscricao_id=inscricao.id)
                
        except PagamentoException as gateway_err:
            messages.error(request, f"Erro no gateway Prontu: {gateway_err}")
            return redirect('tela_pagamento_inscricao', inscricao_id=inscricao.id)
        except Exception as e_err:
            messages.error(request, f"Ocorreu um erro inesperado ao iniciar o pagamento: {e_err}")
            return redirect('tela_pagamento_inscricao', inscricao_id=inscricao.id)

    context = {
        'inscricao': inscricao,
        'curso': curso
    }
    return render(request, 'cursos/tela_pagamento.html', context)
    
    # Mostrar página de confirmação de inscrição
    context = {
        'curso': curso,
        'aluno': aluno,
        'turma_disponivel': turma_disponivel,
        'turmas_disponiveis': turmas_disponiveis,
        'valor_total': curso.preco_atual,
    }
    
    return render(request, 'cursos/confirmar_inscricao.html', context)



@login_required(login_url='login_aluno')
def cancelar_inscricao(request, inscricao_id):
    """View para cancelar inscrição"""
    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    
    # Verificar se o aluno é o dono da inscrição
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO' or request.user.aluno_profile.id != inscricao.aluno.id:
        messages.error(request, "Você não tem permissão para cancelar esta inscrição.")
        return redirect('curso_detalhe', id=inscricao.curso.id)
    
    # Verificar se pode cancelar
    if inscricao.status == 'C':
        messages.info(request, "Esta inscrição já foi cancelada.")
    elif inscricao.status == 'A':
        inscricao.status = 'C'
        inscricao.data_cancelamento = timezone.now()
        inscricao.save()
        
        messages.success(request, "Inscrição cancelada com sucesso.")
    else:
        messages.error(request, "Não é possível cancelar esta inscrição no momento.")
    
    return redirect('meus_cursos')

@login_required(login_url='login_aluno')
def painel_curso(request, curso_id):
    """View para painel do curso (após inscrição)"""
    curso = get_object_or_404(Curso, id=curso_id, publicado=True)
    
    # Verificar se aluno está logado e é ALUNO
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        messages.error(request, "Você precisa estar logado como aluno.")
        return redirect('login_aluno')
    
    try:
        aluno = request.user.aluno_profile
    except AttributeError:
        messages.error(request, "Perfil de aluno não encontrado.")
        return redirect('login_aluno')
    
    # Verificar se está inscrito
    inscricao = Inscricao.objects.filter(aluno=aluno, curso=curso).first()
    if not inscricao:
        messages.error(request, "Você precisa estar inscrito no curso para acessar o painel.")
        return redirect('curso_detalhe', id=curso_id)
    
    # Verificar se a inscrição foi aceita
    if inscricao.status != 'A':
        messages.warning(request, f"Sua inscrição está {inscricao.get_status_display().lower()}. Aguarde a confirmação.")
    
    context = {
        'curso': curso,
        'inscricao': inscricao,
        'aluno': aluno,
        'modulos': curso.modulos.all(),
    }
    
    return render(request, 'cursos/painel_curso.html', context)


def alterar_status_inscricao(request, inscricao_id, status):
    if not request.user.is_authenticated or request.user.tipo_usuario != 'GESTOR':
        messages.error(request, "Você precisa estar logado como centro para alterar o status.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id

    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    
    if inscricao.curso.centro_id != centro_id:
        messages.error(request, "Você não tem permissão para alterar esta inscrição.")
        return redirect('painel_centro')

    if status in ['A', 'N', 'C']:  
        old_status = inscricao.status
        inscricao.status = status
        
        if status == 'A' and not inscricao.data_confirmacao:
            inscricao.data_confirmacao = timezone.now()
        elif status == 'C' and not inscricao.data_cancelamento:
            inscricao.data_cancelamento = timezone.now()
        
        inscricao.save()

        if (status == 'A' and old_status != 'A') or (old_status == 'A' and status != 'A'):
            inscricao.curso.atualizar_vagas_globais()

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
    if not request.user.is_authenticated or request.user.tipo_usuario != 'GESTOR':
        messages.error(request, "Você precisa estar logado como centro.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
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
    if not request.user.is_authenticated or request.user.tipo_usuario != 'GESTOR':
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
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
    if not request.user.is_authenticated or request.user.tipo_usuario != 'GESTOR':
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
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
    if not request.user.is_authenticated or request.user.tipo_usuario != 'GESTOR':
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
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
    if not request.user.is_authenticated or request.user.tipo_usuario != 'GESTOR':
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
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
    if not request.user.is_authenticated or request.user.tipo_usuario != 'GESTOR':
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
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
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'status': 'error', 'message': 'Não autenticado'}, status=403)
    
    try:
        curso = Curso.objects.get(id=curso_id)
        aluno = request.user.aluno_profile
        
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
    user_auth = request.user.is_authenticated
    aluno_logado = user_auth # Se estiver logado, já não deve mostrar "faça login"
    aluno_nome = None
    aluno_inscricao = None
    aluno_obj = None
    
    if user_auth:
        aluno_nome = request.user.nome
        if request.user.tipo_usuario == 'ALUNO':
            try:
                aluno_obj = request.user.aluno_profile
                aluno_inscricao = aluno_obj.inscricoes.filter(curso_id=id).first()
            except AttributeError:
                pass
        elif request.user.is_staff:
            # Staff/Admin can also see/test things
            aluno_logado = True
    
    curso = get_object_or_404(
        Curso.objects.select_related('centro')
                    .prefetch_related('instrutores', 'pre_requisitos'),
        id=id,
        publicado=True
    )
    
    # Atualizar histórico de visualizações recentes
    viewed = request.session.get('viewed_cursos', [])
    if id in viewed:
        viewed.remove(id)
    viewed.insert(0, id)
    request.session['viewed_cursos'] = viewed[:3]
    
    curso.visualizacoes += 1
    curso.save(update_fields=['visualizacoes'])
    
    # Encontrar outras filiais/centro que oferecem o mesmo curso (mesmo título)
    outras_localizacoes = Curso.objects.filter(
        centro=curso.centro,
        titulo__iexact=curso.titulo,
        publicado=True,
        ativo=True
    ).exclude(id=curso.id)
    
    
    
    comentarios = Comentario.objects.select_related('aluno').filter(
        curso=curso,
        aprovado=True
    ).order_by('-data_comentario')
    
    # Otimização: Agrupar agregações em uma única consulta
    stats = comentarios.aggregate(
        media=Avg('avaliacao'),
        total=Count('id'),
        c5=Count('id', filter=Q(avaliacao=5)),
        c4=Count('id', filter=Q(avaliacao=4)),
        c3=Count('id', filter=Q(avaliacao=3)),
        c2=Count('id', filter=Q(avaliacao=2)),
        c1=Count('id', filter=Q(avaliacao=1)),
    )
    
    media_avaliacoes = stats['media'] or 0.0
    total_comentarios = stats['total'] or 0
    
    rating_counts = {
        '5': stats['c5'],
        '4': stats['c4'],
        '3': stats['c3'],
        '2': stats['c2'],
        '1': stats['c1'],
    }
    
    rating_percent = {}
    for key, count in rating_counts.items():
        rating_percent[key] = (count / total_comentarios) * 100 if total_comentarios > 0 else 0
    
    # Cache para categorias (lista global de filtros)
    from django.core.cache import cache
    categorias = cache.get('categorias_com_contagem')
    if not categorias:
        categorias = list(Categoria.objects.annotate(
            num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
        ))
        cache.set('categorias_com_contagem', categorias, 3600) # 1 hora
    
    centro = curso.centro

    comentario_existente = None
    if aluno_obj:
        comentario_existente = Comentario.objects.filter(
            aluno=aluno_obj, 
            curso=curso
        ).first()
    
    avaliacao_form = None
    if aluno_logado and aluno_inscricao:
        avaliacao_form = AvaliacaoForm(instance=comentario_existente)
    
    cursos_relacionados = list(Curso.objects.filter(
        centro=centro, 
        publicado=True, 
        ativo=True
    ).exclude(id=curso.id).select_related('centro')[:4])
    
    cursos_relacionados_lista = []
    if curso.categoria:
        cursos_relacionados_lista = list(Curso.objects.filter(
            categoria=curso.categoria, 
            publicado=True, 
            ativo=True
        ).exclude(id=curso.id).select_related('centro')[:4])
    
    imagem = cache.get('galeria_detalhe_cache')
    if not imagem:
        imagem = list(GaleriaImagem.objects.all()[:6])
        cache.set('galeria_detalhe_cache', imagem, 1800) # 30 minutos
    
    video_preview = None
    
    # Fetch modules and their videos
    modulos = curso.modulos.all().prefetch_related('videos')
    
    context = {
        'curso': curso,
        'modulos': modulos,
        'comentarios': comentarios,
        'centro': centro,
        'categorias': categorias,
        'cursos_relacionados': cursos_relacionados,
        'cursos_relacionados_lista': cursos_relacionados_lista,
        'outras_localizacoes': outras_localizacoes,
        'video_preview': video_preview,
        'imagem': imagem,
        'media_avaliacoes': round(media_avaliacoes, 1),
        'aluno_logado': aluno_logado,
        'aluno_nome': aluno_nome,
        'aluno_inscricao': aluno_inscricao,
        'avaliacao_form': avaliacao_form,
        'comentario_existente': comentario_existente,
        'rating_counts': rating_counts,
        'rating_percent': rating_percent,
        'total_comentarios': total_comentarios,
    }
    
    return render(request, 'curso_detalhe.html', context)

@login_required(login_url='login_aluno')
def adicionar_comentario(request, curso_id):
    from gestoreduka.models import NotificacaoGestor
    curso = get_object_or_404(Curso, id=curso_id, publicado=True)
    
    # Obter aluno
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        messages.error(request, "Você precisa estar logado como aluno.")
        return redirect('login_aluno')
    
    try:
        aluno = request.user.aluno_profile
    except AttributeError:
        messages.error(request, "Perfil de aluno não encontrado.")
        return redirect('login_aluno')
    
    # Verificar se já avaliou (Opcional: o usuário pode querer permitir múltiplos comentários se for dúvida)
    # Por agora, vamos permitir múltiplos comentários se o usuário assim desejar, removendo a trava de "comentario_existente"
    # ou simplesmente criar um novo sempre.
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.aluno = aluno
            comentario.curso = curso
            
            # Obter status do aluno
            inscricao = aluno.inscricoes.filter(curso=curso).first()
            if inscricao:
                comentario.status_aluno = 'AND' if inscricao.status == 'A' else 'COM'
            else:
                comentario.status_aluno = 'AND' # Visitante/Interessado
            
            # Verificar se é uma resposta a outro comentário
            parent_id = request.POST.get('parent_id')
            if parent_id:
                from avaliacoes.models import Comentario as ComentarioModel
                parent_comment = ComentarioModel.objects.filter(id=parent_id).first()
                if parent_comment:
                    comentario.parent = parent_comment
                    
                    # Notificar o aluno que recebeu a resposta
                    from usuarios.models import NotificacaoAluno
                    if parent_comment.aluno != aluno:
                        NotificacaoAluno.objects.create(
                            aluno=parent_comment.aluno,
                            titulo=f"Nova resposta ao seu comentário",
                            mensagem=f"{aluno.nome} respondeu ao seu comentário no curso {curso.titulo}.",
                            link=f"/cursos/curso_detalhe/{curso.id}/",
                            tipo='CURSO'
                        )

            comentario.save()

            # Criar Notificação para o Centro
            NotificacaoGestor.objects.create(
                centro=curso.centro,
                titulo=f"Nova interação em: {curso.titulo}",
                mensagem=f"O aluno {aluno.nome} deixou um comentário/pergunta: \"{comentario.comentario[:50]}...\"",
                link=f"/gestoreduka/comentarios/",
                tipo='COMENTARIO'
            )
            
            messages.success(request, "Sua mensagem foi enviada com sucesso!")
            return redirect('curso_detalhe', id=curso_id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    
    return redirect('curso_detalhe', id=curso_id)

def api_carregar_comentarios(request, curso_id):
    """Retorna comentários paginados via JSON"""
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 5))
    
    comentarios = Comentario.objects.filter(
        curso_id=curso_id, 
        aprovado=True,
        parent__isnull=True
    ).select_related('aluno', 'aluno__perfil').order_by('-data_comentario')[offset:offset+limit]
    
    data = []
    for c in comentarios:
        respostas = []
        for r in c.respostas_comunidade.all():
            respostas.append({
                'aluno': r.aluno.nome,
                'comentario': r.comentario,
                'foto': r.aluno.perfil.get_foto_perfil_url() if hasattr(r.aluno, 'perfil') else None,
            })
            
        data.append({
            'id': c.id,
            'aluno': c.aluno.nome,
            'foto': c.aluno.perfil.get_foto_perfil_url() if hasattr(c.aluno, 'perfil') else None,
            'avaliacao': c.avaliacao,
            'comentario': c.comentario,
            'data': c.data_comentario.strftime('%d/%m/%Y'),
            'resposta': c.resposta,
            'resposta_data': c.resposta_data.strftime('%d/%m/%Y') if c.resposta_data else None,
            'respostas_comunidade': respostas
        })
    
    total_principais = Comentario.objects.filter(curso_id=curso_id, aprovado=True, parent__isnull=True).count()
    return JsonResponse({'comentarios': data, 'has_more': total_principais > offset + limit})

@login_required
def excluir_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    
    # Verificar se o usuário tem permissão
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        messages.error(request, "Você precisa estar logado.")
        return redirect('login_aluno')
    
    if request.user.aluno_profile.id != comentario.aluno.id:
        messages.error(request, "Você não tem permissão para excluir este comentário.")
        if comentario.curso:
            return redirect('curso_detalhe', id=comentario.curso.id)
        else:
            return redirect('detalhe_curso', slug=comentario.curso_video.slug)
    
    # Salvar referência para redirecionamento antes de excluir
    if comentario.curso:
        url_redirecionamento = redirect('curso_detalhe', id=comentario.curso.id)
    else:
        url_redirecionamento = redirect('detalhe_curso', slug=comentario.curso_video.slug)
        
    comentario.delete()
    
    messages.success(request, "Comentário excluído com sucesso!")
    return url_redirecionamento

@login_required
def denunciar_comentario(request, comentario_id):
    comentario = get_object_or_404(Comentario, id=comentario_id)
    
    # Verificar se não é o próprio autor
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO' and request.user.aluno_profile.id == comentario.aluno.id:
        messages.warning(request, "Você não pode denunciar seu próprio comentário.")
        if comentario.curso:
            return redirect('curso_detalhe', id=comentario.curso.id)
        else:
            return redirect('detalhe_curso', slug=comentario.curso_video.slug)
    
    comentario.denunciar()
    
    messages.info(request, "Obrigado por reportar. Nossa equipe irá analisar o comentário.")
    
    if comentario.curso:
        return redirect('curso_detalhe', id=comentario.curso.id)
    else:
        return redirect('detalhe_curso', slug=comentario.curso_video.slug)

def catalogo_cursos(request):
    """
    View para exibir o catálogo completo de cursos com filtros.
    """
    # Obter todos os cursos ativos e publicados
    cursos = Curso.objects.filter(
        ativo=True,
        publicado=True
    ).order_by('-data_criacao')
    
    # Aplicar filtros
    categoria_id = request.GET.get('categoria')
    nivel = request.GET.get('nivel')
    modalidade = request.GET.get('modalidade')
    idioma = request.GET.get('idioma')
    preco = request.GET.get('preco')
    busca = request.GET.get('q')
    origem = request.GET.get('origem')  # 'parceiro' ou 'original'
    centro_id = request.GET.get('centro')
    
    # Novos filtros solicitados
    filtro_tempo = request.GET.get('tempo')  # 'semana'
    destaque_filtro = request.GET.get('destaque')  # 'true'
    inicio_proximo = request.GET.get('inicio_proximo')  # 'true'
    mais_procurados = request.GET.get('mais_procurados')  # 'true'
    para_voce = request.GET.get('para_voce')  # 'true'
    categoria_slug = request.GET.get('cat_slug')
    
    # Mapeamento de sinônimos (Smart Search Base)
    if busca:
        sinonimos = {
            'computador': 'Informática',
            'informatica': 'Informática',
            'digital': 'Marketing',
            'web': 'Programação',
            'net': 'Redes',
            'ingles': 'Inglês',
            'comunicaçao': 'Marketing',
        }
        for termo, substituto in sinonimos.items():
            if termo in busca.lower():
                busca = f"{busca} {substituto}"
    
    # Filtro por categoria
    if categoria_id:
        cursos = cursos.filter(categoria_id=categoria_id)

    # Filtro por centro
    if centro_id:
        cursos = cursos.filter(centro_id=centro_id)
    
    # Filtro por nível
    if nivel:
        cursos = cursos.filter(nivel=nivel)
    
    # Filtro por modalidade
    if modalidade:
        cursos = cursos.filter(modalidade=modalidade)
    
    # Filtro por idioma
    if idioma:
        cursos = cursos.filter(idioma=idioma)
    
    # Filtro por preço
    if preco:
        if preco == 'gratuitos':
            cursos = cursos.filter(is_gratuito=True)
        elif preco == 'pagina_100':
            cursos = cursos.filter(preco__lte=100, is_gratuito=False)
        elif preco == '100_500':
            cursos = cursos.filter(preco__gte=100, preco__lte=500, is_gratuito=False)
        elif preco == '500_plus':
            cursos = cursos.filter(preco__gt=500, is_gratuito=False)
    
    # Filtro: Cursos da Semana
    if filtro_tempo == 'semana':
        uma_semana_atras = timezone.now() - timedelta(days=7)
        cursos = cursos.filter(data_criacao__gte=uma_semana_atras)
    
    # Filtro: Em Destaque
    if destaque_filtro == 'true':
        cursos = cursos.filter(destaque=True)
    
    # Filtro: Cursos de Tecnologia (Informática)
    if categoria_slug in ['tecnologia', 'informatica']:
        cursos = cursos.filter(categoria__nome__icontains='Informática')
    
    # Lógica de Ordenação
    if inicio_proximo == 'true':
        cursos = cursos.filter(data_inicio__gte=timezone.now().date()).order_by('data_inicio')
    elif mais_procurados == 'true':
        cursos = cursos.annotate(num_estudantes=Count('inscricoes')).order_by('-visualizacoes', '-num_estudantes')
    else:
        # Priorização por Plano do Centro (Padrão)
        from django.db.models.functions import Coalesce
        from django.db.models import Value
        
        cursos = cursos.annotate(
            center_priority=Coalesce('centro__assinatura__plano__prioridade_busca', Value(0))
        ).order_by('-center_priority', '-data_criacao')
    
    # Filtro: Para Você (IA Recomendações)
    if para_voce == 'true' and request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        from inteligencia.utils import recomendar_cursos
        try:
            aluno = request.user.aluno_profile
            cursos_recomendados_ids = recomendar_cursos(aluno, limite=20, ids_only=True)
            if cursos_recomendados_ids:
                # Mantém a ordem da recomendação usando Case/When ou filtrando apenas os IDs
                cursos = cursos.filter(id__in=cursos_recomendados_ids)
        except Exception:
            pass
    
    # Filtro por Origem
    if origem == 'original':
        # Nota: Por simplificação, se for original, retornamos um queryset vazio do principal
        # e o template deve lidar com a exibição de vídeos se houver tempo.
        # Nisto, vamos apenas filtrar o queryset principal para não exibir parceiros.
        cursos = cursos.none()
    
    # Filtro: Secção Dinâmica (Novo)
    secao_key = request.GET.get('secao')
    secao_ativa = None
    if secao_key:
        cursos = filtrar_cursos_por_secao(cursos, secao_key)
        secoes_config = get_secoes_config()
        if secao_key in secoes_config:
            secao_ativa = secoes_config[secao_key]

    # Paginação
    paginator = Paginator(cursos, 12)  # 12 cursos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obter categorias para o menu de filtros
    categorias = Categoria.objects.annotate(
        total_cursos=Count('curso')
    ).filter(total_cursos__gt=0)
    
    # Contexto
    context = {
        'cursos': page_obj,
        'page_obj': page_obj,
        'categorias': categorias,
        'total_cursos': cursos.count(),
        'secao_ativa': secao_ativa,
        'filtros': {
            'categoria': categoria_id,
            'nivel': nivel,
            'modalidade': modalidade,
            'idioma': idioma,
            'preco': preco,
            'busca': busca,
            'origem': origem,
            'secao': secao_key,
        }
    }
    
    return render(request, 'catalogo.html', context)


def instrutor_detalhes(request, id):
    instrutor = get_object_or_404(Instrutor, id=id)
    
    cursos = Curso.objects.filter(instrutores=instrutor)
    
    context = {
        'c1': stats['c1'] or 0,
        'avaliacoes_distribuicao': distrib,
        'outras_localizacoes': outras_localizacoes,
    }
    
    return render(request, 'cursos_app/curso_detalhe.html', context)

def cursos_por_centro(request, centro_id):
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

    centro = get_object_or_404(
        CentroDeFormacao.objects.prefetch_related(
            'galeria_imagens', 'equipe', 'eventos', 'parcerias', 'estatisticas', 'depoimentos', 'seguidores'
        ), 
        id=centro_id
    )
    
    # Atualizar histórico de visualizações recentes
    viewed = request.session.get('viewed_centros', [])
    if centro_id in viewed:
        viewed.remove(centro_id)
    viewed.insert(0, centro_id)
    request.session['viewed_centros'] = viewed[:3]
    
    # Verificar se o aluno logado segue este centro
    aluno_segue = False
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        from gestoreduka.models import CentroSeguimento
        try:
            aluno = request.user.aluno_profile
            aluno_segue = centro.seguidores.filter(aluno=aluno).exists()
        except:
            pass

    context.update({
        'centro': centro,
        'aluno_segue': aluno_segue,
        'seguidores_count': centro.seguidores.count(),
        'todos_os_cursos': centro.cursos.filter(publicado=True).order_by('-destaque', '-data_criacao')
    })

    # Cursos por categoria (Otimizado: Uma única consulta + agrupamento em Python)
    cursos_do_centro = centro.cursos.filter(publicado=True).select_related('categoria').order_by('-destaque', 'data_inicio')
    
    from collections import defaultdict
    grupos = defaultdict(list)
    for c in cursos_do_centro:
        grupos[c.categoria].append(c)
    
    cursos_por_categoria = []
    for cat, cursos_list in grupos.items():
        if cat:
            cursos_por_categoria.append({
                'categoria': cat,
                'cursos': cursos_list,
                'total_cursos': len(cursos_list)
            })
    
    # Ordenar por nome da categoria
    cursos_por_categoria.sort(key=lambda x: x['categoria'].nome)

    instrutores = Instrutor.objects.filter(
        centro_de_formacao=centro, 
        ativo=True
    ).order_by('nome')

    # Dados Adicionais para o Hub Institucional
    try:
        perfil = centro.perfil
    except:
        perfil = None
    
    galeria = centro.galeria_imagens.all().order_by('ordem')
    equipe = centro.equipe.all()
    eventos = centro.eventos.all().order_by('-data_inicio')[:3]
    parcerias = centro.parcerias.filter(ativa=True)
    
    # Seguidores e Estado de Seguimento
    seguidores_count = centro.seguidores.count()
    ja_segue = aluno_segue # Já calculado acima

    # Estatísticas Personalizadas
    estatisticas = centro.estatisticas.all().order_by('ordem')
    
    # Depoimentos (Apenas aprovados e específicos do centro)
    depoimentos = centro.depoimentos.filter(aprovado=True).order_by('-data')

    # --- Dados para Gráficos de Crescimento (Últimos 6 meses) ---
    seis_meses_atras = timezone.now() - timedelta(days=180)
    
    # 1. Agrupar inscrições e seguidores por mês
    stats_inscricoes = centro.cursos.all().values('inscricoes__data_inscricao') \
        .annotate(month=TruncMonth('inscricoes__data_inscricao')) \
        .filter(month__gte=seis_meses_atras) \
        .values('month') \
        .annotate(total=Count('inscricoes')) \
        .order_by('month')

    seguidores_chart_data = centro.seguidores.all() \
        .annotate(month=TruncMonth('data_seguimento')) \
        .filter(month__gte=seis_meses_atras) \
        .values('month') \
        .annotate(total=Count('id')) \
        .order_by('month')

    meses_traduzidos = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    chart_labels = []
    chart_alunos_values = []
    chart_seguidores_values = []
    
    for i in range(5, -1, -1):
        d = timezone.now() - timedelta(days=i*30)
        m_idx = d.month
        y_val = d.year
        label = f"{meses_traduzidos[m_idx]} {y_val}"
        chart_labels.append(label)
        
        val_alunos = next((s['total'] for s in stats_inscricoes if s['month'] and s['month'].month == m_idx), 0)
        chart_alunos_values.append(val_alunos)
        
        val_seg = next((s['total'] for s in seguidores_chart_data if s['month'] and s['month'].month == m_idx), 0)
        chart_seguidores_values.append(val_seg)

    context.update({
        'chart_labels': chart_labels,
        'chart_alunos_values': chart_alunos_values,
        'chart_seguidores_values': chart_seguidores_values,
        'centro': centro,
        'perfil': perfil,
        'cursos_por_categoria': cursos_por_categoria,
        'instrutores': instrutores,
        'galeria': galeria,
        'equipe': equipe,
        'eventos': eventos,
        'parcerias': parcerias,
        'estatisticas': estatisticas,
        'estagios': centro.estagios.filter(ativo=True).order_by('-data_publicacao'),
        'depoimentos': depoimentos,
        'seguidores_count': seguidores_count,
        'ja_segue': ja_segue,
    })

    return render(request, 'cursos_por_centro.html', context)

@aluno_logado_e_centros   
def instrutores_do_centro(request, centro_id):
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

    centro = get_object_or_404(CentroDeFormacao, id=centro_id)
    instrutores = Instrutor.objects.filter(
        centro_de_formacao=centro, 
        ativo=True
    ).order_by('nome')

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

    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except AttributeError:
            pass

    
    imagens = GaleriaImagem.objects.all()[:6]
    categoria = get_object_or_404(Categoria, slug=slug)

    # Filtros e Ordenação
    ordenar = request.GET.get('ordenar')
    competencia = request.GET.get('competencia')
    busca = request.GET.get('busca')
    
    # Filtros de destaque e novos
    filtro_em_destaque = request.GET.get('em_destaque') == 'on'
    filtro_esta_semana = request.GET.get('esta_semana') == 'on'
    filtro_tecnologia = request.GET.get('tecnologia') == 'on'
    filtro_para_voce = request.GET.get('para_voce') == 'on'
    filtro_proximos = request.GET.get('proximos') == 'on'

    queryset = Curso.objects.filter(
        categoria=categoria,
        publicado=True,
        ativo=True
    ).select_related('centro').prefetch_related('instrutores', 'modulos', 'comentarios')

    # Aplicar busca se existir
    if busca:
        queryset = queryset.filter(
            Q(titulo__icontains=busca) | 
            Q(descricao__icontains=busca) |
            Q(centro__nome__icontains=busca)
        )

    # Aplicar filtros específicos do usuário
    if filtro_em_destaque:
        queryset = queryset.filter(destaque=True)

    if filtro_esta_semana:
        uma_semana_atras = timezone.now() - timedelta(days=7)
        queryset = queryset.filter(data_criacao__gte=uma_semana_atras)

    if filtro_tecnologia:
        queryset = queryset.filter(
            Q(categoria__slug__icontains='tecnologia') | 
            Q(categoria__slug__icontains='informatica')
        )

    if filtro_proximos:
        hoje = timezone.now()
        um_mes_depois = hoje + timedelta(days=30)
        queryset = queryset.filter(data_inicio__gte=hoje, data_inicio__lte=um_mes_depois)

    # Filtro "Para Você" (Recomendações de IA)
    if filtro_para_voce and request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            from inteligencia.utils import recomendar_cursos
            cursos_recomendados_ids = recomendar_cursos(request.user.aluno_profile)
            if cursos_recomendados_ids:
                # Mantém os cursos da categoria atual que estão nas recomendações
                queryset = queryset.filter(id__in=cursos_recomendados_ids)
        except ImportError:
            pass

    # Aplicar Ordenação
    if ordenar == 'recentes':
        queryset = queryset.order_by('-data_criacao')
    elif ordenar == 'popularidade':
        queryset = queryset.annotate(
            num_estudantes=Count('inscricoes')
        ).order_by('-num_estudantes')
    elif ordenar == 'preco_baixo':
        queryset = queryset.order_by('preco')
    elif ordenar == 'preco_alto':
        queryset = queryset.order_by('-preco')
    elif ordenar == 'mais_procurados':
        queryset = queryset.annotate(
            num_vviews=Coalesce('visualizacoes', Value(0))
        ).order_by('-num_vviews')
    else:
        # Padrão: Destaque primeiro, depois data de início
        queryset = queryset.order_by('-destaque', 'data_inicio')

    cursos = queryset

    # Adicionar secções especiais (Filtros Funcionais por Secção)
    context.update({
        'categoria': categoria,
        'cursos': cursos,
        'imagens': imagens,
        'cursos_destaque': queryset.filter(destaque=True)[:8],
        'cursos_recentes': queryset.order_by('-data_criacao')[:8],
        'cursos_populares': queryset.annotate(num_estudantes=Count('inscricoes')).order_by('-num_estudantes')[:8],
        'filtros_ativos': any([busca, ordenar, competencia, filtro_em_destaque, filtro_esta_semana, filtro_para_voce, filtro_proximos]),
        'filtros': {
            'ordenar': ordenar,
            'busca': busca,
            'em_destaque': filtro_em_destaque,
            'esta_semana': filtro_esta_semana,
            'tecnologia': filtro_tecnologia,
            'para_voce': filtro_para_voce,
            'proximos': filtro_proximos,
        }
    })

    # Recomendações personalizadas dentro da categoria
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            from inteligencia.utils import recomendar_cursos
            recomendados = recomendar_cursos(request.user.aluno_profile, limite=10)
            # Filtrar recomendações para garantir que são desta categoria
            context['cursos_recomendados_categoria'] = [c for c in recomendados if c.categoria_id == categoria.id]
        except Exception:
            pass

    return render(request, 'curso_categoria.html', context)

@aluno_logado_e_centros
def pagina_categoria(request):
    imagens = GaleriaImagem.objects.all()[:6]
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
    pais_selecionado = request.GET.get('pais')
    
    context = {
        'aluno_logado': False,
        'pais_selecionado': pais_selecionado
    }

    # Verifica se o aluno está logado
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except AttributeError:
            pass

    # Monta lista de categorias com cursos publicados (Otimizado)
    cursos_qs = Curso.objects.filter(publicado=True).select_related('categoria', 'centro').order_by('-destaque', 'data_inicio')
    if pais_selecionado:
        cursos_qs = cursos_qs.filter(centro__pais=pais_selecionado)
    
    from collections import defaultdict
    grupos = defaultdict(list)
    for c in cursos_qs:
        if c.categoria:
            grupos[c.categoria].append(c)
            
    categorias_com_cursos = []
    for cat, cursos_list in grupos.items():
        categorias_com_cursos.append({
            'categoria': cat,
            'cursos': cursos_list,
            'total_cursos': len(cursos_list)
        })
    
    # Ordenar por nome da categoria
    categorias_com_cursos.sort(key=lambda x: x['categoria'].nome)

    cursos_destaque = Curso.objects.filter(
        destaque=True, publicado=True, ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    # Lista simples de cursos para animação
    cursos_animacao = [c.titulo for c in cursos_qs[:50]] # Limitando para performance

    # Atualiza o contexto com os dados
    context.update({
        'categorias_com_cursos': categorias_com_cursos,
        'cursos_animacao': cursos_animacao
    })

    return render(request, 'todo_curso.html', context)
    
@login_required(login_url='login_aluno')
def ficha_inscricao(request, curso_id):
    if request.user.tipo_usuario != 'ALUNO':
        messages.error(request, "Você precisa estar logado como aluno.")
        return redirect('login_aluno')

    curso = get_object_or_404(Curso, id=curso_id)

    # Verificar se curso está lotado, se não possui turmas ativas ou se inscrições estão fechadas
    if curso.lotado or not curso.possui_turmas_ativas or not curso.inscricoes_abertas:
        if curso.lotado:
            messages.error(request, "Este curso não possui mais vagas disponíveis.")
        elif not curso.possui_turmas_ativas:
            messages.error(request, "Este curso não possui turmas ativas planejadas de momento.")
        else:
            messages.error(request, "As inscrições para este curso estão encerradas.")
        return redirect('curso_detalhe', id=curso_id)

    aluno = None
    try:
        aluno = request.user.aluno_profile
    except AttributeError:
        messages.error(request, "Perfil de aluno não encontrado.")
        return redirect('login_aluno')

    # Obter turmas disponíveis
    turmas_disponiveis = curso.turmas.filter(status='ABERTA', vagas_disponiveis__gt=0)
    turma_disponivel = curso.get_turma_menos_lotada()

    contexto = {
        'curso': curso,
        'aluno': aluno,
        'turma_disponivel': turma_disponivel,
        'turmas_disponiveis': turmas_disponiveis,
        'valor_total': curso.preco_atual,
    }

    return render(request, 'cursos/confirmar_inscricao.html', contexto)


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
            Q(instrutor__nome__icontains=termo)
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

    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
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
        except AttributeError:
            pass

    return render(request, 'resultados_busca.html', context)




@require_POST
def toggle_favorito(request):
    """API to toggle favorite status for a course"""
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'status': 'error', 'message': 'Não autorizado'}, status=403)
    
    import json
    try:
        data = json.loads(request.body)
        curso_id = data.get('curso_id')
        curso = Curso.objects.get(id=curso_id)
        aluno = request.user.aluno_profile
        
        favorito, created = Favorito.objects.get_or_create(aluno=aluno, curso=curso)
        
        if not created:
            favorito.delete()
            return JsonResponse({'status': 'removed'})
        
        return JsonResponse({'status': 'added'})
        
    except Curso.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Curso não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def api_load_more_cursos(request):
    """
    API to load more courses for infinite scroll/pagination.
    Supports filtering.
    """
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 4))
        tipo_filtro = request.GET.get('tipo', 'recentes') # recentes, populares, avaliados, categoria
        categoria_slug = request.GET.get('categoria', None)
        
        qs = Curso.objects.filter(publicado=True, ativo=True)
        
        if categoria_slug:
            qs = qs.filter(categoria__slug=categoria_slug)
            
        if tipo_filtro == 'populares':
            qs = qs.order_by('-visualizacoes')
        elif tipo_filtro == 'avaliados':
            qs = qs.annotate(media=Avg('comentarios__avaliacao')).order_by('-media')
        else: # recentes default
            qs = qs.order_by('-data_criacao')
            
        cursos = qs[offset:offset+limit]
        
        data = []
        # Check favorites if logged in
        favoritos = []
        if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
             favoritos = list(Favorito.objects.filter(
                 aluno=request.user.aluno_profile, 
                 curso__in=cursos
             ).values_list('curso_id', flat=True))

        for curso in cursos:
            data.append({
                'id': curso.id,
                'titulo': curso.titulo,
                'imagem_url': curso.imagem.url if curso.imagem else '/static/assets/images/course/default-course.jpg', # Fallback needed
                'preco': float(curso.preco),
                'centro_nome': curso.centro.nome,
                'visualizacoes': curso.visualizacoes,
                'is_favorito': curso.id in favoritos,
                'url_detalhe': reverse('curso_detalhe', args=[curso.id])
            })
            
        return JsonResponse({'cursos': data, 'has_more': qs.count() > offset + limit})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_buscar_sugestoes(request):
    """
    API para retornar sugestões de cursos ou centros em tempo real (autocomplete).
    """
    termo = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', 'curso')
    if not termo or len(termo) < 1:
        return JsonResponse({'sugestoes': []})
    
    sugestoes = []
    
    if tipo == 'centro':
        from gestoreduka.models import CentroDeFormacao
        centros = CentroDeFormacao.objects.filter(ativo=True).filter(
            Q(nome__icontains=termo) |
            Q(cidade__icontains=termo) |
            Q(provincia__icontains=termo)
        )[:8]
        for c in centros:
            sugestoes.append({
                'id': c.id,
                'titulo': c.nome,
                'centro': c.cidade or c.provincia,
                'url': reverse('cursos_por_centro', kwargs={'centro_id': c.id})
            })
    else:
        cursos = Curso.objects.filter(
            publicado=True, 
            ativo=True
        ).filter(
            Q(titulo__icontains=termo) |
            Q(centro__nome__icontains=termo)
        ).select_related('centro').only('id', 'titulo', 'centro__nome')[:8]
        
        for curso in cursos:
            sugestoes.append({
                'id': curso.id,
                'titulo': curso.titulo,
                'centro': curso.centro.nome if curso.centro else '',
                'url': reverse('curso_detalhe', kwargs={'id': curso.id})
            })
    
    return JsonResponse({'sugestoes': sugestoes})

def lista_centros(request):
    """
    Página que lista todos os Centros de Formação ativos agrupados por sessões.
    """
    from gestoreduka.models import CentroDeFormacao, CategoriaCentro
    
    query = request.GET.get('q', '')
    provincia = request.GET.get('provincia', '')
    
    centros_qs = CentroDeFormacao.objects.filter(ativo=True).select_related('perfil').annotate(
        total_cursos=Count('cursos', filter=Q(cursos__publicado=True, cursos__ativo=True))
    )
    
    if query:
        centros_qs = centros_qs.filter(
            Q(nome__icontains=query) | 
            Q(cidade__icontains=query) |
            Q(endereco__icontains=query)
        )
        
    if provincia:
        centros_qs = centros_qs.filter(provincia=provincia)

    # --- Sessões Temáticas ---
    sessoes = []

    # 1. Centros de Tecnologia
    centros_tech = centros_qs.filter(
        Q(categorias__slug__icontains='tecnologia') | 
        Q(categorias__slug__icontains='informatica')
    ).distinct()[:8]
    if centros_tech.exists():
        sessoes.append({
            'titulo': _('Centros de Tecnologia'),
            'subtitulo': _('As melhores instituições para carreiras digitais'),
            'centros': centros_tech,
            'icone': 'feather-monitor'
        })

    # 2. Centros de Línguas
    centros_linguas = centros_qs.filter(
        Q(categorias__slug__icontains='lingua') | 
        Q(categorias__slug__icontains='idioma')
    ).distinct()[:8]
    if centros_linguas.exists():
        sessoes.append({
            'titulo': _('Centros de Línguas'),
            'subtitulo': _('Aprenda novos idiomas com especialistas'),
            'centros': centros_linguas,
            'icone': 'feather-globe'
        })

    # 3. Centros em Destaque (Sessão Geral)
    centros_destaque = centros_qs.filter(perfil__destaque=True).distinct()[:8]
    if centros_destaque.exists():
        sessoes.append({
            'titulo': _('Instituições em Destaque'),
            'subtitulo': _('Centros parceiros com alto índice de satisfação'),
            'centros': centros_destaque,
            'icone': 'feather-award'
        })

    # Os 3 primeiros centros para o banner Swiper
    centros_banner = CentroDeFormacao.objects.filter(ativo=True).select_related('perfil').annotate(
        total_cursos=Count('cursos', filter=Q(cursos__publicado=True, cursos__ativo=True))
    ).order_by('-perfil__destaque', 'data_criacao')[:3]
    
    # Paginação para a lista geral (Todos os Centros)
    paginator = Paginator(centros_qs.order_by('-perfil__destaque', 'data_criacao'), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    provincias = [
        "Bengo", "Benguela", "Bié", "Cabinda", "Cuando Cubango", "Cuanza Norte", 
        "Cuanza Sul", "Cunene", "Huambo", "Huíla", "Luanda", "Lunda Norte", 
        "Lunda Sul", "Malanje", "Moxico", "Namibe", "Uíge", "Zaire"
    ]
    
    context = {
        'page_obj': page_obj,
        'sessoes': sessoes,
        'centros_banner': centros_banner,
        'q': query,
        'provincia_selecionada': provincia,
        'provincias': provincias,
        'total_centros': centros_qs.count(),
    }
    
    return render(request, 'lista_instituicoes.html', context)

def api_centros_proximos(request):
    """
    API que retorna os centros de formação mais próximos (raio de 30km)
    baseado em latitude e longitude.
    """
    import math
    from gestoreduka.models import CentroDeFormacao
    
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    provincia = request.GET.get('provincia')
    
    todos_centros = CentroDeFormacao.objects.filter(ativo=True).select_related('perfil').annotate(
        total_cursos_count=Count('cursos', filter=Q(cursos__publicado=True, cursos__ativo=True))
    )
    
    centros_proximos = []
    
    if user_lat and user_lng:
        try:
            user_lat = float(user_lat)
            user_lng = float(user_lng)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Coordenadas inválidas'}, status=400)
            
        radius = 30.0 # km
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        for centro in todos_centros:
            c_lat = centro.latitude
            c_lng = centro.longitude
            
            if c_lat and c_lng:
                dist = haversine(user_lat, user_lng, c_lat, c_lng)
                if dist <= radius:
                    centros_proximos.append({
                        'id': centro.id,
                        'nome': centro.nome,
                        'distancia': round(dist, 1),
                        'cidade': centro.cidade or centro.provincia,
                        'url': reverse('cursos_por_centro', kwargs={'centro_id': centro.id}),
                        'banner': centro.perfil.banner.url if centro.perfil and centro.perfil.banner else '/static/assets/images/bg/bg-image-10.jpg',
                        'imagem': centro.perfil.imagem.url if centro.perfil and centro.perfil.imagem else '/static/assets/images/client/client-01.png',
                        'verificado': centro.perfil.verificado if centro.perfil else False,
                        'total_cursos': centro.total_cursos_count
                    })
        
        centros_proximos.sort(key=lambda x: x['distancia'])
        
    elif provincia:
        centros_prov = todos_centros.filter(provincia__icontains=provincia)[:6]
        for centro in centros_prov:
            centros_proximos.append({
                'id': centro.id,
                'nome': centro.nome,
                'distancia': None,
                'cidade': centro.cidade or centro.provincia,
                'url': reverse('cursos_por_centro', kwargs={'centro_id': centro.id}),
                'banner': centro.perfil.banner.url if centro.perfil and centro.perfil.banner else '/static/assets/images/bg/bg-image-10.jpg',
                'imagem': centro.perfil.imagem.url if centro.perfil and centro.perfil.imagem else '/static/assets/images/client/client-01.png',
                'verificado': centro.perfil.verificado if centro.perfil else False,
                'total_cursos': centro.total_cursos_count
            })
    else:
        return JsonResponse({'error': 'Coordenadas ou província necessárias'}, status=400)
    
    return JsonResponse({'centros': centros_proximos[:6]})


def api_mapa_global(request):
    """
    Retorna todos os centros e filiais ativos para visualização no mapa global.
    """
    from gestoreduka.models import CentroDeFormacao, Filial
    from django.db.models import Count, Q
    
    pontos = []
    
    # 1. Obter Centros Principais
    centros = CentroDeFormacao.objects.filter(ativo=True).select_related('perfil').annotate(
        total_cursos_count=Count('cursos', filter=Q(cursos__publicado=True, cursos__ativo=True))
    )
    
    for c in centros:
        if c.latitude and c.longitude:
            pontos.append({
                'id': f"c_{c.id}",
                'nome': c.nome,
                'lat': float(c.latitude),
                'lng': float(c.longitude),
                'tipo': 'CENTRO',
                'cidade': c.cidade or c.provincia,
                'url': reverse('cursos_por_centro', kwargs={'centro_id': c.id}),
                'imagem': c.perfil.imagem.url if c.perfil and c.perfil.imagem else '/static/assets/images/client/client-01.png',
                'total_cursos': c.total_cursos_count,
                'verificado': c.perfil.verificado if c.perfil else False
            })
            
    # 2. Obter Filiais
    filiais = Filial.objects.filter(ativo=True).select_related('centro_principal', 'centro_principal__perfil')
    
    for f in filiais:
        if f.latitude and f.longitude:
            pontos.append({
                'id': f"f_{f.id}",
                'nome': f.nome,
                'lat': float(f.latitude),
                'lng': float(f.longitude),
                'tipo': 'FILIAL',
                'cidade': f.endereco.split(',')[-1].strip() if ',' in f.endereco else f.nome,
                'url': reverse('cursos_por_centro', kwargs={'centro_id': f.centro_principal.id}),
                'imagem': f.centro_principal.perfil.imagem.url if f.centro_principal.perfil and f.centro_principal.perfil.imagem else '/static/assets/images/client/client-01.png',
                'total_cursos': 0, # Filiais podem não ter cursos próprios no momento
                'verificado': f.centro_principal.perfil.verificado if f.centro_principal.perfil else False
            })
            
    return JsonResponse({'pontos': pontos})


@login_required(login_url='login_aluno')
def gerar_comprovante_inscricao(request, inscricao_id):
    """Gera um PDF da ficha de inscrição"""
    inscricao = get_object_or_404(Inscricao, id=inscricao_id)
    
    # Verificar permissão (apenas o próprio aluno ou gestor do centro)
    if request.user.tipo_usuario == 'ALUNO':
        if inscricao.aluno.usuario != request.user:
            messages.error(request, "Você não tem permissão para baixar este comprovante.")
            return redirect('aluno_dashboard')
    elif request.user.tipo_usuario == 'GESTOR':
        if inscricao.curso.centro.usuario != request.user:
            messages.error(request, "Você não tem permissão para baixar este comprovante.")
            return redirect('dashboard_gestor')
    
    if HTML is None:
        messages.error(request, "A funcionalidade de PDF não está disponível no servidor.")
        return redirect('aluno_dashboard')

    # Obter caminho absoluto do logo para o WeasyPrint (versão ícone da tela de carregamento)
    logo_path = finders.find('assets/images/logo/logo1.png') or finders.find('assets/images/logo/logo1-removebg-preview.png')
    
    # Caminho absoluto da imagem do centro
    centro_logo_path = None
    if inscricao.curso.centro.perfil and inscricao.curso.centro.perfil.imagem:
        centro_logo_path = inscricao.curso.centro.perfil.imagem.path
    
    # Renderizar HTML
    html_string = render_to_string('cursos/comprovante_inscricao.html', {
        'inscricao': inscricao,
        'request': request,
        'logo_path': logo_path,
        'centro_logo_path': centro_logo_path,
    })

    # Gerar PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    # Retornar resposta
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ficha_inscricao_{inscricao.id}.pdf"'
    
    return response
