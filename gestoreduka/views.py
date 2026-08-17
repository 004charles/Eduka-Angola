import re
import os
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q, Sum, Count, Value
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
# from django.contrib.gis.geos import Point
# from django.contrib.gis.measure import D
# from django.contrib.gis.db.models.functions import Distance

from .models import (
    CentroDeFormacao, PerfilCentroDeFormacao, Certificacao, 
    Diferencial, AreaFormacao, Equipe, Recurso, Depoimento,
    Estatistica, Parceria, Evento, GaleriaImagem, ReelCentro,
    Filial, ConviteCentro, Conversa, Mensagem, CentroSeguimento,
    CategoriaCentro, AnuncioCentro, EventoIntegracao, AuditoriaCentro
)
from cursos_app.models import Curso, Categoria, Instrutor, Inscricao, Turma, Presenca, NotaAluno, Matricula, ParcelaMatricula
from pagamentos.models import RecebimentoCentro
from planos.models import AssinaturaMembro, Plano
from usuarios.models import Aluno
from core.notification_events import queue_notification_event
from usuarios.decorators import aluno_logado_e_centros
from .forms import CursoForm, AnuncioForm
from .plan_permissions import permite, get_plano_ativo, limite

@aluno_logado_e_centros
def buscar_centros(request):
    """
    View principal para busca espacial de centros de formação.
    Usa lógica GeoDjango se disponível, com fallback para lista simples.
    """
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lng')
    raio = request.GET.get('raio', 10)  # Default 10km
    
    try:
        raio = float(raio)
    except (ValueError, TypeError):
        raio = 10
    
    q = request.GET.get('q')
    cat_slug = request.GET.get('categoria')
    
    centros = CentroDeFormacao.objects.filter(ativo=True)
    
    # Filtrar por categoria
    if cat_slug:
        centros = centros.filter(categorias__slug=cat_slug)
    
    # Se pesquisar por curso, filtrar os centros que oferecem o curso
    if q:
        centros = centros.filter(
            Q(cursos__titulo__icontains=q) | 
            Q(nome__icontains=q)
        ).distinct()

    categorias = CategoriaCentro.objects.filter(ativa=True)

    context = {
        'centros': centros,
        'q': q,
        'categorias': categorias,
        'categoria_selecionada': cat_slug,
        'latitude': latitude,
        'longitude': longitude,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }
    
    # Se tiver coordenadas, calcular distância
    if latitude and longitude:
        try:
            lat = float(latitude)
            lng = float(longitude)
            if not getattr(settings, 'USE_SQLITE', False):
                try:
                    from django.contrib.gis.geos import Point
                    from django.contrib.gis.measure import D
                    from django.contrib.gis.db.models.functions import Distance
                    
                    user_location = Point(lng, lat, srid=4326)
                    
                    # Filtra centros num raio configurável e anota a distância
                    # Prioriza por Plano (Assinatura) e depois por distância
                    centros = centros.annotate(
                        distance=Distance('localizacao', user_location),
                        priority=Coalesce('assinatura__plano__prioridade_busca', Value(0))
                    ).filter(
                        localizacao__distance_lte=(user_location, D(km=raio))
                    ).order_by('-priority', 'distance')
                except Exception:
                     # Fallback para SQLite se falhar importação ou query
                     centros = centros.annotate(
                        priority=Coalesce('assinatura__plano__prioridade_busca', Value(0))
                    ).order_by('-priority', 'nome')
            else:
                 # Fallback para SQLite (apenas ordenação simples)
                 centros = centros.annotate(
                    priority=Coalesce('assinatura__plano__prioridade_busca', Value(0))
                ).order_by('-priority', 'nome')
            
        except (ValueError, TypeError) as e:
            print(f"Erro nas coordenadas: {e}")
            pass
    
    # Atualizar centros no contexto após filtros geo
    context['centros'] = centros
            
    return render(request, 'core/buscar_centros.html', context)

@login_required
def seguir_centro_ajax(request, centro_id):
    """
    Endpoint AJAX para seguir ou deixar de seguir um centro.
    """
    if request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'error': 'Apenas alunos podem seguir centros.'}, status=403)
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id)
    aluno = request.user.aluno_profile
    
    seguimento, created = CentroSeguimento.objects.get_or_create(aluno=aluno, centro=centro)
    
    if not created:
        seguimento.delete()
        return JsonResponse({'seguindo': False, 'mensagem': f'Deixaste de seguir {centro.nome}'})
    
    return JsonResponse({'seguindo': True, 'mensagem': f'Agora segues {centro.nome}'})



def get_gestor_context(user):
    """
    Helper function to get the centro and filial based on the user's role.
    Returns (centro, filial) or (None, None) if not found.
    """
    try:
        if user.tipo_usuario == 'GESTOR_FILIAL':
            filial = user.filial_profile
            centro = filial.centro_principal
            return centro, filial
        elif user.tipo_usuario in ['GESTOR', 'ADMIN', 'ALUNO'] or user.is_superuser:
            # Tentar pegar o centro, se falhar (ObjectDoesNotExist), retorna None
            try:
                centro = user.centro_profile
                return centro, None
            except Exception:
                return None, None
    except Exception:
        pass
    return None, None

@login_required
def perfil_institucional_interno(request):
    """
    Visualização interna premium do perfil do centro (estilo portfólio/Works).
    """
    centro, filial = get_gestor_context(request.user)
    
    if not centro:
        messages.error(request, "Perfil do centro não encontrado.")
        return redirect('centro_dashboard')

    # Dados para o layout Works
    try:
        perfil = centro.perfil
    except:
        perfil = None

    cursos = centro.cursos.all().order_by('-destaque', '-data_criacao')
    instrutores = Instrutor.objects.filter(centro_de_formacao=centro, ativo=True)
    galeria = centro.galeria_imagens.all().order_by('ordem')
    seguidores_count = centro.seguidores.count()

    context = {
        'centro': centro,
        'filial': filial,
        'perfil': perfil,
        'cursos': cursos,
        'instrutores': instrutores,
        'galeria': galeria,
        'seguidores_count': seguidores_count,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
    }

    return render(request, 'perfil_interno.html', context)

def centro_dashboard(request):
    """
    Dashboard principal do Gestor exibindo métricas de desempenho do centro e atividades recentes.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar o dashboard.")
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        messages.error(request, "Esta conta não tem permissões de Gestor ou o perfil não foi encontrado.")
        return redirect('login_gestor')
        
    from datetime import timedelta
    # Estatísticas Gerais (Filtrar por filial se aplicável)
    cursos_qs = filial.cursos_disponiveis.all() if filial else centro.cursos.all()
    total_cursos = cursos_qs.count()
    total_cursos_ativos = cursos_qs.filter(ativo=True).count()
    
    inscricoes_qs = Inscricao.objects.filter(curso__centro=centro)
    if filial:
        inscricoes_qs = inscricoes_qs.filter(curso__filiais=filial)
        
    total_inscricoes = inscricoes_qs.count()
    inscricoes_pendentes = inscricoes_qs.filter(status='P').count()
    
    # Receita Real (baseada em pagamentos confirmados)
    receita_total = inscricoes_qs.filter(
        status='A'
    ).aggregate(total=Sum('valor_pago'))['total'] or 0

    # Módulo 1.1: Total de inscrições do mês actual, com comparação percentual face ao mês anterior
    hoje = timezone.now()
    primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if primeiro_dia_mes.month == 1:
        primeiro_dia_mes_anterior = primeiro_dia_mes.replace(year=primeiro_dia_mes.year - 1, month=12)
    else:
        primeiro_dia_mes_anterior = primeiro_dia_mes.replace(month=primeiro_dia_mes.month - 1)

    inscricoes_mes_atual = inscricoes_qs.filter(data_inscricao__gte=primeiro_dia_mes).count()
    inscricoes_mes_anterior = inscricoes_qs.filter(
        data_inscricao__gte=primeiro_dia_mes_anterior, 
        data_inscricao__lt=primeiro_dia_mes
    ).count()

    if inscricoes_mes_anterior > 0:
        crescimento_inscricoes = ((inscricoes_mes_atual - inscricoes_mes_anterior) / inscricoes_mes_anterior) * 100
    else:
        crescimento_inscricoes = 100.0 if inscricoes_mes_atual > 0 else 0.0

    # Receita total gerada via plataforma no mês corrente, com comparação percentual
    receita_mes_atual = inscricoes_qs.filter(
        status='A', 
        data_confirmacao__gte=primeiro_dia_mes
    ).aggregate(total=Sum('valor_pago'))['total'] or 0

    receita_mes_anterior = inscricoes_qs.filter(
        status='A', 
        data_confirmacao__gte=primeiro_dia_mes_anterior, 
        data_confirmacao__lt=primeiro_dia_mes
    ).aggregate(total=Sum('valor_pago'))['total'] or 0

    if receita_mes_anterior > 0:
        crescimento_receita = ((receita_mes_atual - receita_mes_anterior) / receita_mes_anterior) * 100
    else:
        crescimento_receita = 100.0 if receita_mes_atual > 0 else 0.0

    # Total de vagas ainda disponíveis e taxa de ocupação média
    vagas_totais_disponiveis = 0
    vagas_ocupadas_totais = 0
    vagas_capacidade_total = 0
    
    for c in cursos_qs.filter(ativo=True):
        vagas_totais_disponiveis += c.total_vagas_disponiveis
        vagas_ocupadas_totais += c.vagas_ocupadas
        vagas_capacidade_total += c.total_vagas_totais

    if vagas_capacidade_total > 0:
        taxa_ocupacao_media = (vagas_ocupadas_totais / vagas_capacidade_total) * 100
    else:
        taxa_ocupacao_media = 0.0

    # Avaliação média do centro (sistema de estrelas baseado nos reviews dos alunos)
    from django.db.models import Avg
    from avaliacoes.models import Comentario
    comentarios_centro = Comentario.objects.filter(
        Q(curso__centro=centro) | Q(curso_video__instrutor__centro_de_formacao=centro)
    )
    if filial:
        comentarios_centro = comentarios_centro.filter(
            Q(curso__filiais=filial) | Q(curso_video__instrutor__filial=filial)
        )
    avaliacao_media = comentarios_centro.aggregate(media=Avg('avaliacao'))['media'] or 0.0
    avaliacao_media = round(avaliacao_media, 1)

    # Número de certificados emitidos no mês
    from cursovideoapp.models import Certificado
    certificados_mes = Certificado.objects.filter(
        curso__instrutor__centro_de_formacao=centro,
        data_emissao__gte=primeiro_dia_mes
    )
    if filial:
        certificados_mes = certificados_mes.filter(curso__instrutor__filial=filial)
    total_certificados_mes = certificados_mes.count()
    
    # Meta de cursos (exemplo baseado no plano)
    assinatura = getattr(centro, 'assinatura', None)
    limite_cursos = assinatura.plano.limite_cursos if assinatura and assinatura.plano else 5
    
    # Cursos Populares
    cursos_populares = cursos_qs.annotate(
        num_alunos=Count('inscricoes', filter=Q(inscricoes__status='A'))
    ).order_by('-num_alunos')[:4]
    
    # Inscrições Recentes
    recent_enrollments = inscricoes_qs.select_related('aluno', 'curso').order_by('-data_inscricao')[:6]

    # Módulo 1.2: Alertas activos (Ex: Inscrições pendentes há mais de 48h, vagas em níveis críticos, ou novos comentários não respondidos)
    alertas = []
    # 1. Inscrições pendentes há mais de 48h
    limite_48h = hoje - timedelta(hours=48)
    pendentes_criticas = inscricoes_qs.filter(status='P', data_inscricao__lt=limite_48h).count()
    if pendentes_criticas > 0:
        alertas.append({
            'tipo': 'danger',
            'titulo': 'Matrículas Atrasadas',
            'mensagem': f'Tens {pendentes_criticas} inscrições pendentes há mais de 48 horas aguardando verificação.',
            'link': reverse('gerenciar_inscricoes') + '?status=P'
        })
    
    # 2. Vagas em níveis críticos (ex: lotação > 90% ou vagas disponíveis < 3 em turmas abertas)
    turmas_criticas = Turma.objects.filter(curso__centro=centro, status='ABERTA')
    if filial:
        turmas_criticas = turmas_criticas.filter(curso__filiais=filial)
    
    count_turmas_criticas = 0
    for t in turmas_criticas:
        if t.vagas_disponiveis <= 3:
            count_turmas_criticas += 1
            
    if count_turmas_criticas > 0:
        alertas.append({
            'tipo': 'warning',
            'titulo': 'Capacidade Crítica',
            'mensagem': f'Tens {count_turmas_criticas} turma(s) com 3 ou menos vagas disponíveis. Considera abrir novas turmas!',
            'link': reverse('gerenciar_turmas')
        })

    # 3. Novos comentários ou dúvidas não respondidos
    from avaliacoes.models import Comentario
    comentarios_nao_respondidos = Comentario.objects.filter(
        Q(curso__centro=centro) | Q(curso_video__instrutor__centro_de_formacao=centro),
        resposta__isnull=True
    )
    if filial:
        comentarios_nao_respondidos = comentarios_nao_respondidos.filter(
            Q(curso__filiais=filial) | Q(curso_video__instrutor__filial=filial)
        )
    count_comentarios_nao_respondidos = comentarios_nao_respondidos.count()
    if count_comentarios_nao_respondidos > 0:
        alertas.append({
            'tipo': 'info',
            'titulo': 'Dúvidas Pendentes',
            'mensagem': f'Tens {count_comentarios_nao_respondidos} novos comentários/dúvidas de alunos sem resposta.',
            'link': reverse('gerenciar_comentarios')
        })

    # Gráfico do desempenho mensal (últimos 6 meses)
    dados_grafico = []
    for i in range(5, -1, -1):
        # Mês a calcular
        mes_data = hoje - timedelta(days=i*30)
        # Obter primeiro e último dia desse mês
        m_start = mes_data.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if m_start.month == 12:
            m_end = m_start.replace(year=m_start.year + 1, month=1, day=1)
        else:
            m_end = m_start.replace(month=m_start.month + 1, day=1)
            
        inscs = inscricoes_qs.filter(data_inscricao__gte=m_start, data_inscricao__lt=m_end).count()
        rev = inscricoes_qs.filter(status='A', data_confirmacao__gte=m_start, data_confirmacao__lt=m_end).aggregate(total=Sum('valor_pago'))['total'] or 0
        
        # Nome do mês em português
        meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        nome_mes = meses_nomes[m_start.month - 1]
        
        dados_grafico.append({
            'mes': f"{nome_mes} {m_start.year}",
            'inscricoes': inscs,
            'receita': float(rev)
        })
    
    context = {
        'centro': centro,
        'filial': filial,
        'is_filial': filial is not None,
        'stats': {
            'total_cursos': total_cursos,
            'total_cursos_ativos': total_cursos_ativos,
            'total_inscricoes': total_inscricoes,
            'inscricoes_pendentes': inscricoes_pendentes,
            'receita_total': receita_total,
            'limite_cursos': limite_cursos,
            'percentual_cursos': (total_cursos / limite_cursos * 100) if limite_cursos > 0 else 0,
            'total_seguidores': centro.seguidores.count(),
            
            # Novos campos Módulo 1.1
            'inscricoes_mes_atual': inscricoes_mes_atual,
            'crescimento_inscricoes': crescimento_inscricoes,
            'receita_mes_atual': receita_mes_atual,
            'crescimento_receita': crescimento_receita,
            'vagas_totais_disponiveis': vagas_totais_disponiveis,
            'taxa_ocupacao_media': round(taxa_ocupacao_media, 1),
            'avaliacao_media': avaliacao_media,
            'total_certificados_mes': total_certificados_mes
        },
        'cursos_populares': cursos_populares,
        'recent_enrollments': recent_enrollments,
        'assinatura': assinatura,
        'alertas': alertas,
        'dados_grafico': json.dumps(dados_grafico)
    }
    
    return render(request, 'centro_dashboard.html', context)

@login_required
def listar_seguidores(request):
    """
    Lista os alunos que seguem o centro de formação.
    """
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    from gestoreduka.models import CentroSeguimento
    seguidores = CentroSeguimento.objects.filter(centro=centro).select_related('aluno__usuario', 'aluno__perfil').order_by('-data_seguimento')
    
    # Pesquisa simples
    q = request.GET.get('q', '')
    if q:
        seguidores = seguidores.filter(
            Q(aluno__usuario__nome__icontains=q) | 
            Q(aluno__usuario__email__icontains=q)
        )
        
    # Paginação
    paginator = Paginator(seguidores, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'gestor/seguidores.html', {
        'centro': centro,
        'filial': filial,
        'page_obj': page_obj,
        'q': q,
        'total_seguidores': seguidores.count()
    })

@login_required
def gerenciar_inscricoes(request):
    """
    View para o gestor gerenciar todas as inscrições do centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

        
    if request.method == 'POST':
        action = request.POST.get('action')
        inscricao_id = request.POST.get('inscricao_id')
        if action and inscricao_id:
            from django.shortcuts import get_object_or_404
            from django.contrib import messages
            inscricoes_qs = Inscricao.objects.filter(curso__centro=centro)
            if filial:
                inscricoes_qs = inscricoes_qs.filter(curso__filiais=filial)
            inscricao = get_object_or_404(inscricoes_qs, id=inscricao_id)
            if action == 'approve':
                inscricao.status = 'A'
                inscricao.save()
                messages.success(request, f"Inscrição de {inscricao.aluno.nome} aprovada com sucesso!")
            elif action == 'reject':
                inscricao.status = 'N'
                inscricao.save()
                messages.success(request, f"Inscrição de {inscricao.aluno.nome} rejeitada com sucesso!")
            return redirect(request.path_info + ('?' + request.META.get('QUERY_STRING', '') if request.META.get('QUERY_STRING') else ''))

    inscricoes_qs = Inscricao.objects.filter(curso__centro=centro)
    if filial:
        inscricoes_qs = inscricoes_qs.filter(curso__filiais=filial)

    # Calculate statistics before filtering
    total_count = inscricoes_qs.count()
    pendentes_count = inscricoes_qs.filter(status='P').count()
    aprovadas_count = inscricoes_qs.filter(status='A').count()
    rejeitadas_count = inscricoes_qs.filter(status='N').count()
        
    inscricoes_list = inscricoes_qs.select_related('aluno', 'curso', 'turma_escolhida').order_by('-data_inscricao')
    
    # Filtros
    status = request.GET.get('status')
    if status:
        db_status = 'N' if status == 'R' else status
        inscricoes_list = inscricoes_list.filter(status=db_status)
    
    paginator = Paginator(inscricoes_list, 15)
    page_number = request.GET.get('page')
    inscricoes = paginator.get_page(page_number)
    
    prontu_payment_link = request.session.pop('prontu_payment_link', None)
    
    return render(request, 'gestor/inscricoes.html', {
        'centro': centro,
        'filial': filial,
        'inscricoes': inscricoes,
        'selected_status': status,
        'total_count': total_count,
        'pendentes_count': pendentes_count,
        'aprovadas_count': aprovadas_count,
        'rejeitadas_count': rejeitadas_count,
        'cursos_ativos': Curso.objects.filter(centro=centro, publicado=True, ativo=True) if not filial else Curso.objects.filter(filiais=filial, publicado=True, ativo=True),
        'turmas_ativas': Turma.objects.filter(curso__centro=centro, status__in=['ABERTA', 'EM_ANDAMENTO']).select_related('curso').order_by('data_inicio'),
        'formas_pagamento': Inscricao.FORMA_PAGAMENTO_CHOICES,
        'origens_matricula': Matricula.ORIGEM_CHOICES,
        'prontu_payment_link': prontu_payment_link
    })

from django.views.decorators.http import require_POST
from usuarios.models import Aluno
from django.contrib.auth import get_user_model

@require_POST
def matricular_aluno_manual(request):
    """Regista uma matrícula presencial completa no centro."""
    if not request.user.is_authenticated:
        return redirect('login_gestor')

    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')

    if not permite(centro, 'permite_inscricao_manual', permitir_periodo_teste=True):
        messages.error(request, 'O seu plano atual não permite inscrições manuais. Atualize a subscrição para continuar.')
        return redirect('gerenciar_assinatura')

    curso_id = request.POST.get('curso_id')

    turma_id = request.POST.get('turma_id')
    nome = request.POST.get('nome', '').strip()
    email = request.POST.get('email', '').strip().lower()
    telefone = request.POST.get('telefone', '').strip()
    origem = request.POST.get('origem', 'PRESENCIAL')
    forma_pagamento = request.POST.get('forma_pagamento', 'DINHEIRO')
    pagamento_confirmado = request.POST.get('pagamento_confirmado') == 'on'

    try:
        curso = Curso.objects.get(id=curso_id, centro=centro)
        turma = Turma.objects.get(id=turma_id, curso=curso)
        if filial and not curso.filiais.filter(pk=filial.pk).exists():
            messages.error(request, 'Esta turma não pertence à filial selecionada.')
            return redirect('gerenciar_inscricoes')
        if not nome or not email:
            messages.error(request, 'Nome e email são obrigatórios para criar a ficha do aluno.')
            return redirect('gerenciar_inscricoes')
        if turma.status in ('CONCLUIDA', 'CANCELADA'):
            messages.error(request, 'Não é possível matricular alunos numa turma encerrada ou cancelada.')
            return redirect('gerenciar_inscricoes')
        if turma.vagas_disponiveis <= 0:
            messages.error(request, 'A turma selecionada não tem vagas disponíveis.')
            return redirect('gerenciar_inscricoes')

        User = get_user_model()
        user, _ = User.objects.get_or_create(email=email, defaults={
            'nome': nome,
            'is_active': False,
            'tipo_usuario': 'ALUNO',
        })
        if not user.nome:
            user.nome = nome
        if telefone:
            perfil, _ = __import__('usuarios.models', fromlist=['PerfilAluno']).PerfilAluno.objects.get_or_create(
                aluno=Aluno.objects.get_or_create(usuario=user, defaults={'nome': nome})[0]
            )
            perfil.telefone = telefone
            perfil.save(update_fields=['telefone'])
        user.save()
        aluno, _ = Aluno.objects.get_or_create(usuario=user, defaults={'nome': nome})
        aluno.nome = nome
        aluno.save(update_fields=['nome'])

        if Matricula.objects.filter(aluno=aluno, turma=turma, estado__in=['PENDENTE', 'ATIVA', 'SUSPENSA']).exists():
            messages.warning(request, f'O aluno {nome} já possui uma matrícula nesta turma.')
            return redirect('gerenciar_inscricoes')

        valor = request.POST.get('valor_acordado', '') or str(curso.preco_atual or 0)
        desconto = request.POST.get('desconto', '0') or '0'
        try:
            from decimal import Decimal
            valor = Decimal(valor.replace(',', '.'))
            desconto = Decimal(desconto.replace(',', '.'))
        except Exception:
            messages.error(request, 'O valor ou desconto informado não é válido.')
            return redirect('gerenciar_inscricoes')

        inscricao, _ = Inscricao.objects.get_or_create(
            aluno=aluno,
            curso=curso,
            defaults={
                'status': 'A' if pagamento_confirmado else 'P',
                'tipo_inscricao': 'PRESENCIAL',
                'turma_escolhida': turma,
                'forma_pagamento': forma_pagamento,
                'valor_pago': valor if pagamento_confirmado else 0,
                'data_pagamento': timezone.now() if pagamento_confirmado else None,
                'observacoes': 'Registo presencial no GestorEduka',
            },
        )
        if inscricao.turma_escolhida_id != turma.pk:
            inscricao.turma_escolhida = turma
        inscricao.tipo_inscricao = 'PRESENCIAL'
        inscricao.forma_pagamento = forma_pagamento
        inscricao.valor_pago = valor if pagamento_confirmado else (inscricao.valor_pago or 0)
        inscricao.status = 'A' if pagamento_confirmado else 'P'
        if pagamento_confirmado and not inscricao.data_pagamento:
            inscricao.data_pagamento = timezone.now()
        inscricao.save()

        matricula = Matricula.objects.create(
            aluno=aluno,
            curso=curso,
            turma=turma,
            inscricao=inscricao,
            origem=origem if origem in dict(Matricula.ORIGEM_CHOICES) else 'PRESENCIAL',
            estado='ATIVA' if pagamento_confirmado else 'PENDENTE',
            valor_acordado=valor,
            desconto=desconto,
            responsavel=request.user,
            observacoes='Matrícula criada presencialmente pelo centro.',
        )
        from datetime import timedelta
        ParcelaMatricula.objects.create(
            matricula=matricula,
            numero=1,
            descricao='Pagamento inicial da matrícula',
            valor=max(valor - desconto, 0),
            vencimento=timezone.localdate(),
            status='PAGA' if pagamento_confirmado else 'PENDENTE',
            valor_pago=max(valor - desconto, 0) if pagamento_confirmado else 0,
            data_pagamento=timezone.now() if pagamento_confirmado else None,
        )
        if pagamento_confirmado:
            recebimento = RecebimentoCentro.objects.create(
                centro=centro,
                matricula=matricula,
                aluno=aluno,
                valor=max(valor - desconto, 0),
                forma=forma_pagamento if forma_pagamento in dict(RecebimentoCentro.FORMA_CHOICES) else 'OUTRO',
                recebido_por=request.user,
                observacoes='Recebimento registado no atendimento presencial.',
            )
            parcela = matricula.parcelas.first()
            if parcela:
                parcela.recebimento = recebimento
                parcela.save(update_fields=['recebimento'])
            turma.atualizar_vagas_turma()
            AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CRIAR_MATRICULA', entidade='Matricula', objeto_id=str(matricula.pk), dados={'origem': matricula.origem, 'pagamento': True, 'recibo': recebimento.referencia})
            messages.success(request, f'Matrícula {matricula.codigo_matricula} criada e recibo emitido para {nome}.')
        else:
            messages.success(request, f'Pré-matrícula {matricula.codigo_matricula} criada. Aguarda confirmação do pagamento.')
    except (Curso.DoesNotExist, Turma.DoesNotExist):
        messages.error(request, 'Curso ou turma não encontrados.')
    except Exception as exc:
        messages.error(request, f'Erro ao criar matrícula presencial: {exc}')
    return redirect('gerenciar_inscricoes')

from cursos_app.models import CertificadoCurso

@require_POST
def emitir_certificado_manual(request, inscricao_id):
    """
    Gera um certificado para uma inscrição aprovada.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    # Validar Assinatura e Permissão do Plano
    assinatura = getattr(centro, 'assinatura', None)
    if not assinatura or not assinatura.esta_ativa:
        messages.error(request, "A sua assinatura não está ativa. Impossível emitir certificados.")
        return redirect('gerenciar_inscricoes')
        
    if not assinatura.plano or not assinatura.plano.permite_gerar_certificado:
        messages.error(request, "O seu plano atual não permite gerar certificados.")
        return redirect('gerenciar_assinatura')
        
    try:
        inscricoes_qs = Inscricao.objects.filter(curso__centro=centro, status='A')
        if filial:
            inscricoes_qs = inscricoes_qs.filter(curso__filiais=filial)
            
        inscricao = inscricoes_qs.get(id=inscricao_id)
        
        # Validação académica mínima do MVP presencial
        if not inscricao.turma_escolhida:
            messages.error(request, 'O aluno precisa de estar associado a uma turma antes de receber certificado.')
            return redirect('gerenciar_inscricoes')

        registos_presenca = Presenca.objects.filter(turma=inscricao.turma_escolhida, inscricao=inscricao)
        total_presencas = registos_presenca.count()
        presencas_validas = registos_presenca.filter(estado__in=['PRESENTE', 'ATRASO']).count()
        percentagem_presenca = (presencas_validas / total_presencas * 100) if total_presencas else 0
        if total_presencas == 0 or percentagem_presenca < 75:
            messages.error(request, f'Certificado bloqueado: a assiduidade atual é de {percentagem_presenca:.0f}% e o mínimo exigido é 75%.')
            return redirect('gerenciar_inscricoes')

        nota_final = NotaAluno.objects.filter(
            turma=inscricao.turma_escolhida,
            inscricao=inscricao,
            avaliacao='Nota Final',
        ).first()
        if not nota_final or nota_final.nota < 10:
            nota_display = nota_final.nota if nota_final else 'não registada'
            messages.error(request, f'Certificado bloqueado: a nota final é {nota_display}; o mínimo exigido é 10 valores.')
            return redirect('gerenciar_inscricoes')

        # Cria ou devolve o existente
        certificado, created = CertificadoCurso.objects.get_or_create(inscricao=inscricao)

        if created:
            messages.success(request, f"Certificado para {inscricao.aluno.nome} gerado com sucesso!")
        else:
            messages.info(request, f"O certificado para {inscricao.aluno.nome} já estava emitido.")
            
    except Inscricao.DoesNotExist:
        messages.error(request, "Inscrição não encontrada ou não está aprovada.")
    except Exception as e:
        messages.error(request, f"Erro ao emitir certificado: {str(e)}")
        
    return redirect('gerenciar_inscricoes')

def gerenciar_assinatura(request):
    """
    View de monetização: Gestor vê seu plano e pode assinar ou mudar.
    Para filiais, isso geralmente não se aplica, mas será mantido para visualização.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:
        messages.error(request, "Acesso negado. Apenas a Sede pode gerir assinaturas.")
        return redirect('centro_dashboard')
        
    assinatura = getattr(centro, 'assinatura', None)
    planos_disponiveis = Plano.objects.filter(ativo=True).exclude(id=assinatura.plano.id if assinatura and assinatura.plano else None)
    
    return render(request, 'gestor/assinatura.html', {
        'centro': centro,
        'filial': filial,
        'assinatura': assinatura,
        'planos_disponiveis': planos_disponiveis
    })

from django.utils.crypto import get_random_string
from pagamentos.services import PaymentService, PagamentoException
from django.urls import reverse

@login_required
@require_http_methods(["POST"])
def assinar_plano_prontu(request, plano_id):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    plano = get_object_or_404(Plano, id=plano_id, ativo=True)

    # Criar a subscrição pendente antes do checkout para que o webhook
    # consiga ativar a relação correta quando o pagamento for confirmado.
    assinatura, _ = AssinaturaMembro.objects.get_or_create(
        centro=centro,
        defaults={'status': 'PENDENTE'}
    )

    try:
        service = PaymentService()

        pagamento = service.criar_pagamento(
            usuario=request.user,
            tipo_pagamento='ASSINATURA_PLANO',
            valor=plano.preco,
            plano=plano,
            moeda='AOA',
            url_sucesso=request.build_absolute_uri(reverse('gerenciar_assinatura')),
            url_cancelamento=request.build_absolute_uri(reverse('gerenciar_assinatura'))
        )
        return redirect(pagamento.url_pagamento)
        
    except PagamentoException as e:
        messages.error(request, f"Erro ao iniciar pagamento: {str(e)}")
        return redirect('gerenciar_assinatura')
    except Exception as e:
        messages.error(request, "Ocorreu um erro inesperado ao conectar à Prontu.")
        return redirect('gerenciar_assinatura')

def analytics_centro(request):
    """
    Dashboard de análises e métricas detalhadas do centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    
    from datetime import timedelta
    hoje = timezone.now()
    mes_passado = hoje - timedelta(days=30)
    
    inscricoes_qs = Inscricao.objects.filter(curso__centro=centro)
    cursos_qs = centro.cursos.all()
    if filial:
        inscricoes_qs = inscricoes_qs.filter(curso__filiais=filial)
        cursos_qs = filial.cursos_disponiveis.all()
    
    # Receita mensal
    receita_mes = inscricoes_qs.filter(
        status='A',
        data_confirmacao__gte=mes_passado
    ).aggregate(total=Sum('valor_pago'))['total'] or 0
    
    # Crescimento de inscrições
    inscricoes_mes = inscricoes_qs.filter(
        data_inscricao__gte=mes_passado
    ).count()
    
    # Top cursos
    top_cursos = cursos_qs.annotate(
        num_alunos=Count('inscricoes', filter=Q(inscricoes__status='A'))
    ).order_by('-num_alunos')[:5]
    
    total_inscricoes = inscricoes_qs.filter(status='A').count()
    
    context = {
        'centro': centro,
        'filial': filial,
        'receita_mes': receita_mes,
        'inscricoes_mes': inscricoes_mes,
        'top_cursos': top_cursos,
        'total_inscricoes': total_inscricoes,
    }
    
    return render(request, 'gestor/analytics.html', context)

def gerenciar_turmas(request):
    """
    Listagem e gerenciamento de todas as turmas do centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    turmas_qs = Turma.objects.filter(curso__centro=centro)
    if filial:
        turmas_qs = turmas_qs.filter(curso__filiais=filial)
        
    # O centro gere todo o processo; o instrutor não tem painel operacional no MVP.
    turmas = turmas_qs.select_related('curso').order_by('-data_inicio')
    
    paginator = Paginator(turmas, 15)
    page_number = request.GET.get('page')
    turmas_page = paginator.get_page(page_number)
    
    return render(request, 'gestor/turmas/listar.html', {
        'centro': centro,
        'filial': filial,
        'turmas': turmas_page
    })

def criar_turma(request):
    """
    Criação de uma nova turma para um curso do centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    cursos_context = filial.cursos_disponiveis.filter(ativo=True) if filial else centro.cursos.filter(ativo=True)

    
    if request.method == 'POST':
        curso_id = request.POST.get('curso')
        nome = request.POST.get('nome')
        codigo = request.POST.get('codigo')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        turno = request.POST.get('turno')
        horario_inicio = request.POST.get('horario_inicio')
        horario_fim = request.POST.get('horario_fim')
        dias_semana = request.POST.get('dias_semana')
        vagas_totais = request.POST.get('vagas_totais')

        try:
            curso = get_object_or_404(Curso, id=curso_id, centro=centro)
            if filial and not curso.filiais.filter(pk=filial.pk).exists():
                raise Exception("Curso não pertence à sua filial.")
                
            
            
            turma = Turma.objects.create(
                curso=curso,
                nome=nome,
                codigo=codigo,
                data_inicio=data_inicio,
                data_fim=data_fim,
                turno=turno,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                dias_semana=dias_semana,
                vagas_totais=int(vagas_totais)

            )
            
            messages.success(request, f'Turma "{turma.nome}" criada com sucesso!')
            return redirect('gerenciar_turmas')
        except Exception as e:
            messages.error(request, f'Erro ao criar turma: {str(e)}')
    
    return render(request, 'gestor/turmas/form.html', {
        'centro': centro,
        'filial': filial,
        'cursos': cursos_context,
        'action': 'Criar'
    })

def editar_turma(request, turma_id):
    """
    Edição de uma turma existente no centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    turma = get_object_or_404(Turma, id=turma_id, curso__centro=centro)
    if filial and not turma.curso.filiais.filter(pk=filial.pk).exists():
        messages.error(request, "Permissão negada.")
        return redirect('gerenciar_turmas')
        
    cursos_context = filial.cursos_disponiveis.filter(ativo=True) if filial else centro.cursos.filter(ativo=True)

    
    if request.method == 'POST':
        turma.nome = request.POST.get('nome')
        turma.data_inicio = request.POST.get('data_inicio')
        turma.data_fim = request.POST.get('data_fim')
        turma.turno = request.POST.get('turno')
        turma.horario_inicio = request.POST.get('horario_inicio')
        turma.horario_fim = request.POST.get('horario_fim')
        turma.dias_semana = request.POST.get('dias_semana')
        turma.vagas_totais = int(request.POST.get('vagas_totais'))
        turma.status = request.POST.get('status')
        
        
        turma.save()
        messages.success(request, f'Turma "{turma.nome}" atualizada com sucesso!')
        return redirect('gerenciar_turmas')
    
    return render(request, 'gestor/turmas/form.html', {
        'centro': centro,
        'filial': filial,
        'turma': turma,
        'cursos': cursos_context,
        'action': 'Editar'
    })

def gerenciar_instrutores(request):
    """
    Listagem e gestão de instrutores associados ao centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    instrutores = filial.instrutores.all().order_by('nome') if filial else centro.instrutores.all().order_by('nome')
    
    return render(request, 'gestor/instrutores/listar.html', {
        'centro': centro,
        'filial': filial,
        'instrutores': instrutores
    })

def criar_instrutor(request):
    """
    Cadastro de um novo instrutor para o centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        biografia = request.POST.get('biografia')
        area_especializacao = request.POST.get('area_especializacao')
        
        try:
            instrutor = Instrutor.objects.create(
                centro_de_formacao=centro,
                filial=filial,
                nome=nome,
                email=email,
                biografia=biografia,
                area_especializacao=area_especializacao
            )
            messages.success(request, f'Instrutor "{instrutor.nome}" criado com sucesso!')
            return redirect('gerenciar_instrutores')
        except Exception as e:
            messages.error(request, f'Erro ao criar instrutor: {str(e)}')
    
    return render(request, 'gestor/instrutores/form.html', {
        'centro': centro,
        'filial': filial,
        'action': 'Criar',
        'areas': Instrutor.TIPO_CHOICES_ESPECIALIZACAO
    })

def editar_instrutor(request, instrutor_id):
    """
    Edição de dados de um instrutor existente no centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    instrutor = get_object_or_404(Instrutor, id=instrutor_id, centro_de_formacao=centro)
    
    if filial and instrutor.filial != filial:
        messages.error(request, "Permissão negada.")
        return redirect('gerenciar_instrutores')
    
    if request.method == 'POST':
        instrutor.nome = request.POST.get('nome')
        instrutor.email = request.POST.get('email')
        instrutor.biografia = request.POST.get('biografia')
        instrutor.area_especializacao = request.POST.get('area_especializacao')
        instrutor.ativo = request.POST.get('ativo') == 'on'
        
        instrutor.save()
        messages.success(request, f'Instrutor "{instrutor.nome}" atualizado com sucesso!')
        return redirect('gerenciar_instrutores')
    
    return render(request, 'gestor/instrutores/form.html', {
        'centro': centro,
        'filial': filial,
        'instrutor': instrutor,
        'action': 'Editar',
        'areas': Instrutor.TIPO_CHOICES_ESPECIALIZACAO
    })

def gerenciar_eventos(request):
    """
    Listagem e gerenciamento de eventos organizados pelo centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    eventos_qs = centro.eventos.all()
    # Atualmente o modelo de Evento não possui ForeignKey de Filial associada no modelo.
    # Será carregado tudo do centro principal por simplicidade momentânea até adicionar Filial no Evento caso desejado.
    eventos = eventos_qs.order_by('-data_inicio')
    
    return render(request, 'gestor/eventos.html', {
        'centro': centro,
        'filial': filial,
        'eventos': eventos
    })

def criar_evento(request):
    """
    Criação de um novo evento relacionado ao centro (e filial caso modelado).
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    
    if request.method == 'POST':
        from .models import Evento
        
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_fim')
        local = request.POST.get('local')
        tipo = request.POST.get('tipo')
        
        try:
            evento = Evento.objects.create(
                centro=centro,
                titulo=titulo,
                descricao=descricao,
                data_inicio=data_inicio,
                data_fim=data_fim if data_fim else None,
                local=local,
                tipo=tipo
            )
            messages.success(request, f'Evento "{evento.titulo}" criado com sucesso!')
            return redirect('gerenciar_eventos')
        except Exception as e:
            messages.error(request, f'Erro ao criar evento: {str(e)}')
    
    from .models import Evento
    return render(request, 'gestor/evento_form.html', {
        'centro': centro,
        'filial': filial,
        'action': 'Criar',
        'tipos': Evento._meta.get_field('tipo').choices
    })


def gerenciar_estagios(request):
    """
    Listagem e gerenciamento de estágios publicados pelo centro.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    from estagio.models import Estagio
    
    estagios_qs = Estagio.objects.filter(centro_formacao=centro)
    estagios = estagios_qs.order_by('-data_publicacao')
    
    from django.core.paginator import Paginator
    paginator = Paginator(estagios, 15)
    page_number = request.GET.get('page')
    estagios_page = paginator.get_page(page_number)
    
    return render(request, 'gestor/estagios/listar.html', {
        'centro': centro,
        'filial': filial,
        'estagios': estagios_page
    })

def criar_estagio(request):
    """
    Criação de uma nova vaga de estágio pelo centro.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    from estagio.models import Estagio, AreaEstagio
    
    areas = AreaEstagio.objects.filter(ativa=True)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        area_id = request.POST.get('area')
        descricao = request.POST.get('descricao')
        resumo = request.POST.get('resumo')
        tipo_remuneracao = request.POST.get('tipo_remuneracao')
        valor_remuneracao = request.POST.get('valor_remuneracao') or None
        modalidade = request.POST.get('modalidade')
        duracao_meses = request.POST.get('duracao_meses')
        carga_horaria_semanal = request.POST.get('carga_horaria_semanal')
        vagas_disponiveis = request.POST.get('vagas_disponiveis')
        local_trabalho = request.POST.get('local_trabalho')
        cidade = request.POST.get('cidade')
        provincia = request.POST.get('provincia')
        requisitos = request.POST.get('requisitos')
        competencias_desejadas = request.POST.get('competencias_desejadas')
        data_inicio = request.POST.get('data_inicio')
        data_limite_inscricao = request.POST.get('data_limite_inscricao')
        
        try:
            area = AreaEstagio.objects.get(id=area_id) if area_id else None
            
            estagio = Estagio.objects.create(
                centro_formacao=centro,
                titulo=titulo,
                area=area,
                descricao=descricao,
                resumo=resumo,
                tipo_remuneracao=tipo_remuneracao,
                valor_remuneracao=valor_remuneracao,
                modalidade=modalidade,
                duracao_meses=int(duracao_meses),
                carga_horaria_semanal=int(carga_horaria_semanal),
                vagas_disponiveis=int(vagas_disponiveis),
                local_trabalho=local_trabalho,
                cidade=cidade,
                provincia=provincia,
                requisitos=requisitos,
                competencias_desejadas=competencias_desejadas,
                data_inicio=data_inicio,
                data_limite_inscricao=data_limite_inscricao
            )
            
            if 'imagem_principal' in request.FILES:
                estagio.imagem_principal = request.FILES['imagem_principal']
                estagio.save()
                
            messages.success(request, f'Estágio "{estagio.titulo}" criado com sucesso!')
            return redirect('gerenciar_estagios')
        except Exception as e:
            messages.error(request, f'Erro ao criar estágio: {str(e)}')
            
    return render(request, 'gestor/estagios/form.html', {
        'centro': centro,
        'filial': filial,
        'areas': areas,
        'action': 'Criar',
        'modalidades': Estagio.MODALIDADE,
        'tipos_remuneracao': Estagio.TIPO_REMUNERACAO,
        'duracoes': Estagio.DURACAO,
    })

def editar_estagio(request, estagio_id):
    """
    Edição de uma vaga de estágio existente.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    from estagio.models import Estagio, AreaEstagio
    
    estagio = get_object_or_404(Estagio, id=estagio_id, centro_formacao=centro)
    areas = AreaEstagio.objects.filter(ativa=True)
    
    if request.method == 'POST':
        estagio.titulo = request.POST.get('titulo')
        area_id = request.POST.get('area')
        estagio.area = AreaEstagio.objects.get(id=area_id) if area_id else None
        estagio.descricao = request.POST.get('descricao')
        estagio.resumo = request.POST.get('resumo')
        estagio.tipo_remuneracao = request.POST.get('tipo_remuneracao')
        estagio.valor_remuneracao = request.POST.get('valor_remuneracao') or None
        estagio.modalidade = request.POST.get('modalidade')
        estagio.duracao_meses = int(request.POST.get('duracao_meses'))
        estagio.carga_horaria_semanal = int(request.POST.get('carga_horaria_semanal'))
        estagio.vagas_disponiveis = int(request.POST.get('vagas_disponiveis'))
        estagio.local_trabalho = request.POST.get('local_trabalho')
        estagio.cidade = request.POST.get('cidade')
        estagio.provincia = request.POST.get('provincia')
        estagio.requisitos = request.POST.get('requisitos')
        estagio.competencias_desejadas = request.POST.get('competencias_desejadas')
        estagio.data_inicio = request.POST.get('data_inicio')
        estagio.data_limite_inscricao = request.POST.get('data_limite_inscricao')
        estagio.ativo = request.POST.get('ativo') == 'on'
        
        if 'imagem_principal' in request.FILES:
            estagio.imagem_principal = request.FILES['imagem_principal']
            
        try:
            estagio.save()
            messages.success(request, f'Estágio "{estagio.titulo}" atualizado com sucesso!')
            return redirect('gerenciar_estagios')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar estágio: {str(e)}')
            
    return render(request, 'gestor/estagios/form.html', {
        'centro': centro,
        'filial': filial,
        'estagio': estagio,
        'areas': areas,
        'action': 'Editar',
        'modalidades': Estagio.MODALIDADE,
        'tipos_remuneracao': Estagio.TIPO_REMUNERACAO,
        'duracoes': Estagio.DURACAO,
    })


def confirmar_cadastro(request, token):
    convite = get_object_or_404(ConviteCentro, token=token, usado=False)

    if request.method == "POST":
        nome_centro = request.POST.get("nome_centro", "").strip()
        nome_gestor = request.POST.get("nome_gestor", "").strip()
        nif = request.POST.get("nif", "").strip()
        telefone = request.POST.get("telefone", "").strip()
        endereco = request.POST.get("endereco", "").strip()
        cidade = request.POST.get("cidade", "").strip()
        provincia = request.POST.get("provincia", "").strip()
        pais = request.POST.get("pais", "AO").strip()
        senha = request.POST.get("senha", "").strip()
        confirm_senha = request.POST.get("confirm_senha", "").strip()
        biografia = request.POST.get("biografia", "").strip()
        lat = request.POST.get("lat", "").strip()
        lng = request.POST.get("lng", "").strip()
        metodo_precificacao = request.POST.get("metodo_precificacao", "MARKUP").strip()

        # Validações completas
        errors = []

        if not nome_centro: errors.append("O nome do centro é obrigatório.")
        if not nome_gestor: errors.append("O nome do gestor é obrigatório.")
        if not nif: errors.append("O NIF é obrigatório.")
        if not senha: errors.append("A senha é obrigatória.")
        if senha != confirm_senha: errors.append("As senhas não coincidem.")
        if len(senha) < 8: errors.append("A senha deve ter pelo menos 8 caracteres.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "confirmar_cadastro.html", {"convite": convite, "post_data": request.POST, "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY})

        try:
            centro = convite.centro
            from usuarios.models import Usuario
            
            # 1. Criar/Atualizar Usuário
            usuario, created = Usuario.objects.get_or_create(
                email=centro.email,
                defaults={
                    'nome': nome_gestor,
                    'tipo_usuario': 'GESTOR',
                    'is_active': True
                }
            )
            usuario.set_password(senha)
            usuario.tipo_usuario = 'GESTOR'
            usuario.is_active = True
            usuario.nome = nome_gestor
            usuario.save()

            # 2. Atualizar Centro
            centro.nome = nome_centro
            centro.nif = nif
            centro.telefone = telefone
            centro.endereco = endereco
            centro.cidade = cidade
            centro.provincia = provincia
            centro.pais = pais
            centro.usuario = usuario
            centro.ativo = True
            centro.metodo_precificacao = metodo_precificacao
            
            if lat and lng:
                centro.set_localizacao(float(lat), float(lng))
                
            centro.save()

            # 3. Criar/Atualizar Perfil Institucional
            perfil, _ = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
            perfil.descricao = biografia
            if 'logo' in request.FILES:
                perfil.imagem = request.FILES['logo']
            perfil.save()

            # 4. Finalizar Convite
            convite.usado = True
            convite.save()

            messages.success(request, f"Cadastro do centro {nome_centro} concluído com sucesso! Pode agora fazer login.")
            return redirect('login_gestor')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao processar o cadastro: {str(e)}")
            return render(request, "confirmar_cadastro.html", {
                "convite": convite,
                "post_data": request.POST,
                "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY
            })

    # GET request - mostrar formulário vazio
    return render(request, "confirmar_cadastro.html", {
        "convite": convite,
        "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY
    })

    
def seguir_centro(request, centro_id):
    """
    Permite que um aluno siga um centro de formação específico.
    """
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'status': 'erro', 'mensagem': 'É necessário estar logado para seguir um centro.'}, status=401)

    centro = get_object_or_404(CentroDeFormacao, id=centro_id)

    try:
        aluno = request.user.aluno_profile
    except Aluno.DoesNotExist:
        return JsonResponse({'status': 'erro', 'mensagem': 'Aluno não encontrado.'}, status=404)

    seguimento, criado = CentroSeguimento.objects.get_or_create(aluno=aluno, centro=centro)

    if criado:
        return JsonResponse({
            'status': 'sucesso',
            'mensagem': f"Agora você está seguindo o centro {centro.nome}."
        })
    else:
        return JsonResponse({
            'status': 'info',
            'mensagem': f"Você já segue o centro {centro.nome}."
        })

def login_gestor(request):
    """
    Autentica gestores de centros ou de filiais usando o sistema centralizado.
    """
    if request.user.is_authenticated and request.user.tipo_usuario in ['GESTOR', 'GESTOR_FILIAL']:
        return redirect("centro_dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "").strip()

        if not email or not senha:
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, "login_gestor.html")

        try:
            from django.contrib.auth import authenticate, login
            user = authenticate(request, email=email, password=senha)
            
            if user is not None:
                # Lógica Flexível: Se tem perfil de centro, é gestor, mesmo que o tipo esteja como ALUNO
                if user.tipo_usuario in ['GESTOR', 'GESTOR_FILIAL'] or user.is_superuser or hasattr(user, 'centro_profile'):
                    if hasattr(user, 'centro_profile') or hasattr(user, 'filial_profile'):
                        login(request, user)
                        messages.success(request, f"Olá, {user.nome}! Bem-vindo ao seu painel.")
                        return redirect("centro_dashboard")
                    else:
                        messages.error(request, "Este utilizador não possui um Centro ou Filial vinculado.")
                else:
                    messages.error(request, "Esta conta não tem permissões de Gestor.")
            else:
                messages.error(request, "E-mail ou senha incorretos. Verifique os dados e tente novamente.")
                
        except Exception as e:
            messages.error(request, f"Ocorreu um problema técnico: {str(e)}")

    return render(request, "login_gestor.html")


def logout_gestor(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, "Logout realizado com sucesso!")
    return redirect('login_gestor')



def configuracao_gestor(request):
    """
    Exibe a página de configurações do gestor, permitindo editar detalhes do centro e perfil.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    try:
        centro = request.user.centro_profile
        perfil, created = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
        
        # Determinar tab ativa
        active_tab = request.GET.get('tab', 'details')
        
        context = {
            'centro': centro,
            'perfil': perfil,
            'active_tab': active_tab,
            'latitude': centro.latitude,
            'longitude': centro.longitude,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        }

        return render(request, 'configuracao_gestor.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')


def atualizar_dados_pessoais(request):
    """
    Processa a atualização dos dados básicos e localização geográfica do centro de formação.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = request.user.centro_profile
            perfil, created = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
            
            # Dados básicos do centro
            centro.nome = request.POST.get('nome', centro.nome)
            centro.telefone = request.POST.get('telefone', centro.telefone)
            centro.endereco = request.POST.get('endereco', centro.endereco)
            centro.site = request.POST.get('site', centro.site)
            centro.cidade = request.POST.get('cidade', centro.cidade)
            centro.provincia = request.POST.get('provincia', centro.provincia)
            
            if 'metodo_precificacao' in request.POST:
                centro.metodo_precificacao = request.POST.get('metodo_precificacao')
                
            # Dados Bancários
            if 'banco_nome' in request.POST:
                centro.banco_nome = request.POST.get('banco_nome')
            if 'banco_iban' in request.POST:
                centro.banco_iban = request.POST.get('banco_iban')
            if 'banco_titular' in request.POST:
                centro.banco_titular = request.POST.get('banco_titular')
            
            # Processar localização geográfica
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            
            if latitude and longitude:
                try:
                    lat_float = float(latitude)
                    lng_float = float(longitude)
                    
                    # Guardar a localização (agora suporta qualquer parte do mundo)
                    centro.set_localizacao(lat_float, lng_float)
                        
                except (ValueError, TypeError):
                    messages.warning(request, "Coordenadas inválidas. Use números decimais.")
            else:
                # Se ambos os campos estiverem vazios, limpa a localização
                centro.localizacao = None
            
            centro.save()
            
            # Dados do perfil
            perfil.dono = request.POST.get('dono', perfil.dono)
            perfil.descricao = request.POST.get('descricao', perfil.descricao)
            perfil.tipo = request.POST.get('tipo', perfil.tipo)
            perfil.modalidade = request.POST.get('modalidade', perfil.modalidade)
            
            if 'video_apresentacao' in request.FILES:
                if perfil.video_apresentacao:
                    if os.path.isfile(perfil.video_apresentacao.path):
                        os.remove(perfil.video_apresentacao.path)
                perfil.video_apresentacao = request.FILES['video_apresentacao']
            
            perfil.save()
            
            messages.success(request, 'Dados atualizados com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar dados: {str(e)}')
    
    return redirect(reverse('configuracao_gestor') + '?tab=details')

def atualizar_senha(request):
    """
    Permite ao gestor alterar sua senha de acesso após validação da senha atual.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = request.user.centro_profile
            
            senha_atual = request.POST.get('senha_atual', '').strip()
            nova_senha = request.POST.get('nova_senha', '').strip()
            confirmar_senha = request.POST.get('confirmar_senha', '').strip()
            
            if not senha_atual or not nova_senha or not confirmar_senha:
                messages.error(request, "Todos os campos são obrigatórios.")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            if not centro.verificar_senha(senha_atual):
                messages.error(request, "Senha atual incorreta!")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            if nova_senha != confirmar_senha:
                messages.error(request, "As novas senhas não coincidem!")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            if len(nova_senha) < 8:
                messages.error(request, "A senha deve ter pelo menos 8 caracteres.")
                return redirect(reverse('configuracao_gestor') + '?tab=password')
            
            centro.set_senha(nova_senha)
            centro.save()
            
            messages.success(request, 'Senha atualizada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar senha: {str(e)}')
    
    return redirect(reverse('configuracao_gestor') + '?tab=password')

def atualizar_redes_sociais(request):
    """
    Atualiza os links das redes sociais (Facebook, Instagram, WhatsApp) no perfil do centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        try:
            centro = request.user.centro_profile
            perfil = PerfilCentroDeFormacao.objects.get(centro=centro)
            
            perfil.facebook = request.POST.get('facebook', '')
            perfil.instagram = request.POST.get('instagram', '')
            perfil.whatsapp = request.POST.get('whatsapp', '')
            perfil.save()
            
            messages.success(request, 'Redes sociais atualizadas com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao atualizar redes sociais: {str(e)}')
    
    return redirect(reverse('configuracao_gestor') + '?tab=profile')

def upload_imagem_perfil(request):
    """
    Endpoint AJAX para upload e atualização da imagem de perfil (logo) do centro.
    """
    if request.method == 'POST' and request.FILES.get('imagem_perfil'):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Sessão expirada'})
        
        try:
            centro = request.user.centro_profile
            perfil, created = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
            
            if perfil.imagem:
                if os.path.isfile(perfil.imagem.path):
                    os.remove(perfil.imagem.path)
            
            perfil.imagem = request.FILES['imagem_perfil']
            perfil.save()
            
            return JsonResponse({
                'success': True, 
                'url': perfil.imagem.url,
                'message': 'Imagem atualizada com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})

def upload_banner(request):
    """
    Endpoint AJAX para upload e atualização do banner de capa do perfil do centro.
    """
    if request.method == 'POST' and request.FILES.get('banner'):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Sessão expirada'})
        
        try:
            centro = request.user.centro_profile
            perfil, created = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
            
            if perfil.banner:
                if os.path.isfile(perfil.banner.path):
                    os.remove(perfil.banner.path)
            
            perfil.banner = request.FILES['banner']
            perfil.save()
            
            return JsonResponse({
                'success': True, 
                'url': perfil.banner.url,
                'message': 'Banner atualizado com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Requisição inválida'})



def diferenciais_gestor(request):
    """
    Exibe a lista de diferenciais competitivos cadastrados para o centro.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        diferenciais = centro.diferenciais.all()
        
        context = {
            'centro': centro,
            'diferenciais': diferenciais,
            'active_tab': 'diferentials'
        }
        return render(request, 'gestor/diferenciais.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_diferencial(request):
    """
    Cadastra um novo diferencial (título, descrição e ícone) para o centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            Diferencial.objects.create(
                centro=centro,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao'),
                icone=request.POST.get('icone', 'feather-check')
            )
            
            messages.success(request, 'Diferencial adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar diferencial: {str(e)}')
    
    return redirect('diferenciais_gestor')

def editar_diferencial(request, diferencial_id):
    """
    Edita os dados de um diferencial existente pertencente ao centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            diferencial = Diferencial.objects.get(
                id=diferencial_id, 
                centro_id=centro_id
            )
            
            diferencial.titulo = request.POST.get('titulo', diferencial.titulo)
            diferencial.descricao = request.POST.get('descricao', diferencial.descricao)
            diferencial.icone = request.POST.get('icone', diferencial.icone)
            diferencial.save()
            
            messages.success(request, 'Diferencial atualizado com sucesso!')
            
        except Diferencial.DoesNotExist:
            messages.error(request, "Diferencial não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar diferencial: {str(e)}')
    
    return redirect('diferenciais_gestor')

def excluir_diferencial(request, diferencial_id):
    """
    Remove permanentemente um diferencial do cadastro do centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            diferencial = Diferencial.objects.get(
                id=diferencial_id, 
                centro_id=centro_id
            )
            diferencial.delete()
            messages.success(request, 'Diferencial excluído com sucesso!')
            
        except Diferencial.DoesNotExist:
            messages.error(request, "Diferencial não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir diferencial: {str(e)}')
    
    return redirect('diferenciais_gestor')


def equipe_gestor(request):
    """
    Exibe a listagem de membros da equipe administrativa e docente do centro.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        equipe = centro.equipe.all()
        
        context = {
            'centro': centro,
            'equipe': equipe,
            'active_tab': 'team'
        }
        return render(request, 'gestor/equipe.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_membro_equipe(request):
    """
    Cadastra um novo membro na equipe do centro, incluindo foto e biografia.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            membro = Equipe(
                centro=centro,
                nome=request.POST.get('nome'),
                cargo=request.POST.get('cargo'),
                biografia=request.POST.get('biografia', ''),
                formacao=request.POST.get('formacao', ''),
                experiencia=request.POST.get('experiencia', ''),
                linkedin=request.POST.get('linkedin', ''),
                email=request.POST.get('email', ''),
                ordem=request.POST.get('ordem', 0)
            )
            
            if 'foto' in request.FILES:
                membro.foto = request.FILES['foto']
            
            membro.save()
            messages.success(request, 'Membro da equipe adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar membro: {str(e)}')
    
    return redirect('equipe_gestor')

def editar_membro_equipe(request, membro_id):
    """
    Edita os dados de um membro da equipe existente.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        try:
            membro = Equipe.objects.get(
                id=membro_id, 
                centro_id=centro_id
            )
            
            membro.nome = request.POST.get('nome', membro.nome)
            membro.cargo = request.POST.get('cargo', membro.cargo)
            membro.biografia = request.POST.get('biografia', membro.biografia)
            membro.formacao = request.POST.get('formacao', membro.formacao)
            membro.experiencia = request.POST.get('experiencia', membro.experiencia)
            membro.linkedin = request.POST.get('linkedin', membro.linkedin)
            membro.email = request.POST.get('email', membro.email)
            membro.ordem = request.POST.get('ordem', membro.ordem)
            
            if 'foto' in request.FILES:
                if membro.foto:
                    if os.path.isfile(membro.foto.path):
                        os.remove(membro.foto.path)
                membro.foto = request.FILES['foto']
            
            membro.save()
            messages.success(request, 'Membro da equipe atualizado com sucesso!')
            
        except Equipe.DoesNotExist:
            messages.error(request, "Membro não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar membro: {str(e)}')
    
    return redirect('equipe_gestor')

def excluir_membro_equipe(request, membro_id):
    """
    Remove permanentemente um membro da equipe do centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            membro = Equipe.objects.get(
                id=membro_id, 
                centro_id=centro_id
            )
            
            if membro.foto and os.path.isfile(membro.foto.path):
                os.remove(membro.foto.path)
            
            membro.delete()
            messages.success(request, 'Membro da equipe excluído com sucesso!')
            
        except Equipe.DoesNotExist:
            messages.error(request, "Membro não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir membro: {str(e)}')
    
    return redirect('equipe_gestor')



def depoimentos_gestor(request):
    """
    Lista todos os depoimentos (testimonials) vinculados ao centro.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        depoimentos = centro.depoimentos.all()
        
        context = {
            'centro': centro,
            'depoimentos': depoimentos,
            'active_tab': 'testimonials'
        }
        return render(request, 'gestor/depoimentos.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_depoimento(request):
    """
    Adiciona um novo depoimento manual ao perfil do centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            depoimento = Depoimento(
                centro=centro,
                nome=request.POST.get('nome'),
                cargo=request.POST.get('cargo', ''),
                texto=request.POST.get('texto'),
                nota=int(request.POST.get('nota', 5)),
                aprovado=True  # Aprova automaticamente quando adicionado pelo gestor
            )
            
            if 'foto' in request.FILES:
                depoimento.foto = request.FILES['foto']
            
            depoimento.save()
            messages.success(request, 'Depoimento adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar depoimento: {str(e)}')
    
    return redirect('depoimentos_gestor')

def toggle_aprovacao_depoimento(request, depoimento_id):
    """
    Alterna o status de aprovação de um depoimento para exibição pública.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            depoimento = Depoimento.objects.get(
                id=depoimento_id, 
                centro_id=centro_id
            )
            depoimento.aprovado = not depoimento.aprovado
            depoimento.save()
            
            status = "aprovado" if depoimento.aprovado else "reprovado"
            messages.success(request, f'Depoimento {status} com sucesso!')
            
        except Depoimento.DoesNotExist:
            messages.error(request, "Depoimento não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar status: {str(e)}')
    
    return redirect('depoimentos_gestor')

def excluir_depoimento(request, depoimento_id):
    """
    Exclui permanentemente um depoimento.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            depoimento = Depoimento.objects.get(
                id=depoimento_id, 
                centro_id=centro_id
            )
            
            if depoimento.foto and os.path.isfile(depoimento.foto.path):
                os.remove(depoimento.foto.path)
            
            depoimento.delete()
            messages.success(request, 'Depoimento excluído com sucesso!')
            
        except Depoimento.DoesNotExist:
            messages.error(request, "Depoimento não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir depoimento: {str(e)}')
    
    return redirect('depoimentos_gestor')



def estatisticas_gestor(request):
    """
    Gerencia as estatísticas chave exibidas no perfil do centro (ex: número de formados).
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        estatisticas = centro.estatisticas.all()
        
        context = {
            'centro': centro,
            'estatisticas': estatisticas,
            'active_tab': 'statistics'
        }
        return render(request, 'gestor/estatisticas.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_estatistica(request):
    """
    Cria uma nova métrica estatística para o centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            Estatistica.objects.create(
                centro=centro,
                titulo=request.POST.get('titulo'),
                valor=request.POST.get('valor'),
                icone=request.POST.get('icone', 'feather-users'),
                ordem=request.POST.get('ordem', 0)
            )
            
            messages.success(request, 'Estatística adicionada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar estatística: {str(e)}')
    
    return redirect('estatisticas_gestor')

def editar_estatistica(request, estatistica_id):
    """
    Atualiza os dados de uma estatística existente.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            estatistica = Estatistica.objects.get(
                id=estatistica_id, 
                centro_id=centro_id
            )
            
            estatistica.titulo = request.POST.get('titulo', estatistica.titulo)
            estatistica.valor = request.POST.get('valor', estatistica.valor)
            estatistica.icone = request.POST.get('icone', estatistica.icone)
            estatistica.ordem = request.POST.get('ordem', estatistica.ordem)
            estatistica.save()
            
            messages.success(request, 'Estatística atualizada com sucesso!')
            
        except Estatistica.DoesNotExist:
            messages.error(request, "Estatística não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar estatística: {str(e)}')
    
    return redirect('estatisticas_gestor')

def excluir_estatistica(request, estatistica_id):
    """
    Remove uma estatística da exibição do centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            estatistica = Estatistica.objects.get(
                id=estatistica_id, 
                centro_id=centro_id
            )
            estatistica.delete()
            messages.success(request, 'Estatística excluída com sucesso!')
            
        except Estatistica.DoesNotExist:
            messages.error(request, "Estatística não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir estatística: {str(e)}')
    
    return redirect('estatisticas_gestor')



def parcerias_gestor(request):
    """
    Exibe a listagem de parcerias estratégicas do centro de formação.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        parcerias = centro.parcerias.all()
        
        context = {
            'centro': centro,
            'parcerias': parcerias,
            'active_tab': 'partnerships'
        }
        return render(request, 'gestor/parcerias.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_parceria(request):
    """
    Cadastra uma nova parceria, incluindo logo da empresa parceira.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            parceria = Parceria(
                centro=centro,
                nome_empresa=request.POST.get('nome_empresa'),
                tipo_parceria=request.POST.get('tipo_parceria'),
                website=request.POST.get('website', '')
            )
            
            if 'logo' in request.FILES:
                parceria.logo = request.FILES['logo']
            
            parceria.save()
            messages.success(request, 'Parceria adicionada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar parceria: {str(e)}')
    
    return redirect('parcerias_gestor')

def toggle_parceria(request, parceria_id):
    """
    Ativa ou desativa a exibição de uma parceria no perfil do centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            parceria = Parceria.objects.get(
                id=parceria_id, 
                centro_id=centro_id
            )
            parceria.ativa = not parceria.ativa
            parceria.save()
            
            status = "ativada" if parceria.ativa else "desativada"
            messages.success(request, f'Parceria {status} com sucesso!')
            
        except Parceria.DoesNotExist:
            messages.error(request, "Parceria não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar status: {str(e)}')
    
    return redirect('parcerias_gestor')

def excluir_parceria(request, parceria_id):
    """
    Remove permanentemente uma parceria do cadastro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            parceria = Parceria.objects.get(
                id=parceria_id, 
                centro_id=centro_id
            )
            
            if parceria.logo and os.path.isfile(parceria.logo.path):
                os.remove(parceria.logo.path)
            
            parceria.delete()
            messages.success(request, 'Parceria excluída com sucesso!')
            
        except Parceria.DoesNotExist:
            messages.error(request, "Parceria não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir parceria: {str(e)}')
    
    return redirect('parcerias_gestor')



def eventos_gestor(request):
    """
    Lista todos os eventos cadastrados pelo centro.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        eventos = centro.eventos.all()
        
        context = {
            'centro': centro,
            'eventos': eventos,
            'active_tab': 'events'
        }
        return render(request, 'gestor/eventos.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_evento(request):
    """
    Cria um novo evento com data, local e imagem.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            data_inicio_str = request.POST.get('data_inicio')
            data_fim_str = request.POST.get('data_fim')
            
            evento = Evento(
                centro=centro,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao'),
                local=request.POST.get('local'),
                tipo=request.POST.get('tipo'),
                link_inscricao=request.POST.get('link_inscricao', '')
            )
            
            if data_inicio_str:
                evento.data_inicio = timezone.make_aware(
                    datetime.strptime(data_inicio_str, '%Y-%m-%dT%H:%M')
                )
            
            if data_fim_str:
                evento.data_fim = timezone.make_aware(
                    datetime.strptime(data_fim_str, '%Y-%m-%dT%H:%M')
                )
            
            if 'imagem' in request.FILES:
                evento.imagem = request.FILES['imagem']
            
            evento.save()
            messages.success(request, 'Evento adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar evento: {str(e)}')
    
    return redirect('eventos_gestor')

def toggle_destaque_evento(request, evento_id):
    """
    Define se um evento deve aparecer em destaque no perfil.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            evento = Evento.objects.get(
                id=evento_id, 
                centro_id=centro_id
            )
            evento.destaque = not evento.destaque
            evento.save()
            
            status = "em destaque" if evento.destaque else "removido do destaque"
            messages.success(request, f'Evento {status} com sucesso!')
            
        except Evento.DoesNotExist:
            messages.error(request, "Evento não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar destaque: {str(e)}')
    
    return redirect('eventos_gestor')

def excluir_evento(request, evento_id):
    """
    Remove um evento permanentemente.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            evento = Evento.objects.get(
                id=evento_id, 
                centro_id=centro_id
            )
            
            if evento.imagem and os.path.isfile(evento.imagem.path):
                os.remove(evento.imagem.path)
            
            evento.delete()
            messages.success(request, 'Evento excluído com sucesso!')
            
        except Evento.DoesNotExist:
            messages.error(request, "Evento não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir evento: {str(e)}')
    
    return redirect('eventos_gestor')




def reels_gestor(request):
    """
    Gerencia os vídeos curtos (reels) promocionais do centro.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        reels = centro.reels.all()
        
        context = {
            'centro': centro,
            'reels': reels,
            'active_tab': 'reels'
        }
        return render(request, 'gestor/reels.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_reel(request):
    """
    Realiza o upload de um novo vídeo para os reels do centro.
    """
    if request.method == 'POST' and request.FILES.get('video'):
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            reel = ReelCentro(
                centro=centro,
                titulo=request.POST.get('titulo'),
                descricao=request.POST.get('descricao', ''),
                video=request.FILES['video']
            )
            
            if 'thumbnail' in request.FILES:
                reel.thumbnail = request.FILES['thumbnail']
            
            reel.save()
            messages.success(request, 'Reel adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar reel: {str(e)}')
    
    return redirect('reels_gestor')

def toggle_publico_reel(request, reel_id):
    """
    Alterna a visibilidade pública de um reel.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            reel = ReelCentro.objects.get(
                id=reel_id, 
                centro_id=centro_id
            )
            reel.publico = not reel.publico
            reel.save()
            
            status = "público" if reel.publico else "privado"
            messages.success(request, f'Reel definido como {status} com sucesso!')
            
        except ReelCentro.DoesNotExist:
            messages.error(request, "Reel não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar visibilidade: {str(e)}')
    
    return redirect('reels_gestor')

def toggle_destaque_reel(request, reel_id):
    """
    Define se um vídeo curto (reel) deve aparecer em destaque no perfil.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            reel = ReelCentro.objects.get(
                id=reel_id, 
                centro_id=centro_id
            )
            reel.destaque = not reel.destaque
            reel.save()
            
            status = "em destaque" if reel.destaque else "removido do destaque"
            messages.success(request, f'Reel {status} com sucesso!')
            
        except ReelCentro.DoesNotExist:
            messages.error(request, "Reel não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao alterar destaque: {str(e)}')
    
    return redirect('reels_gestor')

def excluir_reel(request, reel_id):
    """
    Remove permanentemente um vídeo curto (reel) e seus arquivos de mídia.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            reel = ReelCentro.objects.get(
                id=reel_id, 
                centro_id=centro_id
            )
            
            # Remover arquivos de mídia
            if reel.video and os.path.isfile(reel.video.path):
                os.remove(reel.video.path)
            if reel.thumbnail and os.path.isfile(reel.thumbnail.path):
                os.remove(reel.thumbnail.path)
            
            reel.delete()
            messages.success(request, 'Reel excluído com sucesso!')
            
        except ReelCentro.DoesNotExist:
            messages.error(request, "Reel não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir reel: {str(e)}')
    
    return redirect('reels_gestor')




def recursos_gestor(request):
    """
    Lista os recursos e infraestrutura (ex: Wi-Fi, Estacionamento) do centro.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        recursos = centro.recursos.all()
        
        context = {
            'centro': centro,
            'recursos': recursos,
            'active_tab': 'resources'
        }
        return render(request, 'gestor/recursos.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_recurso(request):
    """
    Cadastra um novo recurso ou benefício oferecido pelo centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            Recurso.objects.create(
                centro=centro,
                nome=request.POST.get('nome'),
                descricao=request.POST.get('descricao'),
                icone=request.POST.get('icone', '')
            )
            
            messages.success(request, 'Recurso adicionado com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar recurso: {str(e)}')
    
    return redirect('recursos_gestor')

def editar_recurso(request, recurso_id):
    """
    Edita os dados de um recurso existente.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            recurso = Recurso.objects.get(
                id=recurso_id, 
                centro_id=centro_id
            )
            
            recurso.nome = request.POST.get('nome', recurso.nome)
            recurso.descricao = request.POST.get('descricao', recurso.descricao)
            recurso.icone = request.POST.get('icone', recurso.icone)
            recurso.save()
            
            messages.success(request, 'Recurso atualizado com sucesso!')
            
        except Recurso.DoesNotExist:
            messages.error(request, "Recurso não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar recurso: {str(e)}')
    
    return redirect('recursos_gestor')

def excluir_recurso(request, recurso_id):
    """
    Exclui um recurso do perfil do centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            recurso = Recurso.objects.get(
                id=recurso_id, 
                centro_id=centro_id
            )
            recurso.delete()
            messages.success(request, 'Recurso excluído com sucesso!')
            
        except Recurso.DoesNotExist:
            messages.error(request, "Recurso não encontrado.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir recurso: {str(e)}')
    
    return redirect('recursos_gestor')




def areas_formacao_gestor(request):
    """
    Gerencia as áreas de formação técnica e acadêmica do centro.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para acessar as configurações.")
        return redirect('login_gestor')
    
    centro_id = request.user.centro_profile.id
    
    try:
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        areas = centro.areas_formacao.all()
        
        context = {
            'centro': centro,
            'areas': areas,
            'active_tab': 'areas'
        }
        return render(request, 'gestor/areas_formacao.html', context)
        
    except CentroDeFormacao.DoesNotExist:
        messages.error(request, "Centro não encontrado.")
        return redirect('login_gestor')

def adicionar_area_formacao(request):
    """
    Cadastra uma nova área de conhecimento ou departamento no centro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
            
            AreaFormacao.objects.create(
                centro=centro,
                nome=request.POST.get('nome'),
                descricao=request.POST.get('descricao', ''),
                icone=request.POST.get('icone', ''),
                ordem=request.POST.get('ordem', 0)
            )
            
            messages.success(request, 'Área de formação adicionada com sucesso!')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar área: {str(e)}')
    
    return redirect('areas_formacao_gestor')

def editar_area_formacao(request, area_id):
    """
    Atualiza as informações de uma área de formação existente.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            area = AreaFormacao.objects.get(
                id=area_id, 
                centro_id=centro_id
            )
            
            area.nome = request.POST.get('nome', area.nome)
            area.descricao = request.POST.get('descricao', area.descricao)
            area.icone = request.POST.get('icone', area.icone)
            area.ordem = request.POST.get('ordem', area.ordem)
            area.save()
            
            messages.success(request, 'Área de formação atualizada com sucesso!')
            
        except AreaFormacao.DoesNotExist:
            messages.error(request, "Área não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao atualizar área: {str(e)}')
    
    return redirect('areas_formacao_gestor')

def excluir_area_formacao(request, area_id):
    """
    Remove uma área de formação do cadastro.
    """
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Sessão expirada.")
            return redirect('login_gestor')
        
        centro_id = request.user.centro_profile.id
        
        try:
            area = AreaFormacao.objects.get(
                id=area_id, 
                centro_id=centro_id
            )
            area.delete()
            messages.success(request, 'Área de formação excluída com sucesso!')
            
        except AreaFormacao.DoesNotExist:
            messages.error(request, "Área não encontrada.")
        except Exception as e:
            messages.error(request, f'Erro ao excluir área: {str(e)}')
    
    return redirect('areas_formacao_gestor')






def save_turmas_from_json(curso, turmas_json_str):
    if not turmas_json_str:
        return
    
    try:
        turmas_data = json.loads(turmas_json_str)
    except Exception:
        return
        
    received_ids = []
    for t_data in turmas_data:
        t_id = t_data.get('id')
        if t_id:
            try:
                received_ids.append(int(t_id))
            except ValueError:
                pass

    # Excluir turmas que não vieram no JSON e não têm inscrições ativas (vagas_ocupadas == 0)
    turmas_para_deletar = curso.turmas.exclude(id__in=received_ids)
    for t_del in turmas_para_deletar:
        if t_del.vagas_ocupadas == 0:
            t_del.delete()

    for t_data in turmas_data:
        t_id = t_data.get('id')
        nome = t_data.get('nome', '').strip()
        if not nome:
            continue
            
        turno = t_data.get('turno', 'MANHA')
        vagas_totais = int(t_data.get('vagas_totais', 0))
        
        # Tratar dias da semana
        dias_lista = t_data.get('dias_semana', [])
        if isinstance(dias_lista, list):
            dias_semana = ",".join(dias_lista)
        else:
            dias_semana = str(dias_lista)
            
        local = t_data.get('local', '').strip()
        sala = t_data.get('sala', '').strip()
        observacoes = t_data.get('observacoes', '').strip()
        status = t_data.get('status', 'ABERTA')
        
        # Parse de datas e horas
        try:
            data_inicio = datetime.strptime(t_data.get('data_inicio'), '%Y-%m-%d').date() if t_data.get('data_inicio') else None
            data_fim = datetime.strptime(t_data.get('data_fim'), '%Y-%m-%d').date() if t_data.get('data_fim') else None
            horario_inicio = datetime.strptime(t_data.get('horario_inicio'), '%H:%M').time() if t_data.get('horario_inicio') else None
            horario_fim = datetime.strptime(t_data.get('horario_fim'), '%H:%M').time() if t_data.get('horario_fim') else None
        except Exception:
            continue
            
        if not (data_inicio and data_fim and horario_inicio and horario_fim):
            continue

        if t_id:
            # Atualizar
            try:
                turma = Turma.objects.get(id=t_id, curso=curso)
                turma.nome = nome
                turma.turno = turno
                turma.horario_inicio = horario_inicio
                turma.horario_fim = horario_fim
                turma.dias_semana = dias_semana
                turma.data_inicio = data_inicio
                turma.data_fim = data_fim
                turma.vagas_totais = vagas_totais
                turma.local = local
                turma.sala = sala
                turma.status = status
                turma.observacoes = observacoes
                turma.save()
            except Turma.DoesNotExist:
                pass
        else:
            # Criar novo
            Turma.objects.create(
                curso=curso,
                nome=nome,
                turno=turno,
                horario_inicio=horario_inicio,
                horario_fim=horario_fim,
                dias_semana=dias_semana,
                data_inicio=data_inicio,
                data_fim=data_fim,
                vagas_totais=vagas_totais,
                local=local,
                sala=sala,
                status=status,
                observacoes=observacoes
            )


def criar_curso(request):
    """
    Cria um novo curso de um centro ou filial, permitindo salvar como rascunho ou iniciar processo de publicação.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para criar cursos.")
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    if request.user.tipo_usuario == 'GESTOR_FILIAL':
        messages.error(request, "Apenas a Sede Principal (Master) tem permissões para criar novos cursos.")
        return redirect('gestor_dashboard')
        
    # Verificação de Limite de Cursos do Plano Atual
    try:
        assinatura = centro.assinatura
        if not assinatura.esta_ativa:
            messages.warning(request, "O seu plano expirou! Por favor, renove a sua assinatura para criar novos cursos.")
            return redirect('gerenciar_assinatura')
            
        limite = assinatura.plano.limite_cursos
        total_cursos = centro.cursos.count()
        if total_cursos >= limite:
            messages.warning(request, f"Atingiu o limite de cursos do seu plano atual ({limite}). Antes de criar um novo curso, precisa de atualizar o seu plano.")
            return redirect('gerenciar_assinatura')
    except Exception:
        messages.warning(request, "Não possui um plano ativo associado ao seu centro. Subscreva a um plano para criar cursos.")
        return redirect('gerenciar_assinatura')
    
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES, centro=centro)
        if form.is_valid():
            try:
                curso = form.save(commit=False)
                curso.centro = centro
                
                # Se for salvar como rascunho
                if request.POST.get('rascunho'):
                    curso.rascunho = True
                    curso.publicado = False
                    curso.save()
                    if filial:
                        curso.filiais.add(filial)
                    form.save_m2m()
                    save_turmas_from_json(curso, request.POST.get('turmas_json'))
                    messages.success(request, 'Curso salvo como rascunho com sucesso!')
                    return redirect('listar_cursos')
                else:
                    # Salva e redireciona para overview
                    curso.rascunho = True
                    curso.publicado = False
                    curso.save()
                    if filial:
                        curso.filiais.add(filial)
                    form.save_m2m()
                    save_turmas_from_json(curso, request.POST.get('turmas_json'))
                    return redirect('curso_overview', curso_id=curso.id)
                    
            except Exception as e:
                messages.error(request, f'Erro ao criar curso: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CursoForm(centro=centro)
    
    instrutores = filial.instrutores.filter(ativo=True) if filial else centro.instrutores.filter(ativo=True)
    
    context = {
        'form': form,
        'centro': centro,
        'filial': filial,
        'categorias': Categoria.objects.all(),
        'instrutores': instrutores
    }
    return render(request, 'criar_curso.html', context)

def curso_overview(request, curso_id):
    """Página de revisão do curso antes da publicação"""
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para ver o curso.")
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    curso = get_object_or_404(Curso, id=curso_id, centro=centro)
    if filial and not curso.filiais.filter(pk=filial.pk).exists():
        messages.error(request, "Permissão negada.")
        return redirect('listar_cursos')
    
    context = {
        'curso': curso,
        'centro': centro,
        'filial': filial
    }
    return render(request, 'curso_overview.html', context)

def publicar_curso_final(request, curso_id):
    """Publicação final do curso após revisão"""
    if not request.user.is_authenticated:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    
    try:
        curso = Curso.objects.get(id=curso_id, centro=centro)
        if filial and not curso.filiais.filter(pk=filial.pk).exists():
            messages.error(request, "Permissão negada.")
            return redirect('listar_cursos')
            
        try:
            assinatura = centro.assinatura
            if not assinatura.esta_ativa:
                messages.warning(request, "Atenção: O seu plano expirou. Antes de publicar este curso, tem que renovar a sua assinatura.")
                return redirect('gerenciar_assinatura')
        except Exception:
            messages.warning(request, "Atenção: Precisa de um plano ativo para publicar cursos.")
            return redirect('gerenciar_assinatura')
            
        # Validações finais antes de publicar
        if not curso.titulo:
            messages.error(request, "O curso precisa ter um título.")
            return redirect('curso_overview', curso_id=curso_id)
        
        if not curso.descricao:
            messages.error(request, "O curso precisa ter uma descrição.")
            return redirect('curso_overview', curso_id=curso_id)
        
        if not curso.instrutores.exists():
            messages.error(request, "Atribua pelo menos um formador antes de publicar o curso.")
            return redirect('curso_overview', curso_id=curso_id)
        
        
        # Publica o curso e agenda o evento apenas na transição para publicado.
        era_publicado = curso.publicado
        curso.publicado = True
        curso.save()
        if not era_publicado:
            queue_notification_event(
                'course.published',
                f'course.published:{curso.pk}',
                {'course_id': curso.pk, 'title': curso.titulo, 'center': getattr(curso.centro, 'nome', ''), 'link': f'/cursos/{curso.pk}'},
            )
        messages.success(request, 'Curso publicado com sucesso!')
        return redirect('listar_cursos')
        
    except Exception as e:
        messages.error(request, f'Erro ao publicar curso: {str(e)}')
        return redirect('curso_overview', curso_id=curso_id)




def listar_cursos(request):
    """
    Lista todos os cursos do centro ou filial, organizados por status (publicados, rascunhos, destaques).
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para ver seus cursos.")
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    
    cursos_qs = filial.cursos_disponiveis.all() if filial else centro.cursos.all()
    cursos = cursos_qs.order_by('-data_criacao')
    
    # Filtros para as abas
    cursos_publicados = cursos.filter(publicado=True)
    cursos_rascunhos = cursos.filter(publicado=False)
    cursos_destaque = cursos.filter(destaque=True)
    
    context = {
        'cursos': cursos,
        'cursos_publicados': cursos_publicados,
        'cursos_rascunhos': cursos_rascunhos,
        'cursos_destaque': cursos_destaque,
        'centro': centro,
        'filial': filial
    }
    return render(request, 'listar_cursos.html', context)
    
        
def editar_curso(request, curso_id):
    """
    Permite editar os detalhes de um curso existente.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Faça login para editar cursos.")
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    
    curso = get_object_or_404(Curso, id=curso_id, centro=centro)
    if filial and not curso.filiais.filter(pk=filial.pk).exists():
        messages.error(request, "Permissão negada.")
        return redirect('listar_cursos')
    
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES, instance=curso, centro=centro)
        if form.is_valid():
            try:
                form.save()
                save_turmas_from_json(curso, request.POST.get('turmas_json'))
                messages.success(request, 'Curso atualizado com sucesso!')
                return redirect('listar_cursos')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar curso: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CursoForm(instance=curso, centro=centro)
    
    # Serializar turmas existentes do curso
    turmas_existentes = []
    for t in curso.turmas.all():
        turmas_existentes.append({
            'id': t.id,
            'nome': t.nome,
            'turno': t.turno,
            'horario_inicio': t.horario_inicio.strftime('%H:%M') if t.horario_inicio else '',
            'horario_fim': t.horario_fim.strftime('%H:%M') if t.horario_fim else '',
            'dias_semana': t.dias_semana.split(',') if t.dias_semana else [],
            'data_inicio': t.data_inicio.strftime('%Y-%m-%d') if t.data_inicio else '',
            'data_fim': t.data_fim.strftime('%Y-%m-%d') if t.data_fim else '',
            'vagas_totais': t.vagas_totais,
            'local': t.local,
            'sala': t.sala,
            'status': t.status,
            'observacoes': t.observacoes
        })
    
    context = {
        'form': form,
        'curso': curso,
        'centro': centro,
        'filial': filial,
        'turmas_existentes_json': json.dumps(turmas_existentes)
    }
    return render(request, 'editar_curso.html', context)

def publicar_curso(request, curso_id):
    """
    Endpoint AJAX para publicar um curso, tornando-o visível no site.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Sessão expirada'})
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'success': False, 'error': 'Centro não encontrado'})
    
    try:
        curso = Curso.objects.get(id=curso_id, centro=centro)
        if filial and not curso.filiais.filter(pk=filial.pk).exists():
            return JsonResponse({'success': False, 'error': 'Permissão negada'})
            
        era_publicado = curso.publicado
        curso.publicado = True
        curso.save()
        if not era_publicado:
            queue_notification_event(
                'course.published',
                f'course.published:{curso.pk}',
                {'course_id': curso.pk, 'title': curso.titulo, 'center': getattr(curso.centro, 'nome', ''), 'link': f'/cursos/{curso.pk}'},
            )
        return JsonResponse({
            'success': True, 
            'message': 'Curso publicado com sucesso!',
            'publicado': True
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def despublicar_curso(request, curso_id):
    """
    Endpoint AJAX para despublicar um curso, removendo-o da visão pública.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Sessão expirada'})
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'success': False, 'error': 'Centro não encontrado'})
    
    try:
        curso = Curso.objects.get(id=curso_id, centro=centro)
        if filial and not curso.filiais.filter(pk=filial.pk).exists():
            return JsonResponse({'success': False, 'error': 'Permissão negada'})
            
        curso.publicado = False
        curso.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Curso despublicado com sucesso!',
            'publicado': False
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def excluir_curso(request, curso_id):
    """
    Exclui permanentemente um curso do banco de dados.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Sessão expirada.")
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    
    try:
        curso = Curso.objects.get(id=curso_id, centro=centro)
        if filial and not curso.filiais.filter(pk=filial.pk).exists():
            messages.error(request, "Permissão negada.")
            return redirect('listar_cursos')
            
        curso.delete()
        
        messages.success(request, 'Curso excluído com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao excluir curso: {str(e)}')
    
    return redirect('listar_cursos')




# views.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

def chat_centro(request):
    """
    Interface principal de chat para o gestor do centro responder a alunos.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    # Verificação robusta: se tem perfil de centro, é admin ou é aluno (teste), pode entrar
    tem_centro = hasattr(request.user, 'centro_profile') and request.user.centro_profile is not None
    is_admin_or_test = request.user.tipo_usuario in ['ADMIN', 'ALUNO']
    
    if not (tem_centro or is_admin_or_test):
        messages.error(request, f"Acesso negado. O seu utilizador ({request.user.email}) não possui um centro de formação associado.")
        return redirect('login_gestor')
    
    try:
        centro = request.user.centro_profile
    except AttributeError:
        # Se for admin sem centro, pegamos o primeiro para visualização
        centro = CentroDeFormacao.objects.filter(ativo=True).first()
    
    # Buscar conversas ativas do centro
    conversas = Conversa.objects.filter(centro=centro, ativa=True).select_related('aluno__usuario')
    
    # Capturar e validar ID da conversa
    conversa_id = request.GET.get('conversa_id')
    conversa_atual = None
    mensagens = []
    
    if conversa_id:
        # Limpar o ID caso venha com lixo (ex: / no final)
        clean_id = ''.join(filter(str.isdigit, str(conversa_id)))
        if clean_id:
            conversa_atual = Conversa.objects.filter(id=clean_id, centro=centro).first()
            if conversa_atual:
                mensagens = Mensagem.objects.filter(conversa=conversa_atual).select_related('remetente_aluno', 'remetente_centro').order_by('data_envio')
    
    cursos_centro = []
    if conversa_atual:
        cursos_centro = conversa_atual.centro.cursos.filter(ativo=True, publicado=True).order_by('-destaque', '-data_criacao')[:6]
    
    context = {
        'centro': centro,
        'conversas': conversas,
        'conversa_atual': conversa_atual,
        'mensagens': mensagens,
        'cursos_centro': cursos_centro,
    }
    
    # Se for um pedido parcial via AJAX para carregar o miolo do chat
    if request.GET.get('partial') == 'true':
        return render(request, 'include/dashboard_chat_content.html', context)
        
    return render(request, 'chat_centro.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def enviar_mensagem_centro(request):
    """
    Endpoint para o centro enviar uma mensagem (texto ou imagem) em uma conversa.
    Suporta FormData para permitir upload de arquivos.
    """
    if not request.user.is_authenticated or request.user.tipo_usuario not in ['GESTOR', 'GESTOR_FILIAL', 'ADMIN', 'ALUNO']:
        return JsonResponse({'error': 'Não autenticado ou permissão insuficiente'}, status=401)
    
    try:
        centro = request.user.centro_profile
        
        # Aceita tanto JSON como FormData
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            conversa_id = data.get('conversa_id')
            mensagem_texto = data.get('mensagem')
            arquivo = None
        else:
            conversa_id = request.POST.get('conversa_id')
            mensagem_texto = request.POST.get('mensagem', '')
            arquivo = request.FILES.get('arquivo')
        
        if not mensagem_texto and not arquivo:
            return JsonResponse({'error': 'A mensagem não pode estar vazia'}, status=400)
            
        conversa = get_object_or_404(Conversa, id=conversa_id, centro=centro)
        
        tipo_msg = 'TEXTO'
        if arquivo:
            if arquivo.content_type.startswith('image/'):
                tipo_msg = 'IMAGEM'
            else:
                tipo_msg = 'ARQUIVO'
        
        mensagem = Mensagem.objects.create(
            conversa=conversa,
            remetente_centro=centro,
            mensagem=mensagem_texto,
            arquivo=arquivo,
            tipo=tipo_msg
        )
        
        # Atualizar última mensagem da conversa
        conversa.ultima_mensagem = timezone.now()
        conversa.save()
        
        return JsonResponse({
            'success': True,
            'mensagem_id': mensagem.id,
            'data_envio': mensagem.data_envio.strftime('%d/%m/%Y %H:%M')
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def get_mensagens_ajax(request, conversa_id):
    """
    Retorna apenas o fragmento HTML das mensagens de uma conversa para atualização dinâmica.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
        
    term_centro = hasattr(request.user, 'centro_profile') and request.user.centro_profile is not None
    if not (term_centro or request.user.tipo_usuario in ['ADMIN', 'ALUNO']):
        return JsonResponse({'error': 'Acesso negado'}, status=403)
        
    try:
        centro = request.user.centro_profile
    except AttributeError:
        centro = CentroDeFormacao.objects.filter(ativo=True).first()
        
    conversa = get_object_or_404(Conversa, id=conversa_id, centro=centro)
    mensagens = Mensagem.objects.filter(conversa=conversa).select_related('remetente_aluno', 'remetente_centro').order_by('data_envio')
    
    # NOVO: Carregar cursos para o catálogo inicial (sempre presente no topo do fragmento)
    cursos_centro = conversa.centro.cursos.filter(ativo=True, publicado=True).order_by('-destaque', '-data_criacao')[:6]
    
    return render(request, 'include/chat_messages_fragment.html', {
        'mensagens': mensagens,
        'conversa_atual': conversa,
        'cursos_centro': cursos_centro,
    })

@login_required
def eliminar_conversa(request, conversa_id):
    """
    Remove permanentemente uma conversa e todas as suas mensagens.
    """
    if request.user.tipo_usuario == 'ALUNO':
        centro = CentroDeFormacao.objects.filter(ativo=True).first()
    else:
        centro = getattr(request.user, 'centro_profile', None)
        
    if not centro:
        messages.error(request, "Não possui permissão para esta ação.")
        return redirect('chat_centro')
        
    conversa = get_object_or_404(Conversa, id=conversa_id, centro=centro)
    conversa.delete()
    messages.success(request, "Conversa removida com sucesso.")
    return redirect('chat_centro')

def atualizar_status_digitando(request):
    """
    Atualiza o status "digitando" do centro em uma conversa via AJAX.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    centro_id = request.user.centro_profile.id
    
    try:
        data = json.loads(request.body)
        conversa_id = data.get('conversa_id')
        digitando = data.get('digitando', False)
        
        centro = CentroDeFormacao.objects.get(id=centro_id, ativo=True)
        conversa = get_object_or_404(Conversa, id=conversa_id, centro=centro)
        
        # Buscar a mensagem de digitando existente
        mensagem_digitando = Mensagem.objects.filter(
            conversa=conversa, 
            remetente_centro=centro, 
            digitando=True
        ).first()
        
        if digitando:
            # Se não existe uma mensagem de digitando, criar uma
            if not mensagem_digitando:
                Mensagem.objects.create(
                    conversa=conversa,
                    remetente_centro=centro,
                    mensagem='...',
                    tipo='TEXTO',
                    digitando=True
                )
        else:
            # Se existe uma mensagem de digitando, deletá-la
            if mensagem_digitando:
                mensagem_digitando.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def buscar_mensagens(request, conversa_id):
    """
    Recupera as mensagens de uma conversa específica para atualização do chat.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    centro_id = request.user.centro_profile.id
    
    centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
    conversa = get_object_or_404(Conversa, id=conversa_id, centro=centro)
    
    # Buscar mensagens normais + apenas a última mensagem de digitando do centro
    mensagens_normais = Mensagem.objects.filter(
        conversa=conversa, 
        digitando=False
    ).select_related('remetente_aluno', 'remetente_centro')
    
    ultima_digitando = Mensagem.objects.filter(
        conversa=conversa,
        remetente_centro=centro,
        digitando=True
    ).order_by('-data_envio').first()
    
    mensagens_data = []
    
    for msg in mensagens_normais:
        foto_perfil = None
        inicial = None
        
        if msg.remetente_aluno and hasattr(msg.remetente_aluno, 'perfil'):
            if msg.remetente_aluno.perfil:
                foto_perfil = msg.remetente_aluno.perfil.get_foto_perfil_url()
                inicial = msg.remetente_aluno.perfil.get_inicial_nome()
        
        mensagens_data.append({
            'id': msg.id,
            'mensagem': msg.mensagem,
            'tipo': msg.tipo,
            'is_centro': msg.is_centro(),
            'remetente_nome': msg.remetente.nome if msg.remetente_aluno else msg.remetente_centro.nome,
            'foto_perfil': foto_perfil,
            'inicial': inicial,
            'data_envio': msg.data_envio.strftime('%H:%M'),
            'digitando': msg.digitando
        })
    
    if ultima_digitando:
        mensagens_data.append({
            'id': ultima_digitando.id,
            'mensagem': ultima_digitando.mensagem,
            'tipo': ultima_digitando.tipo,
            'is_centro': ultima_digitando.is_centro(),
            'remetente_nome': ultima_digitando.remetente_centro.nome,
            'foto_perfil': None,
            'inicial': None,
            'data_envio': ultima_digitando.data_envio.strftime('%H:%M'),
            'digitando': True
        })
    
    return JsonResponse({'mensagens': mensagens_data})



@login_required
def iniciar_conversa_centro(request, centro_id):
    """Iniciar uma nova conversa com um centro"""
    try:
        if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
            messages.error(request, 'Você precisa estar logado como aluno para iniciar uma conversa.')
            return redirect('login_aluno')
        
        aluno = request.user.aluno_profile
        centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
        
        # Verificar se já existe uma conversa
        conversa, created = Conversa.objects.get_or_create(
            centro=centro,
            aluno=aluno,
            defaults={
                'data_criacao': timezone.now(),
                'ultima_mensagem': timezone.now()
            }
        )
        
        # Redirecionar para a página de perfil do centro
        return redirect('cursos_por_centro', centro_id=centro.id)
        
    except Aluno.DoesNotExist:
        messages.error(request, 'Aluno não encontrado. Faça login novamente.')
        return redirect('login_aluno')
    except Exception as e:
        messages.error(request, f'Erro ao iniciar conversa: {str(e)}')
        return redirect('listar_cursos')



@login_required
def centro_chat_modal(request, centro_id):
    """View para carregar o modal de chat no perfil do centro"""
    try:
        centro = get_object_or_404(CentroDeFormacao, id=centro_id, ativo=True)
        if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
        
        aluno = request.user.aluno_profile
        
        # Buscar ou criar conversa
        conversa, created = Conversa.objects.get_or_create(
            centro=centro,
            aluno=aluno,
            defaults={
                'data_criacao': timezone.now(),
                'ultima_mensagem': timezone.now()
            }
        )
        
        # Buscar mensagens
        mensagens = Mensagem.objects.filter(conversa=conversa).select_related(
            'remetente_aluno', 'remetente_centro'
        ).order_by('data_envio')
        
        mensagens_data = []
        for msg in mensagens:
            mensagens_data.append({
                'id': msg.id,
                'mensagem': msg.mensagem,
                'is_centro': msg.is_centro(),
                'remetente_nome': msg.remetente_centro.nome if msg.is_centro() else aluno.nome,
                'data_envio': msg.data_envio.strftime('%H:%M'),
                'digitando': msg.digitando
            })
        
        # NOVO: Incluir cursos para o catálogo inicial no modal
        cursos_centro = centro.cursos.filter(ativo=True, publicado=True).order_by('-destaque', '-data_criacao')[:6]
        cursos_data = [{'titulo': c.titulo, 'url': c.get_absolute_url()} for c in cursos_centro]
        
        return JsonResponse({
            'success': True,
            'conversa_id': conversa.id,
            'mensagens': mensagens_data,
            'centro_nome': centro.nome,
            'aluno_nome': aluno.nome,
            'cursos': cursos_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def enviar_mensagem_centro_modal(request):
    """
    Versão unificada para o aluno enviar mensagens via modal ou página de chat.
    Suporta JSON (apenas texto) e FormData (texto + multimédia).
    """
    if request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'error': 'Acesso restrito a alunos'}, status=403)
    
    try:
        conversa_id = None
        mensagem_texto = ""
        arquivo = None

        # Tentar obter dados independentemente do Content-Type (mais robusto)
        if request.content_type and 'application/json' in request.content_type:
            try:
                data = json.loads(request.body)
                conversa_id = data.get('conversa_id')
                mensagem_texto = data.get('mensagem', '')
            except:
                pass
        
        # Se não veio via JSON, ou se JSON falhou, tentar POST
        if not conversa_id:
            conversa_id = request.POST.get('conversa_id')
            mensagem_texto = request.POST.get('mensagem', '')
            arquivo = request.FILES.get('arquivo')

        if not conversa_id:
            print("[CHAT ERROR] conversa_id não encontrado no pedido")
            return JsonResponse({'success': False, 'error': 'Conversa não especificada'}, status=400)

        aluno = request.user.aluno_profile
        conversa = get_object_or_404(Conversa, id=conversa_id, aluno=aluno)

        tipo_msg = 'TEXTO'
        if arquivo:
            ext = arquivo.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                tipo_msg = 'IMAGEM'
            else:
                tipo_msg = 'ARQUIVO'

        mensagem = Mensagem.objects.create(
            conversa=conversa,
            remetente_aluno=aluno,
            mensagem=mensagem_texto,
            arquivo=arquivo,
            tipo=tipo_msg
        )
        
        # Atualizar última mensagem da conversa
        from django.utils import timezone
        conversa.ultima_mensagem = timezone.now()
        conversa.save()

        return JsonResponse({
            'success': True,
            'mensagem_id': mensagem.id,
            'data_envio': mensagem.data_envio.strftime('%H:%M'),
            'is_centro': False
        })
        
    except Exception as e:
        print(f"[CHAT ERROR] Erro geral ao enviar: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def atualizar_digitando_modal(request):
    """Atualizar status de digitando no modal"""
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        conversa_id = data.get('conversa_id')
        digitando = data.get('digitando', False)
        
        aluno = request.user.aluno_profile
        conversa = get_object_or_404(Conversa, id=conversa_id, aluno=aluno)
        
        # Buscar mensagem de digitando existente
        mensagem_digitando = Mensagem.objects.filter(
            conversa=conversa, 
            remetente_aluno=aluno, 
            digitando=True
        ).first()
        
        if digitando:
            if not mensagem_digitando:
                Mensagem.objects.create(
                    conversa=conversa,
                    remetente_aluno=aluno,
                    mensagem='...',
                    tipo='TEXTO',
                    digitando=True
                )
        else:
            if mensagem_digitando:
                mensagem_digitando.delete()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def buscar_mensagens_modal(request, conversa_id):
    """Buscar mensagens para o modal"""
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    aluno = request.user.aluno_profile
    conversa = get_object_or_404(Conversa, id=conversa_id, aluno=aluno)
    
    # Buscar mensagens normais + digitando
    mensagens_normais = Mensagem.objects.filter(
        conversa=conversa, 
        digitando=False
    ).select_related('remetente_aluno', 'remetente_centro')
    
    ultima_digitando = Mensagem.objects.filter(
        conversa=conversa,
        remetente_aluno=aluno,
        digitando=True
    ).order_by('-data_envio').first()
    
    mensagens_data = []
    
    for msg in mensagens_normais:
        mensagens_data.append({
            'id': msg.id,
            'mensagem': msg.mensagem,
            'is_centro': msg.is_centro(),
            'remetente_nome': msg.remetente_centro.nome if msg.is_centro() else aluno.nome,
            'data_envio': msg.data_envio.strftime('%H:%M'),
            'digitando': False
        })
    
    if ultima_digitando:
        mensagens_data.append({
            'id': ultima_digitando.id,
            'mensagem': ultima_digitando.mensagem,
            'is_centro': False,
            'remetente_nome': aluno.nome,
            'data_envio': ultima_digitando.data_envio.strftime('%H:%M'),
            'digitando': True
        })
    
    # NOVO: Incluir cursos para o catálogo inicial no modal
    cursos_centro = conversa.centro.cursos.filter(ativo=True, publicado=True).order_by('-destaque', '-data_criacao')[:6]
    cursos_data = [{'titulo': c.titulo, 'url': c.get_absolute_url()} for c in cursos_centro]
    
    return JsonResponse({
        'mensagens': mensagens_data,
        'cursos': cursos_data
    })


# --- New Home Views ---

def home_centros(request):
    """
    Página inicial dedicada aos Centros de Formação (Parceiros).
    """
    # 1. Featured Centers (Destaques/Mais Populares)
    centros_destaque = CentroDeFormacao.objects.filter(
        ativo=True
    ).annotate(
        num_cursos=Count('cursos', filter=Q(cursos__ativo=True)),
        num_seguidores=Count('seguidores')
    ).order_by('-num_seguidores')[:4]
    
    # 2. Newest Partners
    centros_novos = CentroDeFormacao.objects.filter(
        ativo=True
    ).order_by('-data_criacao')[:4]
    
    # 3. All Centers (for grid)
    centros_todos = CentroDeFormacao.objects.filter(ativo=True).order_by('nome')[:8]
    
    context = {
        'centros_destaque': centros_destaque,
        'centros_novos': centros_novos,
        'centros_todos': centros_todos,
        'active_menu': 'centros',
    }
    
    return render(request, 'gestoreduka/home_centros.html', context)

def api_load_more_centros(request):
    """
    API para carregar mais centros na home via scroll infinito ou botão "Ver Mais".
    """
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 8))
        
        qs = CentroDeFormacao.objects.filter(ativo=True).order_by('nome')
        centros = qs[offset:offset+limit]
        
        data = []
        for centro in centros:
            # Safe layout access
            banner = centro.perfil.banner.url if hasattr(centro, 'perfil') and centro.perfil.banner else '/static/assets/images/bg/bg-image-10.jpg'
            logo = centro.perfil.imagem.url if hasattr(centro, 'perfil') and centro.perfil.imagem else '/static/assets/images/team/team-01.jpg'
            
            data.append({
                'id': centro.id,
                'nome': centro.nome,
                'endereco': centro.endereco,
                'banner_url': banner,
                'logo_url': logo,
                'num_cursos': centro.cursos.filter(ativo=True).count(),
                'url_detalhe': reverse('cursos_por_centro', args=[centro.id]) # Assuming this view exists or similar
            })
            
        return JsonResponse({'centros': data, 'has_more': qs.count() > offset + limit})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def gerenciar_filiais(request):
    """
    Listagem e gerenciamento de filiais pelo Centro Principal.
    """
    if not request.user.is_authenticated:
        messages.error(request, "Acesso negado. Apenas o gestor principal pode gerir filiais.")
        return redirect('login_gestor')
        
    centro = request.user.centro_profile
    filiais = centro.filiais.select_related('usuario').all()
    
    return render(request, 'gestor/filiais/listar.html', {
        'centro': centro,
        'filiais': filiais
    })

from django.db import transaction

def criar_filial(request):
    """
    Cadastro de uma nova filial pelo Centro Principal.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro = request.user.centro_profile
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        endereco = request.POST.get('endereco')
        contato = request.POST.get('contato')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        
        try:
            with transaction.atomic():
                from usuarios.models import Usuario
                # 1. Cria o utilizador da filial
                if Usuario.objects.filter(email=email).exists():
                    messages.error(request, 'Já existe um utilizador com este email.')
                    return render(request, 'gestor/filiais/form.html', {'centro': centro, 'action': 'Criar'})
                
                usuario_filial = Usuario.objects.create(
                    email=email,
                    nome=nome,
                    tipo_usuario='GESTOR_FILIAL'
                )
                usuario_filial.set_password(senha)
                usuario_filial.save()
                
                # 2. Cria o perfil da filial
                filial = Filial.objects.create(
                    centro_principal=centro,
                    usuario=usuario_filial,
                    nome=nome,
                    endereco=endereco,
                    contato=contato,
                    latitude=lat if lat else None,
                    longitude=lng if lng else None
                )
                
                messages.success(request, f'Filial "{filial.nome}" criada com sucesso!')
                return redirect('gerenciar_filiais')
        except Exception as e:
            messages.error(request, f'Erro ao criar filial: {str(e)}')
            
    return render(request, 'gestor/filiais/form.html', {
        'centro': centro,
        'action': 'Criar'
    })

def editar_filial(request, filial_id):
    """
    Edição de uma filial existente pelo Centro Principal.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro = request.user.centro_profile
    filial = get_object_or_404(Filial, id=filial_id, centro_principal=centro)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        contato = request.POST.get('contato')
        senha = request.POST.get('senha')
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        
        try:
            with transaction.atomic():
                # Atualizar perfil filial
                filial.nome = nome
                filial.endereco = endereco
                filial.contato = contato
                if lat and lng:
                    filial.latitude = lat
                    filial.longitude = lng
                filial.save()
                
                # Atualizar utilizador se nome mudou
                if filial.usuario:
                    usuario = filial.usuario
                    usuario.nome = nome
                    if senha:  # Mudar senha se fornecida
                        usuario.set_password(senha)
                    usuario.save()
                    
                messages.success(request, f'Filial "{filial.nome}" atualizada com sucesso!')
                return redirect('gerenciar_filiais')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar filial: {str(e)}')
            
    return render(request, 'gestor/filiais/form.html', {
        'centro': centro,
        'filial': filial,
        'action': 'Editar'
    })

def gerenciar_alunos(request):
    """
    Motor de Busca e listagem de todos os alunos inscritos nos cursos do centro/filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    # Buscar IDs dos cursos pertencentes ao centro/filial
    cursos_ids = filial.cursos_disponiveis.values_list('id', flat=True) if filial else centro.cursos.values_list('id', flat=True)
    
    # Encontrar todas as inscrições nesses cursos
    from cursos_app.models import Inscricao
    inscricoes = Inscricao.objects.filter(curso_id__in=cursos_ids)
    matriculas = Matricula.objects.filter(curso_id__in=cursos_ids)
    alunos_ids = set(inscricoes.values_list('aluno_id', flat=True)) | set(matriculas.values_list('aluno_id', flat=True))
    
    from usuarios.models import Aluno
    alunos = Aluno.objects.filter(id__in=alunos_ids).select_related('usuario', 'perfil')
    
    # Lógica de pesquisa
    query = request.GET.get('q', '')
    if query:
        alunos = alunos.filter(
            Q(nome__icontains=query) |
            Q(usuario__email__icontains=query) |
            Q(id__icontains=query)
        )
        
    return render(request, 'gestor/alunos/listar.html', {
        'centro': centro,
        'filial': filial,
        'alunos': alunos,
        'query': query
    })

def dossie_aluno(request, aluno_id):
    """
    Visão detalhada (Dossiê) do histórico académico de um aluno no centro/filial atual.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    from usuarios.models import Aluno
    aluno = get_object_or_404(Aluno, id=aluno_id)
    
    cursos_ids = filial.cursos_disponiveis.values_list('id', flat=True) if filial else centro.cursos.values_list('id', flat=True)
    
    from cursos_app.models import Inscricao
    inscricoes = Inscricao.objects.filter(aluno=aluno, curso_id__in=cursos_ids).select_related('curso', 'turma_escolhida').order_by('-data_inscricao')
    matriculas = Matricula.objects.filter(aluno=aluno, curso_id__in=cursos_ids).select_related('curso', 'turma', 'inscricao').order_by('-data_matricula')
    
    if not inscricoes.exists() and not matriculas.exists():
        messages.warning(request, "O aluno selecionado não possui histórico neste Centro/Filial.")
        return redirect('gerenciar_alunos')
        
    return render(request, 'gestor/alunos/dossie.html', {
        'centro': centro,
        'filial': filial,
        'aluno': aluno,
        'inscricoes': inscricoes,
        'matriculas': matriculas,
    })

from django.db.models import Sum
from django.utils import timezone

def gerenciar_financeiro(request):
    """
    Gestão do fluxo de caixa (mensalidades, taxas de inscrição).
    Gestor vê o global e quebra por filial. Filial vê apenas o seu.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    from cursos_app.models import Inscricao
    
    # Se GESTOR, pode ver todos os cursos do Centro (incluindo os das Filiais, que também pertecem ao Centro)
    # Mas como o modelo Filial é novo, o Curso tem ForeignKey para Centro e Filial(null=True).
    if request.user.tipo_usuario == 'GESTOR':
        inscricoes_pagas = Inscricao.objects.filter(
            curso__centro=centro,
            valor_pago__gt=0
        ).select_related('curso', 'aluno__usuario').order_by('-data_pagamento', '-data_inscricao')
        
        # Agregação global
        total_receita = inscricoes_pagas.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
        
        # Agregação por filial (null = Centro Mãe)
        receita_centro_mae = inscricoes_pagas.filter(curso__filiais__isnull=True).aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
        
        # Receitas das filiais
        filiais_receita = []
        for fil in centro.filiais.all():
            receitas_f = inscricoes_pagas.filter(curso__filiais=fil).aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
            if receitas_f > 0:
                filiais_receita.append({'nome': fil.nome, 'total': receitas_f})
                
    else:
        # É GESTOR_FILIAL - só os cursos da filial
        inscricoes_pagas = Inscricao.objects.filter(
            curso__filiais=filial,
            valor_pago__gt=0
        ).select_related('curso', 'aluno__usuario').order_by('-data_pagamento', '-data_inscricao')
        
        total_receita = inscricoes_pagas.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
        receita_centro_mae = 0
        filiais_receita = []

    # Recebimentos presenciais confirmados
    recebimentos_qs = RecebimentoCentro.objects.filter(centro=centro, estado='CONFIRMADO')
    if filial:
        recebimentos_qs = recebimentos_qs.filter(matricula__turma__filial=filial)
    recebimentos_recentes = recebimentos_qs.select_related('aluno__usuario', 'matricula__curso', 'matricula__turma').order_by('-data_recebimento')[:50]
    total_recebimentos = recebimentos_qs.aggregate(Sum('valor'))['valor__sum'] or 0

    # Pagamentos recentes da plataforma
    pagamentos_recentes = inscricoes_pagas[:50]
    
    return render(request, 'gestor/financeiro/dashboard.html', {
        'centro': centro,
        'filial': filial,
        'total_receita': total_receita,
        'receita_centro_mae': receita_centro_mae,
        'filiais_receita': filiais_receita,
        'pagamentos_recentes': pagamentos_recentes,
        'recebimentos_recentes': recebimentos_recentes,
        'total_recebimentos': total_recebimentos
    })
@login_required
def listar_anuncios(request):
    """Listagem de anúncios do centro para o gestor"""
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:
        messages.error(request, "Acesso negado. Apenas a Sede pode gerir comunicados.")
        return redirect('centro_dashboard')
        
    anuncios = centro.anuncios.all().order_by('-data_publicacao')
    
    return render(request, 'gestor/anuncios/listar.html', {
        'centro': centro,
        'anuncios': anuncios
    })

@login_required
def criar_anuncio(request):
    """Criação de um novo anúncio institucional"""
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:
        messages.error(request, "Acesso negado. Apenas a Sede pode criar comunicados.")
        return redirect('centro_dashboard')
        
    if request.method == 'POST':
        from .forms import AnuncioForm
        form = AnuncioForm(request.POST, request.FILES)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.centro = centro
            anuncio.save()
            
            # Notificar todos os seguidores
            from usuarios.models import NotificacaoAluno
            seguidores = centro.seguidores.all()
            notificacoes = []
            
            for seguimento in seguidores:
                notificacoes.append(NotificacaoAluno(
                    aluno=seguimento.aluno,
                    titulo=f"Novo comunicado de {centro.nome}",
                    mensagem=f"{anuncio.titulo}",
                    link=f"/cursos/instituicoes/",
                    tipo='ANUNCIO'
                ))
                
            if notificacoes:
                NotificacaoAluno.objects.bulk_create(notificacoes)
                
            messages.success(request, 'Anúncio publicado com sucesso! Os seus seguidores foram notificados.')
            return redirect('listar_anuncios')
    else:
        from .forms import AnuncioForm
        form = AnuncioForm()
        
    return render(request, 'gestor/anuncios/form.html', {
        'centro': centro,
        'form': form,
        'title': 'Novo Anúncio'
    })

from django.shortcuts import get_object_or_404

@login_required
def editar_anuncio(request, anuncio_id):
    """Edição de um anúncio institucional existente"""
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:
        messages.error(request, "Acesso negado. Apenas a Sede pode editar comunicados.")
        return redirect('centro_dashboard')
        
    from gestoreduka.models import AnuncioCentro
    anuncio = get_object_or_404(AnuncioCentro, id=anuncio_id, centro=centro)
        
    if request.method == 'POST':
        from .forms import AnuncioForm
        form = AnuncioForm(request.POST, request.FILES, instance=anuncio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anúncio atualizado com sucesso!')
            return redirect('listar_anuncios')
    else:
        from .forms import AnuncioForm
        form = AnuncioForm(instance=anuncio)
        
    return render(request, 'gestor/anuncios/form.html', {
        'centro': centro,
        'form': form,
        'title': 'Editar Anúncio',
        'anuncio': anuncio
    })

@login_required
def excluir_anuncio(request, anuncio_id):
    """Excluir um anúncio institucional existente"""
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:
        messages.error(request, "Acesso negado. Apenas a Sede pode apagar comunicados.")
        return redirect('centro_dashboard')
        
    from gestoreduka.models import AnuncioCentro
    anuncio = get_object_or_404(AnuncioCentro, id=anuncio_id, centro=centro)
    
    if request.method == 'POST':
        anuncio.delete()
        messages.success(request, 'Anúncio eliminado com sucesso!')
        return redirect('listar_anuncios')
        
    # Se for GET, podemos redirecionar para listar ou mostrar página de confirmação
    return redirect('listar_anuncios')


@login_required
def gerenciar_comentarios(request):
    """Listagem de comentários dos alunos nos cursos do centro"""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    from avaliacoes.models import Comentario
    comentarios = Comentario.objects.filter(curso__centro=centro).select_related('aluno', 'curso').order_by('-data_comentario')
    
    return render(request, 'gestor/comentarios/listar.html', {
        'centro': centro,
        'comentarios': comentarios
    })

@login_required
def responder_comentario(request, comentario_id):
    """Processa a resposta do gestor a um comentário"""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    from avaliacoes.models import Comentario
    from usuarios.models import NotificacaoAluno
    comentario = get_object_or_404(Comentario, id=comentario_id, curso__centro=centro)
    
    if request.method == 'POST':
        resposta = request.POST.get('resposta', '').strip()
        if resposta:
            comentario.resposta = resposta
            comentario.resposta_data = timezone.now()
            comentario.save()
            
            # Notificar o aluno que sua dúvida foi respondida
            NotificacaoAluno.objects.create(
                aluno=comentario.aluno,
                titulo=f"Resposta ao seu comentário",
                mensagem=f"O centro {centro.nome} respondeu à sua dúvida no curso {comentario.curso.titulo}.",
                link=f"/cursos/curso_detalhe/{comentario.curso.id}/",
                tipo='CURSO'
            )
            
            messages.success(request, 'Resposta enviada com sucesso! O aluno foi notificado.')
        else:
            messages.error(request, 'A resposta não pode estar vazia.')
            
    return redirect('gerenciar_comentarios')

def validar_inscricao(request):
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, filial = get_gestor_context(request.user)
    if not centro:
        messages.error(request, "Acesso negado.")
        return redirect('login_gestor')

    if request.method == 'POST':
        codigo = request.POST.get('codigo_inscricao', '').strip()

        if not codigo:
            messages.error(request, "Por favor, insira um código de inscrição válido.")
            return redirect('gestor_inscricoes')

        try:
            inscricao = Inscricao.objects.get(codigo_inscricao__iexact=codigo, curso__centro=centro)
            if inscricao.status == 'A':
                messages.success(request, f"Ficha Validada! O aluno {inscricao.aluno.nome} tem a inscrição PAGA e APROVADA.")
            elif inscricao.status == 'P':
                messages.warning(request, f"Ficha encontrada, mas a inscrição do aluno {inscricao.aluno.nome} ainda está PENDENTE.")
            elif inscricao.status == 'N':
                messages.error(request, f"A inscrição do aluno {inscricao.aluno.nome} foi REJEITADA ou CANCELADA.")
                
        except Inscricao.DoesNotExist:
            messages.error(request, "Código inválido ou a inscrição não pertence a este centro.")
            
    return redirect('gestor_inscricoes')


# ==========================================
# GESTÃO DE FILIAIS
# ==========================================
from django.contrib.auth import get_user_model
from usuarios.models import Usuario

def gerenciar_filiais(request):
    """Lista as filiais do Centro Master."""
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:  # Apenas Master pode ver filiais
        messages.error(request, "Acesso negado. Apenas a Sede (Master) pode gerir filiais.")
        return redirect('centro_dashboard')
        
    filiais = centro.filiais.all()
    
    context = {
        'centro': centro,
        'filiais': filiais,
    }
    return render(request, 'gestor/filiais/lista.html', context)

def criar_filial(request):
    """Cria uma nova filial e o respectivo usuário GESTOR_FILIAL."""
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:
        messages.error(request, "Acesso negado.")
        return redirect('centro_dashboard')
        
    if request.method == 'POST':
        nome = request.POST.get('nome')
        endereco = request.POST.get('endereco')
        telefone = request.POST.get('telefone')
        email = request.POST.get('email')
        whatsapp = request.POST.get('whatsapp')
        senha = request.POST.get('senha')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        # Converter para decimal se não estiver vazio
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            latitude = None
            longitude = None
        
        if Filial.objects.filter(email=email).exists() or Usuario.objects.filter(email=email).exists():
            messages.error(request, "Já existe uma filial ou utilizador com este e-mail.")
        else:
            try:
                # 1. Criar Utilizador
                novo_usuario = Usuario.objects.create_user(
                    email=email,
                    password=senha,
                    nome=f"Gestor - {nome}",
                    tipo_usuario='GESTOR_FILIAL'
                )
                
                # 2. Criar Filial
                nova_filial = Filial.objects.create(
                    centro_principal=centro,
                    usuario=novo_usuario,
                    nome=nome,
                    endereco=endereco,
                    telefone=telefone,
                    email=email,
                    whatsapp=whatsapp,
                    latitude=latitude,
                    longitude=longitude
                )
                
                # 3. Copiar Categorias
                nova_filial.categorias.set(centro.categorias.all())
                
                messages.success(request, "Filial criada com sucesso!")
                return redirect('gerenciar_filiais')
            except Exception as e:
                messages.error(request, f"Erro ao criar filial: {str(e)}")
                
    context = {
        'centro': centro,
        'acao': 'Criar'
    }
    return render(request, 'gestor/filiais/form.html', context)

def editar_filial(request, filial_id):
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, is_filial = get_gestor_context(request.user)
    if not centro or is_filial:
        messages.error(request, "Acesso negado.")
        return redirect('centro_dashboard')
        
    filial_obj = get_object_or_404(Filial, id=filial_id, centro_principal=centro)
    
    if request.method == 'POST':
        filial_obj.nome = request.POST.get('nome')
        filial_obj.endereco = request.POST.get('endereco')
        filial_obj.telefone = request.POST.get('telefone')
        filial_obj.whatsapp = request.POST.get('whatsapp')
        
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        try:
            if latitude: filial_obj.latitude = float(latitude)
            if longitude: filial_obj.longitude = float(longitude)
        except ValueError:
            pass
        
        nova_senha = request.POST.get('senha')
        if nova_senha and filial_obj.usuario:
            filial_obj.usuario.set_password(nova_senha)
            filial_obj.usuario.save()
            
        filial_obj.save()
        messages.success(request, "Filial atualizada com sucesso!")
        return redirect('gerenciar_filiais')
        
    context = {
        'centro': centro,
        'filial_obj': filial_obj,
        'acao': 'Editar'
    }
    return render(request, 'gestor/filiais/form.html', context)

def excluir_filial(request, filial_id):
    if not request.user.is_authenticated:
        return redirect('login_gestor')
        
    centro, is_filial = get_gestor_context(request.user)
    if not centro or is_filial:
        messages.error(request, "Acesso negado.")
        return redirect('centro_dashboard')
        
    filial_obj = get_object_or_404(Filial, id=filial_id, centro_principal=centro)
    
    if request.method == 'POST':
        usuario = filial_obj.usuario
        filial_obj.delete()
        if usuario:
            usuario.delete()
        messages.success(request, "Filial excluída com sucesso!")
        
    return redirect('gerenciar_filiais')

@login_required
def atribuir_cursos_filial(request, filial_id):
    if request.user.tipo_usuario != 'GESTOR':
        messages.error(request, "Apenas o Gestor Principal pode atribuir cursos a filiais.")
        return redirect('gestor_dashboard')
        
    centro = request.user.centro_profile
    filial = get_object_or_404(Filial, id=filial_id, centro_principal=centro, ativo=True)
    
    # Cursos do centro principal
    cursos_centro = Curso.objects.filter(centro=centro, ativo=True)
    
    # Cursos que a filial já tem
    cursos_filial = filial.cursos_disponiveis.all()
    
    # Cursos disponíveis para atribuir (que a filial não tem)
    cursos_disponiveis = cursos_centro.exclude(id__in=cursos_filial.values_list('id', flat=True))
    
    if request.method == 'POST':
        curso_ids = request.POST.getlist('cursos')
        if not curso_ids:
            messages.warning(request, "Selecione pelo menos um curso para atribuir.")
            return redirect('atribuir_cursos_filial', filial_id=filial_id)
            
        cursos_para_atribuir = cursos_centro.filter(id__in=curso_ids)
        
        from django.db import transaction
        
        with transaction.atomic():
            for curso in cursos_para_atribuir:
                curso.filiais.add(filial)
                
        messages.success(request, f"{cursos_para_atribuir.count()} curso(s) atribuído(s) com sucesso à filial {filial.nome}.")
        return redirect('gerenciar_filiais')
        
    context = {
        'filial': filial,
        'cursos_disponiveis': cursos_disponiveis,
        'cursos_atuais': cursos_filial
    }
    return render(request, 'gestor/filiais/atribuir_cursos.html', context)



@login_required
def gerir_presencas_turma(request, turma_id):
    """Permite ao gestor marcar a assiduidade diária da turma."""
    try:
        centro = request.user.centro_profile
    except Exception:
        messages.error(request, 'Não foi possível identificar o centro associado à sua conta.')
        return redirect('login_gestor')

    turma = get_object_or_404(Turma, pk=turma_id, curso__centro=centro)
    data_str = request.POST.get('data') or request.GET.get('data')
    try:
        data_aula = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else timezone.localdate()
    except ValueError:
        data_aula = timezone.localdate()

    inscricoes = list(
        Inscricao.objects.filter(turma_escolhida=turma, status='A')
        .select_related('aluno')
        .order_by('aluno__nome')
    )

    if request.method == 'POST':
        estados_validos = {choice[0] for choice in Presenca.ESTADO_CHOICES}
        for inscricao in inscricoes:
            estado = request.POST.get(f'estado_{inscricao.pk}', 'PRESENTE')
            if estado not in estados_validos:
                estado = 'PRESENTE'
            Presenca.objects.update_or_create(
                turma=turma,
                inscricao=inscricao,
                data=data_aula,
                defaults={
                    'estado': estado,
                    'observacao': request.POST.get(f'observacao_{inscricao.pk}', '').strip(),
                },
            )
        messages.success(request, f'Presenças de {data_aula.strftime("%d/%m/%Y")} registadas com sucesso.')
        return redirect(f'{reverse("gerir_presencas_turma", args=[turma.pk])}?data={data_aula.isoformat()}')

    registos = {
        reg.inscricao_id: reg
        for reg in Presenca.objects.filter(turma=turma, data=data_aula)
    }
    return render(request, 'gestor/turmas/presencas.html', {
        'turma': turma,
        'inscricoes': inscricoes,
        'registos': registos,
        'data_aula': data_aula,
        'estados_presenca': Presenca.ESTADO_CHOICES,
    })


@login_required
def gerir_notas_turma(request, turma_id):
    """Permite ao gestor lançar a nota final dos alunos matriculados."""
    try:
        centro = request.user.centro_profile
    except Exception:
        messages.error(request, 'Não foi possível identificar o centro associado à sua conta.')
        return redirect('login_gestor')

    turma = get_object_or_404(Turma, pk=turma_id, curso__centro=centro)
    inscricoes = list(
        Inscricao.objects.filter(turma_escolhida=turma, status='A')
        .select_related('aluno')
        .order_by('aluno__nome')
    )

    if request.method == 'POST':
        for inscricao in inscricoes:
            valor = request.POST.get(f'nota_{inscricao.pk}', '').strip().replace(',', '.')
            if not valor:
                continue
            try:
                nota = float(valor)
            except ValueError:
                messages.error(request, f'A nota de {inscricao.aluno.nome} não é válida.')
                continue
            if nota < 0 or nota > 20:
                messages.error(request, f'A nota de {inscricao.aluno.nome} deve estar entre 0 e 20.')
                continue
            NotaAluno.objects.update_or_create(
                turma=turma,
                inscricao=inscricao,
                avaliacao='Nota Final',
                defaults={'nota': nota, 'observacao': request.POST.get(f'observacao_{inscricao.pk}', '').strip()},
            )
        messages.success(request, 'Notas finais guardadas com sucesso.')
        return redirect('gerir_notas_turma', turma_id=turma.pk)

    notas = {
        nota.inscricao_id: nota
        for nota in NotaAluno.objects.filter(turma=turma, avaliacao='Nota Final')
    }
    return render(request, 'gestor/turmas/notas.html', {
        'turma': turma,
        'inscricoes': inscricoes,
        'notas': notas,
    })


@csrf_exempt
@require_POST
def receber_integracao_eduka(request):
    """Recebe uma inscrição externa e processa-a sem duplicar alunos ou eventos."""
    chave_esperada = getattr(settings, 'EDUKA_INTEGRATION_KEY', '') or (getattr(settings, 'DEBUG', False) and 'eduka-dev-key')
    chave_recebida = request.headers.get('X-Eduka-Integration-Key', '')
    if not chave_esperada or chave_recebida != chave_esperada:
        return JsonResponse({'ok': False, 'erro': 'Credenciais de integração inválidas.'}, status=401)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'erro': 'O corpo deve conter JSON válido.'}, status=400)

    external_id = str(payload.get('external_id') or payload.get('inscricao_id') or '').strip()
    centro_id = payload.get('centro_id')
    if not external_id or not centro_id:
        return JsonResponse({'ok': False, 'erro': 'external_id e centro_id são obrigatórios.'}, status=400)

    try:
        centro = CentroDeFormacao.objects.get(pk=centro_id, ativo=True)
    except CentroDeFormacao.DoesNotExist:
        return JsonResponse({'ok': False, 'erro': 'Centro não encontrado.'}, status=404)

    evento, criado = EventoIntegracao.objects.get_or_create(
        centro=centro,
        external_id=external_id,
        tipo=str(payload.get('tipo') or 'INSCRICAO'),
        defaults={'payload': payload},
    )
    if not criado and evento.status == 'PROCESSADO':
        return JsonResponse({'ok': True, 'duplicado': True, 'evento_id': evento.pk})

    try:
        from django.db import transaction
        with transaction.atomic():
            evento.payload = payload
            aluno_data = payload.get('aluno') or {}
            email = (aluno_data.get('email') or payload.get('email') or '').strip().lower()
            nome = (aluno_data.get('nome') or payload.get('nome') or '').strip()
            if not email or not nome:
                raise ValueError('Os dados do aluno exigem nome e email.')

            User = get_user_model()
            user, _ = User.objects.get_or_create(email=email, defaults={'nome': nome, 'tipo_usuario': 'ALUNO', 'is_active': True})
            if nome and user.nome != nome:
                user.nome = nome
                user.save(update_fields=['nome'])
            aluno, _ = Aluno.objects.get_or_create(usuario=user, defaults={'nome': nome})
            if aluno.nome != nome:
                aluno.nome = nome
                aluno.save(update_fields=['nome'])

            curso_id = payload.get('curso_id') or (payload.get('curso') or {}).get('id')
            curso_slug = payload.get('curso_slug') or (payload.get('curso') or {}).get('slug')
            curso_qs = Curso.objects.filter(centro=centro)
            curso = curso_qs.filter(pk=curso_id).first() if curso_id else None
            if not curso and curso_slug:
                curso = curso_qs.filter(slug=curso_slug).first()
            if not curso:
                raise ValueError('Curso não encontrado no centro.')

            turma_id = payload.get('turma_id') or (payload.get('turma') or {}).get('id')
            turma_codigo = payload.get('turma_codigo') or (payload.get('turma') or {}).get('codigo')
            turma = Turma.objects.filter(curso=curso, pk=turma_id).first() if turma_id else None
            if not turma and turma_codigo:
                turma = Turma.objects.filter(curso=curso, codigo=turma_codigo).first()

            inscricao, _ = Inscricao.objects.get_or_create(
                aluno=aluno,
                curso=curso,
                defaults={
                    'turma_escolhida': turma,
                    'tipo_inscricao': 'ONLINE',
                    'status': 'P',
                    'observacoes': 'Recebida através da integração Eduka-Angola.',
                },
            )
            if turma and inscricao.turma_escolhida_id != turma.pk:
                inscricao.turma_escolhida = turma
            inscricao.tipo_inscricao = 'ONLINE'
            inscricao.observacoes = 'Recebida através da integração Eduka-Angola.'
            pago = bool(payload.get('pagamento_confirmado') or payload.get('status_pagamento') in ('ACCEPTED', 'CONFIRMED', 'PAGO'))
            inscricao.status = 'A' if pago else 'P'
            if payload.get('valor_pago') is not None:
                from decimal import Decimal
                inscricao.valor_pago = Decimal(str(payload.get('valor_pago')))
            if pago and not inscricao.data_pagamento:
                inscricao.data_pagamento = timezone.now()
            inscricao.save()

            if pago and turma:
                matricula, _ = Matricula.objects.get_or_create(
                    inscricao=inscricao,
                    defaults={
                        'aluno': aluno, 'curso': curso, 'turma': turma,
                        'origem': 'EDUKA_ANGOLA', 'estado': 'ATIVA',
                        'valor_acordado': inscricao.valor_pago or curso.preco_atual,
                    },
                )
                if matricula.estado != 'ATIVA':
                    matricula.estado = 'ATIVA'
                    matricula.save(update_fields=['estado'])

            evento.status = 'PROCESSADO'
            evento.processado_em = timezone.now()
            AuditoriaCentro.objects.create(centro=centro, acao='SINCRONIZAR_INSCRICAO', entidade='EventoIntegracao', objeto_id=str(evento.pk), dados={'external_id': external_id, 'inscricao_id': inscricao.pk})
            evento.erro = ''
            evento.save(update_fields=['payload', 'status', 'processado_em', 'erro'])
        return JsonResponse({'ok': True, 'evento_id': evento.pk, 'inscricao_id': inscricao.pk, 'matricula_criada': bool(pago and turma)})
    except Exception as exc:
        evento.status = 'ERRO'
        evento.erro = str(exc)
        evento.save(update_fields=['payload', 'status', 'erro'])
        return JsonResponse({'ok': False, 'evento_id': evento.pk, 'erro': str(exc)}, status=422)


@login_required
def descarregar_recibo_presencial(request, recibo_id):
    """Gera o recibo PDF para um recebimento pertencente ao centro atual."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    recibo = get_object_or_404(
        RecebimentoCentro.objects.select_related('centro', 'aluno__usuario', 'matricula__curso', 'matricula__turma', 'recebido_por'),
        pk=recibo_id,
        centro=centro,
    )
    if filial and recibo.matricula.turma.filial_id != filial.pk:
        messages.error(request, 'Não tem permissão para consultar este recibo.')
        return redirect('gerenciar_financeiro')
    try:
        from weasyprint import HTML
        html_string = render_to_string('gestor/financeiro/recibo.html', {'centro': centro, 'recebimento': recibo, 'request': request})
        response = HttpResponse(HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="recibo_{recibo.referencia}.pdf"'
        return response
    except Exception as exc:
        messages.error(request, f'Não foi possível gerar o recibo: {exc}')
        return redirect('gerenciar_financeiro')


@login_required
@require_POST
def alterar_matricula(request, matricula_id):
    """Executa uma transição controlada numa matrícula do centro."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
    matricula = get_object_or_404(Matricula.objects.select_related('curso', 'turma', 'inscricao', 'aluno'), pk=matricula_id, curso__centro=centro)
    action = request.POST.get('action')
    if action == 'suspender':
        matricula.estado = 'SUSPENSA'
    elif action == 'reativar':
        matricula.estado = 'ATIVA'
    elif action == 'cancelar':
        matricula.estado = 'CANCELADA'
        matricula.data_cancelamento = timezone.now()
        if matricula.inscricao:
            matricula.inscricao.status = 'C'
            matricula.inscricao.save(update_fields=['status', 'data_cancelamento'])
    elif action == 'concluir':
        matricula.estado = 'CONCLUIDA'
        matricula.data_conclusao = timezone.now()
    elif action == 'transferir':
        nova_turma = get_object_or_404(Turma, pk=request.POST.get('nova_turma_id'), curso=matricula.curso)
        if nova_turma.vagas_disponiveis <= 0:
            messages.error(request, 'A nova turma não tem vagas disponíveis.')
            return redirect('dossie_aluno', aluno_id=matricula.aluno_id)
        matricula.turma = nova_turma
        if matricula.inscricao:
            matricula.inscricao.turma_escolhida = nova_turma
            matricula.inscricao.save(update_fields=['turma_escolhida'])
    else:
        messages.error(request, 'Operação de matrícula inválida.')
        return redirect('dossie_aluno', aluno_id=matricula.aluno_id)
    matricula.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao=f'MATRICULA_{action.upper()}', entidade='Matricula', objeto_id=str(matricula.pk), dados={'estado': matricula.estado})
    messages.success(request, f'Matrícula {matricula.codigo_matricula} atualizada com sucesso.')
    return redirect('dossie_aluno', aluno_id=matricula.aluno_id)


@login_required
@require_http_methods(['GET'])
def react_gestor_dashboard(request):
    """Contrato inicial do painel React, sempre limitado ao centro do gestor autenticado."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    cursos = (filial.cursos_disponiveis.all() if filial else centro.cursos.all()).select_related('categoria').order_by('-data_criacao')
    inscricoes = Inscricao.objects.filter(curso__centro=centro)
    plano = get_plano_ativo(centro)
    return JsonResponse({
        'gestor': {'nome': request.user.nome or request.user.email, 'email': request.user.email, 'tipo': request.user.tipo_usuario},
        'centro': {'id': centro.id, 'nome': centro.nome, 'plano': getattr(plano, 'nome', 'Sem plano'), 'filial': filial.nome if filial else ''},
        'metricas': {'cursos': cursos.count(), 'cursos_publicados': cursos.filter(publicado=True, ativo=True).count(), 'inscricoes': inscricoes.count(), 'inscricoes_pendentes': inscricoes.filter(status='P').count(), 'receita_confirmada': float(inscricoes.filter(status='A').aggregate(total=Sum('valor_pago'))['total'] or 0)},
        'cursos': [{'id': curso.id, 'titulo': curso.titulo, 'categoria': curso.categoria.nome if curso.categoria else 'Sem categoria', 'publicado': curso.publicado, 'ativo': curso.ativo, 'preco': float(curso.preco_atual), 'criado_em': curso.data_criacao.isoformat()} for curso in cursos[:12]],
    })


@login_required
@require_http_methods(['POST'])
def react_gestor_course_publish(request, curso_id):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    curso = get_object_or_404(Curso, id=curso_id, centro=centro)
    if filial and not filial.cursos_disponiveis.filter(id=curso.id).exists():
        return JsonResponse({'detail': 'Não pode alterar cursos de outra filial.'}, status=403)
    try:
        payload = json.loads(request.body or '{}')
        publicado = bool(payload['publicado'])
    except (TypeError, ValueError, KeyError):
        return JsonResponse({'detail': 'Indique o estado de publicação do curso.'}, status=400)
    curso.publicado = publicado
    curso.save(update_fields=['publicado'])
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CURSO_PUBLICADO' if publicado else 'CURSO_DESPUBLICADO', entidade='Curso', objeto_id=str(curso.pk), dados={'publicado': publicado})
    return JsonResponse({'ok': True, 'curso_id': curso.id, 'publicado': curso.publicado})


@login_required
@require_http_methods(['POST'])
def react_gestor_course_delete(request, curso_id):
    """Remove um curso do centro autenticado, mantendo a auditoria administrativa."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if filial:
        return JsonResponse({'detail': 'A remoção de cursos deve ser realizada pelo gestor principal do centro.'}, status=403)
    curso = get_object_or_404(Curso, id=curso_id, centro=centro)
    titulo = curso.titulo
    curso.delete()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CURSO_REMOVIDO', entidade='Curso', objeto_id=str(curso_id), dados={'titulo': titulo})
    return JsonResponse({'ok': True, 'curso_id': curso_id})


def _react_course_form_payload(curso):
    """Serializa os campos que o formulário React de cursos pode actualizar."""
    return {
        'id': curso.id, 'titulo': curso.titulo, 'descricao': curso.descricao,
        'descricao_curta': curso.descricao_curta, 'categoria': curso.categoria_id,
        'nivel': curso.nivel, 'idioma': curso.idioma, 'duracao': curso.duracao,
        'moeda': curso.moeda, 'modalidade': curso.modalidade,
        'carga_horaria': curso.carga_horaria, 'preco': str(curso.preco),
        'preco_inscricao': str(curso.preco_inscricao), 'mensalidade': str(curso.mensalidade),
        'tipo_cobranca_inscricao': curso.tipo_cobranca_inscricao,
        'documento_requerido': curso.documento_requerido, 'certificado': curso.certificado,
        'is_gratuito': curso.is_gratuito, 'publicado': curso.publicado,
        'destaque': curso.destaque, 'permite_parcelamento': curso.permite_parcelamento,
        'max_parcelas': curso.max_parcelas, 'preco_promocional': str(curso.preco_promocional or ''),
        'data_inicio_promocao': curso.data_inicio_promocao.isoformat() if curso.data_inicio_promocao else '',
        'data_fim_promocao': curso.data_fim_promocao.isoformat() if curso.data_fim_promocao else '',
        'instrutores': list(curso.instrutores.values_list('id', flat=True)),
        'turmas': [
            {
                'id': turma.id, 'nome': turma.nome, 'turno': turma.turno,
                'horario_inicio': turma.horario_inicio.strftime('%H:%M') if turma.horario_inicio else '',
                'horario_fim': turma.horario_fim.strftime('%H:%M') if turma.horario_fim else '',
                'dias_semana': turma.dias_semana.split(',') if turma.dias_semana else [],
                'data_inicio': turma.data_inicio.strftime('%Y-%m-%d') if turma.data_inicio else '',
                'data_fim': turma.data_fim.strftime('%Y-%m-%d') if turma.data_fim else '',
                'vagas_totais': turma.vagas_totais, 'local': turma.local, 'sala': turma.sala,
                'status': turma.status, 'observacoes': turma.observacoes,
            }
            for turma in curso.turmas.all().order_by('data_inicio', 'nome')
        ],
    }


@login_required
@require_http_methods(['GET', 'PATCH'])
def react_gestor_course_detail(request, curso_id):
    """Lê ou actualiza um curso do centro da sessão através do CursoForm existente."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    curso = get_object_or_404(Curso.objects.prefetch_related('instrutores', 'turmas'), id=curso_id, centro=centro)
    if filial and not filial.cursos_disponiveis.filter(id=curso.id).exists():
        return JsonResponse({'detail': 'Não pode gerir cursos de outra filial.'}, status=403)
    if request.method == 'GET':
        return JsonResponse({'curso': _react_course_form_payload(curso)})
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido de edição deve conter dados JSON válidos.'}, status=400)
    data = QueryDict('', mutable=True)
    for key, value in payload.items():
        if key == 'turmas':
            continue
        if isinstance(value, list):
            data.setlist(key, [str(item) for item in value])
        elif isinstance(value, bool):
            if value:
                data[key] = 'on'
        elif value is not None:
            data[key] = str(value)
    form = CursoForm(data, instance=curso, centro=centro)
    if not form.is_valid():
        return JsonResponse({'detail': 'Corrija os campos assinalados.', 'errors': form.errors.get_json_data()}, status=400)
    curso = form.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CURSO_ACTUALIZADO', entidade='Curso', objeto_id=str(curso.pk), dados={'titulo': curso.titulo})
    return JsonResponse({'ok': True, 'curso': _react_course_form_payload(curso)})


def _react_gestor_turmas_queryset(centro, filial):
    turmas = Turma.objects.filter(curso__centro=centro).select_related('curso', 'instrutor_principal')
    return turmas.filter(curso__filiais=filial) if filial else turmas


def _react_turma_payload(turma):
    return {
        'id': turma.id, 'curso_id': turma.curso_id, 'curso_titulo': turma.curso.titulo,
        'nome': turma.nome, 'codigo': turma.codigo, 'data_inicio': turma.data_inicio.isoformat(),
        'data_fim': turma.data_fim.isoformat(), 'turno': turma.turno,
        'horario_inicio': turma.horario_inicio.strftime('%H:%M'),
        'horario_fim': turma.horario_fim.strftime('%H:%M'),
        'dias_semana': turma.dias_semana.split(','), 'vagas_totais': turma.vagas_totais,
        'vagas_ocupadas': turma.vagas_ocupadas, 'vagas_disponiveis': turma.vagas_disponiveis,
        'local': turma.local, 'sala': turma.sala, 'status': turma.status,
        'observacoes': turma.observacoes, 'instrutor_principal_id': turma.instrutor_principal_id,
        'instrutor_principal': turma.instrutor_principal.nome if turma.instrutor_principal else '',
    }


def _react_turma_choices():
    return {
        'turnos': [{'value': value, 'label': label} for value, label in Turma.TURNO_CHOICES],
        'status': [{'value': value, 'label': label} for value, label in Turma.STATUS_CHOICES],
        'dias_semana': [{'value': value, 'label': label} for value, label in Turma.DIAS_SEMANA_CHOICES],
    }


def _parse_react_turma_payload(payload, centro, filial, turma=None):
    """Normaliza o payload de turma e impede associações fora do contexto do gestor."""
    errors = {}
    curso = turma.curso if turma else None
    if not turma:
        try:
            curso = Curso.objects.get(id=int(payload.get('curso_id')), centro=centro, ativo=True)
            if filial and not curso.filiais.filter(pk=filial.pk).exists():
                raise Curso.DoesNotExist
        except (Curso.DoesNotExist, TypeError, ValueError):
            errors['curso_id'] = ['Selecione um curso activo permitido para este centro.']
    nome = str(payload.get('nome', turma.nome if turma else '')).strip()
    if len(nome) < 3:
        errors['nome'] = ['Indique um nome de turma com pelo menos 3 caracteres.']
    dias = payload.get('dias_semana', turma.dias_semana.split(',') if turma else [])
    if not isinstance(dias, list) or not dias or any(dia not in dict(Turma.DIAS_SEMANA_CHOICES) for dia in dias):
        errors['dias_semana'] = ['Selecione pelo menos um dia de semana válido.']
    turno = payload.get('turno', turma.turno if turma else '')
    if turno not in dict(Turma.TURNO_CHOICES):
        errors['turno'] = ['Selecione um turno válido.']
    status = payload.get('status', turma.status if turma else 'ABERTA')
    if status not in dict(Turma.STATUS_CHOICES):
        errors['status'] = ['Selecione um estado válido.']
    try:
        data_inicio = datetime.strptime(payload.get('data_inicio', turma.data_inicio.isoformat() if turma else ''), '%Y-%m-%d').date()
        data_fim = datetime.strptime(payload.get('data_fim', turma.data_fim.isoformat() if turma else ''), '%Y-%m-%d').date()
        if data_fim < data_inicio:
            errors['data_fim'] = ['A data de término não pode ser anterior à data de início.']
    except (TypeError, ValueError):
        errors['datas'] = ['Indique datas de início e término válidas.']
        data_inicio = data_fim = None
    try:
        horario_inicio = datetime.strptime(payload.get('horario_inicio', turma.horario_inicio.strftime('%H:%M') if turma else ''), '%H:%M').time()
        horario_fim = datetime.strptime(payload.get('horario_fim', turma.horario_fim.strftime('%H:%M') if turma else ''), '%H:%M').time()
        if horario_fim <= horario_inicio:
            errors['horario_fim'] = ['O horário final deve ser posterior ao horário inicial.']
    except (TypeError, ValueError):
        errors['horarios'] = ['Indique horários de início e término válidos.']
        horario_inicio = horario_fim = None
    try:
        vagas_totais = int(payload.get('vagas_totais', turma.vagas_totais if turma else 0))
        if vagas_totais < (turma.vagas_ocupadas if turma else 1):
            errors['vagas_totais'] = ['O total de vagas não pode ser inferior às vagas já ocupadas.']
    except (TypeError, ValueError):
        errors['vagas_totais'] = ['Indique um número válido de vagas.']
        vagas_totais = 0
    instrutor = None
    instrutor_id = payload.get('instrutor_principal_id', turma.instrutor_principal_id if turma else None)
    if instrutor_id:
        try:
            instrutor = Instrutor.objects.get(id=int(instrutor_id), centro_de_formacao=centro, ativo=True)
        except (Instrutor.DoesNotExist, TypeError, ValueError):
            errors['instrutor_principal_id'] = ['Selecione um formador activo deste centro.']
    if errors:
        return None, errors
    return {
        'curso': curso, 'nome': nome, 'data_inicio': data_inicio, 'data_fim': data_fim,
        'turno': turno, 'horario_inicio': horario_inicio, 'horario_fim': horario_fim,
        'dias_semana': ','.join(dias), 'vagas_totais': vagas_totais, 'status': status,
        'local': str(payload.get('local', turma.local if turma else '')).strip(),
        'sala': str(payload.get('sala', turma.sala if turma else '')).strip(),
        'observacoes': str(payload.get('observacoes', turma.observacoes if turma else '')).strip(),
        'instrutor_principal': instrutor,
    }, None


@login_required
@require_http_methods(['GET', 'POST'])
def react_gestor_classes(request):
    """Lista e cria turmas no contexto do centro ou filial do gestor autenticado."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if request.method == 'GET':
        cursos = filial.cursos_disponiveis.filter(ativo=True) if filial else centro.cursos.filter(ativo=True)
        return JsonResponse({
            'turmas': [_react_turma_payload(turma) for turma in _react_gestor_turmas_queryset(centro, filial).order_by('-data_inicio', 'nome')],
            'cursos': list(cursos.values('id', 'titulo').order_by('titulo')),
            'instrutores': list(Instrutor.objects.filter(centro_de_formacao=centro, ativo=True).values('id', 'nome').order_by('nome')),
            'escolhas': _react_turma_choices(),
        })
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    data, errors = _parse_react_turma_payload(payload, centro, filial)
    if errors:
        return JsonResponse({'detail': 'Corrija os campos assinalados.', 'errors': errors}, status=400)
    codigo = str(payload.get('codigo', '')).strip()
    if codigo and Turma.objects.filter(codigo=codigo).exists():
        return JsonResponse({'detail': 'Já existe uma turma com este código.', 'errors': {'codigo': ['Utilize um código único.']}}, status=400)
    turma = Turma.objects.create(**data, codigo=codigo, filial=filial)
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='TURMA_CRIADA', entidade='Turma', objeto_id=str(turma.pk), dados={'nome': turma.nome, 'curso_id': turma.curso_id})
    return JsonResponse({'ok': True, 'turma': _react_turma_payload(turma)}, status=201)


@login_required
@require_http_methods(['PATCH'])
def react_gestor_class_detail(request, turma_id):
    """Actualiza uma turma sem expor dados de outro centro ou filial."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    turma = get_object_or_404(_react_gestor_turmas_queryset(centro, filial), id=turma_id)
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    data, errors = _parse_react_turma_payload(payload, centro, filial, turma=turma)
    if errors:
        return JsonResponse({'detail': 'Corrija os campos assinalados.', 'errors': errors}, status=400)
    for field, value in data.items():
        setattr(turma, field, value)
    turma.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='TURMA_ACTUALIZADA', entidade='Turma', objeto_id=str(turma.pk), dados={'nome': turma.nome, 'curso_id': turma.curso_id})
    return JsonResponse({'ok': True, 'turma': _react_turma_payload(turma)})


def _react_gestor_turma(request, turma_id):
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return None, None, JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    turma = get_object_or_404(_react_gestor_turmas_queryset(centro, filial), id=turma_id)
    return centro, turma, None


def _react_turma_inscricoes(turma):
    return Inscricao.objects.filter(turma_escolhida=turma, status='A').select_related('aluno').order_by('aluno__nome')


@login_required
@require_http_methods(['GET', 'PUT'])
def react_gestor_class_attendance(request, turma_id):
    """Consulta ou guarda presenças da turma, impedindo alterações fora da lista de alunos confirmados."""
    centro, turma, response = _react_gestor_turma(request, turma_id)
    if response:
        return response
    if request.method == 'GET':
        data_str = request.GET.get('data')
        try:
            data_aula = datetime.strptime(data_str, '%Y-%m-%d').date() if data_str else timezone.localdate()
        except (TypeError, ValueError):
            return JsonResponse({'detail': 'Indique uma data válida no formato AAAA-MM-DD.'}, status=400)
        registos = {item.inscricao_id: item for item in Presenca.objects.filter(turma=turma, data=data_aula)}
        return JsonResponse({
            'turma': {'id': turma.id, 'nome': turma.nome, 'curso_titulo': turma.curso.titulo},
            'data': data_aula.isoformat(),
            'estados': [{'value': value, 'label': label} for value, label in Presenca.ESTADO_CHOICES],
            'alunos': [
                {'inscricao_id': inscricao.id, 'nome': inscricao.aluno.nome, 'estado': registos.get(inscricao.id).estado if inscricao.id in registos else 'PRESENTE', 'observacao': registos.get(inscricao.id).observacao if inscricao.id in registos else ''}
                for inscricao in _react_turma_inscricoes(turma)
            ],
        })
    try:
        payload = json.loads(request.body or '{}')
        data_aula = datetime.strptime(payload.get('data', ''), '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'Indique uma data válida no formato AAAA-MM-DD.'}, status=400)
    registos = payload.get('registos')
    if not isinstance(registos, list):
        return JsonResponse({'detail': 'Envie a lista de registos de presença.'}, status=400)
    inscricoes = {item.id: item for item in _react_turma_inscricoes(turma)}
    estados = dict(Presenca.ESTADO_CHOICES)
    for item in registos:
        try:
            inscricao_id = int(item.get('inscricao_id'))
        except (TypeError, ValueError):
            return JsonResponse({'detail': 'Foi encontrada uma inscrição inválida.'}, status=400)
        if inscricao_id not in inscricoes or item.get('estado') not in estados:
            return JsonResponse({'detail': 'Só pode registar presenças válidas dos alunos confirmados desta turma.'}, status=400)
        Presenca.objects.update_or_create(
            turma=turma, inscricao=inscricoes[inscricao_id], data=data_aula,
            defaults={'estado': item['estado'], 'observacao': str(item.get('observacao', '')).strip()[:255]},
        )
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='PRESENCAS_REGISTADAS', entidade='Turma', objeto_id=str(turma.pk), dados={'data': data_aula.isoformat(), 'total': len(registos)})
    return JsonResponse({'ok': True, 'data': data_aula.isoformat(), 'total': len(registos)})


@login_required
@require_http_methods(['GET', 'PUT'])
def react_gestor_class_grades(request, turma_id):
    """Consulta ou guarda notas entre 0 e 20 dos alunos confirmados da turma."""
    centro, turma, response = _react_gestor_turma(request, turma_id)
    if response:
        return response
    inscricoes = {item.id: item for item in _react_turma_inscricoes(turma)}
    if request.method == 'GET':
        notas = {item.inscricao_id: item for item in NotaAluno.objects.filter(turma=turma, avaliacao='Nota Final')}
        return JsonResponse({
            'turma': {'id': turma.id, 'nome': turma.nome, 'curso_titulo': turma.curso.titulo},
            'alunos': [
                {'inscricao_id': inscricao.id, 'nome': inscricao.aluno.nome, 'nota': str(notas[inscricao.id].nota) if inscricao.id in notas else '', 'observacao': notas[inscricao.id].observacao if inscricao.id in notas else ''}
                for inscricao in inscricoes.values()
            ],
        })
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    registos = payload.get('registos')
    if not isinstance(registos, list):
        return JsonResponse({'detail': 'Envie a lista de notas.'}, status=400)
    from decimal import Decimal, InvalidOperation
    for item in registos:
        try:
            inscricao_id = int(item.get('inscricao_id'))
            nota = Decimal(str(item.get('nota')).replace(',', '.'))
        except (TypeError, ValueError, InvalidOperation):
            return JsonResponse({'detail': 'Foi encontrada uma nota inválida.'}, status=400)
        if inscricao_id not in inscricoes or nota < 0 or nota > 20:
            return JsonResponse({'detail': 'As notas devem pertencer a alunos confirmados e estar entre 0 e 20.'}, status=400)
        NotaAluno.objects.update_or_create(
            turma=turma, inscricao=inscricoes[inscricao_id], avaliacao='Nota Final',
            defaults={'nota': nota, 'observacao': str(item.get('observacao', '')).strip()[:255]},
        )
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='NOTAS_REGISTADAS', entidade='Turma', objeto_id=str(turma.pk), dados={'total': len(registos)})
    return JsonResponse({'ok': True, 'total': len(registos)})


def _react_gestor_inscricoes_queryset(centro, filial):
    inscricoes = Inscricao.objects.filter(curso__centro=centro).select_related('aluno', 'curso', 'turma_escolhida')
    return inscricoes.filter(curso__filiais=filial) if filial else inscricoes


def _react_inscricao_payload(inscricao):
    return {
        'id': inscricao.id, 'codigo': inscricao.codigo_inscricao, 'aluno': inscricao.aluno.nome,
        'curso': inscricao.curso.titulo, 'curso_id': inscricao.curso_id,
        'turma': inscricao.turma_escolhida.nome if inscricao.turma_escolhida else 'Sem turma definida',
        'turma_id': inscricao.turma_escolhida_id, 'status': inscricao.status,
        'tipo': inscricao.tipo_inscricao, 'forma_pagamento': inscricao.forma_pagamento,
        'valor_pago': str(inscricao.valor_pago or 0), 'data_inscricao': inscricao.data_inscricao.isoformat(),
        'documento_enviado': bool(inscricao.documento_inscricao),
    }


@login_required
@require_http_methods(['GET'])
def react_gestor_enrollments(request):
    """Lista inscrições do centro e disponibiliza os totais usados pelo painel React."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    inscricoes = _react_gestor_inscricoes_queryset(centro, filial)
    status = request.GET.get('status', '').strip().upper()
    if status in dict(Inscricao.STATUS_CHOICES):
        inscricoes = inscricoes.filter(status=status)
    base = _react_gestor_inscricoes_queryset(centro, filial)
    return JsonResponse({
        'inscricoes': [_react_inscricao_payload(item) for item in inscricoes.order_by('-data_inscricao')[:100]],
        'metricas': {'total': base.count(), 'pendentes': base.filter(status='P').count(), 'aceites': base.filter(status='A').count(), 'negadas': base.filter(status='N').count()},
        'escolhas': {'status': [{'value': value, 'label': label} for value, label in Inscricao.STATUS_CHOICES]},
        'cursos': list((filial.cursos_disponiveis.filter(ativo=True) if filial else centro.cursos.filter(ativo=True)).values('id', 'titulo').order_by('titulo')),
        'turmas': [{'id': turma.id, 'curso_id': turma.curso_id, 'nome': turma.nome, 'vagas_disponiveis': turma.vagas_disponiveis} for turma in _react_gestor_turmas_queryset(centro, filial).filter(status__in=['ABERTA', 'EM_ANDAMENTO'], vagas_disponiveis__gt=0).order_by('data_inicio')],
        'formas_pagamento': [{'value': value, 'label': label} for value, label in Inscricao.FORMA_PAGAMENTO_CHOICES],
        'origens_matricula': [{'value': value, 'label': label} for value, label in Matricula.ORIGEM_CHOICES],
        'permissoes': {'inscricao_manual': permite(centro, 'permite_inscricao_manual', permitir_periodo_teste=True)},
    })


@login_required
@require_http_methods(['PATCH'])
def react_gestor_enrollment_detail(request, inscricao_id):
    """Actualiza apenas o estado de uma inscrição pertencente ao centro ou filial do gestor."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    inscricao = get_object_or_404(_react_gestor_inscricoes_queryset(centro, filial), id=inscricao_id)
    try:
        payload = json.loads(request.body or '{}')
        status = str(payload.get('status', '')).upper()
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    if status not in dict(Inscricao.STATUS_CHOICES):
        return JsonResponse({'detail': 'Indique um estado de inscrição válido.'}, status=400)
    if status == 'A' and inscricao.turma_escolhida and inscricao.turma_escolhida.vagas_disponiveis <= 0 and inscricao.status != 'A':
        return JsonResponse({'detail': 'A turma escolhida já não possui vagas disponíveis.'}, status=400)
    estado_anterior = inscricao.status
    inscricao.status = status
    inscricao.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='INSCRICAO_ACTUALIZADA', entidade='Inscricao', objeto_id=str(inscricao.pk), dados={'anterior': estado_anterior, 'estado': status})
    return JsonResponse({'ok': True, 'inscricao': _react_inscricao_payload(inscricao)})


@login_required
@require_http_methods(['POST'])
def react_gestor_manual_enrollment(request):
    """Cria matrícula presencial com inscrição, parcela e recebimento no mesmo fluxo transaccional."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if not permite(centro, 'permite_inscricao_manual', permitir_periodo_teste=True):
        return JsonResponse({'detail': 'O plano actual não permite inscrições manuais.'}, status=403)
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    nome, email = str(payload.get('nome', '')).strip(), str(payload.get('email', '')).strip().lower()
    if len(nome) < 3 or '@' not in email:
        return JsonResponse({'detail': 'Nome completo e e-mail válido são obrigatórios.'}, status=400)
    try:
        curso = Curso.objects.get(id=int(payload.get('curso_id')), centro=centro, ativo=True)
        turma = Turma.objects.get(id=int(payload.get('turma_id')), curso=curso)
        if filial and not curso.filiais.filter(pk=filial.pk).exists():
            raise Turma.DoesNotExist
    except (Curso.DoesNotExist, Turma.DoesNotExist, TypeError, ValueError):
        return JsonResponse({'detail': 'Selecione um curso e uma turma válidos deste centro.'}, status=400)
    if turma.status in {'CONCLUIDA', 'CANCELADA'} or turma.vagas_disponiveis <= 0:
        return JsonResponse({'detail': 'A turma selecionada não está disponível para novas matrículas.'}, status=400)
    from decimal import Decimal, InvalidOperation
    try:
        valor = Decimal(str(payload.get('valor_acordado', curso.preco_atual or 0)).replace(',', '.'))
        desconto = Decimal(str(payload.get('desconto', 0)).replace(',', '.'))
        if valor < 0 or desconto < 0 or desconto > valor:
            raise InvalidOperation
    except (InvalidOperation, ValueError, TypeError):
        return JsonResponse({'detail': 'Indique valores válidos para a matrícula e o desconto.'}, status=400)
    pago = bool(payload.get('pagamento_confirmado'))
    forma, origem = str(payload.get('forma_pagamento', 'DINHEIRO')), str(payload.get('origem', 'PRESENCIAL'))
    if forma not in dict(Inscricao.FORMA_PAGAMENTO_CHOICES):
        return JsonResponse({'detail': 'Selecione uma forma de pagamento válida.'}, status=400)
    try:
        from django.contrib.auth import get_user_model
        from django.db import transaction
        with transaction.atomic():
            User = get_user_model()
            user, _ = User.objects.get_or_create(email=email, defaults={'nome': nome, 'is_active': False, 'tipo_usuario': 'ALUNO'})
            aluno, _ = Aluno.objects.get_or_create(usuario=user, defaults={'nome': nome})
            if Matricula.objects.filter(aluno=aluno, turma=turma, estado__in=['PENDENTE', 'ATIVA', 'SUSPENSA']).exists():
                raise ValueError('Este aluno já possui uma matrícula activa ou pendente nesta turma.')
            inscricao, _ = Inscricao.objects.get_or_create(aluno=aluno, curso=curso, defaults={'status': 'A' if pago else 'P', 'tipo_inscricao': 'PRESENCIAL', 'turma_escolhida': turma, 'forma_pagamento': forma, 'valor_pago': valor if pago else 0, 'data_pagamento': timezone.now() if pago else None, 'observacoes': 'Registo presencial no GestorEduka React'})
            inscricao.turma_escolhida, inscricao.tipo_inscricao, inscricao.forma_pagamento = turma, 'PRESENCIAL', forma
            inscricao.valor_pago, inscricao.status = (valor if pago else (inscricao.valor_pago or 0)), ('A' if pago else 'P')
            if pago and not inscricao.data_pagamento:
                inscricao.data_pagamento = timezone.now()
            inscricao.save()
            matricula = Matricula.objects.create(aluno=aluno, curso=curso, turma=turma, inscricao=inscricao, origem=origem if origem in dict(Matricula.ORIGEM_CHOICES) else 'PRESENCIAL', estado='ATIVA' if pago else 'PENDENTE', valor_acordado=valor, desconto=desconto, responsavel=request.user, observacoes='Matrícula criada presencialmente pelo GestorEduka React.')
            parcela = ParcelaMatricula.objects.create(matricula=matricula, numero=1, descricao='Pagamento inicial da matrícula', valor=max(valor - desconto, 0), vencimento=timezone.localdate(), status='PAGA' if pago else 'PENDENTE', valor_pago=max(valor - desconto, 0) if pago else 0, data_pagamento=timezone.now() if pago else None)
            if pago:
                recebimento = RecebimentoCentro.objects.create(centro=centro, matricula=matricula, aluno=aluno, valor=max(valor - desconto, 0), forma=forma if forma in dict(RecebimentoCentro.FORMA_CHOICES) else 'OUTRO', recebido_por=request.user, observacoes='Recebimento presencial registado pelo GestorEduka React.')
                parcela.recebimento = recebimento
                parcela.save(update_fields=['recebimento'])
                turma.atualizar_vagas_turma()
            AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CRIAR_MATRICULA', entidade='Matricula', objeto_id=str(matricula.pk), dados={'origem': matricula.origem, 'pagamento': pago})
    except Exception as exc:
        return JsonResponse({'detail': f'Não foi possível criar a matrícula presencial: {exc}'}, status=400)
    return JsonResponse({'ok': True, 'matricula': {'id': matricula.id, 'codigo': matricula.codigo_matricula}, 'inscricao': _react_inscricao_payload(inscricao)}, status=201)


def _react_gestor_instructors_queryset(centro, filial):
    instrutores = Instrutor.objects.filter(centro_de_formacao=centro)
    return instrutores.filter(filial=filial) if filial else instrutores


def _react_instructor_payload(instrutor):
    return {
        'id': instrutor.id, 'nome': instrutor.nome, 'email': instrutor.email,
        'titulo': instrutor.titulo or '', 'biografia': instrutor.biografia,
        'area_especializacao': instrutor.area_especializacao, 'ativo': instrutor.ativo,
        'filial_id': instrutor.filial_id,
    }


def _validate_react_instructor(payload, centro, filial, instance=None):
    nome = str(payload.get('nome', instance.nome if instance else '')).strip()
    email = str(payload.get('email', instance.email if instance else '')).strip().lower()
    biografia = str(payload.get('biografia', instance.biografia if instance else '')).strip()
    area = str(payload.get('area_especializacao', instance.area_especializacao if instance else ''))
    if len(nome) < 3 or '@' not in email or len(biografia) < 10 or area not in dict(Instrutor.TIPO_CHOICES_ESPECIALIZACAO):
        return None, {'detail': 'Preencha nome, e-mail, biografia e área de especialização com valores válidos.'}
    emails = Instrutor.objects.filter(email__iexact=email)
    if instance:
        emails = emails.exclude(pk=instance.pk)
    if emails.exists():
        return None, {'detail': 'Já existe um formador com este e-mail.'}
    return {'nome': nome, 'email': email, 'biografia': biografia, 'area_especializacao': area, 'titulo': str(payload.get('titulo', instance.titulo if instance else '')).strip() or None, 'ativo': bool(payload.get('ativo', instance.ativo if instance else True)), 'centro_de_formacao': centro, 'filial': filial}, None


@login_required
@require_http_methods(['GET', 'POST'])
def react_gestor_instructors(request):
    """Lista e cria formadores no escopo de centro ou filial da sessão."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if request.method == 'GET':
        return JsonResponse({'instrutores': [_react_instructor_payload(item) for item in _react_gestor_instructors_queryset(centro, filial).order_by('nome')], 'areas': [{'value': value, 'label': label} for value, label in Instrutor.TIPO_CHOICES_ESPECIALIZACAO]})
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    values, error = _validate_react_instructor(payload, centro, filial)
    if error:
        return JsonResponse(error, status=400)
    instrutor = Instrutor.objects.create(**values)
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='FORMADOR_CRIADO', entidade='Instrutor', objeto_id=str(instrutor.pk), dados={'nome': instrutor.nome})
    return JsonResponse({'ok': True, 'instrutor': _react_instructor_payload(instrutor)}, status=201)


@login_required
@require_http_methods(['PATCH'])
def react_gestor_instructor_detail(request, instrutor_id):
    """Actualiza dados de um formador permitido pelo escopo da sessão."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    instrutor = get_object_or_404(_react_gestor_instructors_queryset(centro, filial), id=instrutor_id)
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    values, error = _validate_react_instructor(payload, centro, filial, instance=instrutor)
    if error:
        return JsonResponse(error, status=400)
    for field, value in values.items():
        setattr(instrutor, field, value)
    instrutor.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='FORMADOR_ACTUALIZADO', entidade='Instrutor', objeto_id=str(instrutor.pk), dados={'nome': instrutor.nome, 'ativo': instrutor.ativo})
    return JsonResponse({'ok': True, 'instrutor': _react_instructor_payload(instrutor)})


def _react_branch_payload(filial):
    return {'id': filial.id, 'nome': filial.nome, 'endereco': filial.endereco, 'telefone': filial.telefone, 'email': filial.email, 'whatsapp': filial.whatsapp or '', 'latitude': str(filial.latitude or ''), 'longitude': str(filial.longitude or ''), 'ativo': filial.ativo, 'gestor_email': filial.usuario.email if filial.usuario else ''}


def _validate_react_branch(payload, instance=None):
    nome = str(payload.get('nome', instance.nome if instance else '')).strip()
    endereco = str(payload.get('endereco', instance.endereco if instance else '')).strip()
    telefone = str(payload.get('telefone', instance.telefone if instance else '')).strip()
    email = str(payload.get('email', instance.email if instance else '')).strip().lower()
    if len(nome) < 3 or not endereco or not telefone or '@' not in email:
        return None, 'Preencha nome, endereço, telefone e e-mail da filial com valores válidos.'
    try:
        latitude = float(payload['latitude']) if payload.get('latitude') not in (None, '') else None
        longitude = float(payload['longitude']) if payload.get('longitude') not in (None, '') else None
    except (TypeError, ValueError):
        return None, 'As coordenadas da filial devem ser numéricas.'
    return {'nome': nome, 'endereco': endereco, 'telefone': telefone, 'email': email, 'whatsapp': str(payload.get('whatsapp', instance.whatsapp if instance else '')).strip() or None, 'latitude': latitude, 'longitude': longitude, 'ativo': bool(payload.get('ativo', instance.ativo if instance else True))}, None


@login_required
@require_http_methods(['GET', 'POST'])
def react_gestor_branches(request):
    """Lista e cria filiais; apenas o gestor principal pode executar estas operações."""
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:
        return JsonResponse({'detail': 'A gestão de filiais é reservada ao gestor principal do centro.'}, status=403)
    if request.method == 'GET':
        return JsonResponse({'filiais': [_react_branch_payload(item) for item in centro.filiais.select_related('usuario').order_by('nome')]})
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    values, error = _validate_react_branch(payload)
    password = str(payload.get('senha', ''))
    if error or len(password) < 8:
        return JsonResponse({'detail': error or 'A palavra-passe inicial do gestor da filial deve ter pelo menos 8 caracteres.'}, status=400)
    if Filial.objects.filter(email__iexact=values['email']).exists():
        return JsonResponse({'detail': 'Já existe uma filial com este e-mail.'}, status=400)
    from usuarios.models import Usuario
    if Usuario.objects.filter(email__iexact=values['email']).exists():
        return JsonResponse({'detail': 'Já existe uma conta com este e-mail.'}, status=400)
    try:
        from django.db import transaction
        with transaction.atomic():
            utilizador = Usuario.objects.create_user(email=values['email'], password=password, nome=f"Gestor - {values['nome']}", tipo_usuario='GESTOR_FILIAL')
            branch = Filial.objects.create(centro_principal=centro, usuario=utilizador, **values)
            branch.categorias.set(centro.categorias.all())
    except Exception as exc:
        return JsonResponse({'detail': f'Não foi possível criar a filial: {exc}'}, status=400)
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='FILIAL_CRIADA', entidade='Filial', objeto_id=str(branch.pk), dados={'nome': branch.nome})
    return JsonResponse({'ok': True, 'filial': _react_branch_payload(branch)}, status=201)


@login_required
@require_http_methods(['PATCH', 'DELETE'])
def react_gestor_branch_detail(request, filial_id):
    """Actualiza ou remove uma filial pertencente ao centro principal autenticado."""
    centro, filial = get_gestor_context(request.user)
    if not centro or filial:
        return JsonResponse({'detail': 'A gestão de filiais é reservada ao gestor principal do centro.'}, status=403)
    branch = get_object_or_404(Filial.objects.select_related('usuario'), id=filial_id, centro_principal=centro)
    if request.method == 'DELETE':
        usuario = branch.usuario
        branch.delete()
        if usuario:
            usuario.delete()
        AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='FILIAL_REMOVIDA', entidade='Filial', objeto_id=str(filial_id), dados={})
        return JsonResponse({'ok': True, 'filial_id': filial_id})
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    values, error = _validate_react_branch(payload, instance=branch)
    if error:
        return JsonResponse({'detail': error}, status=400)
    if Filial.objects.exclude(pk=branch.pk).filter(email__iexact=values['email']).exists():
        return JsonResponse({'detail': 'Já existe outra filial com este e-mail.'}, status=400)
    for field, value in values.items():
        setattr(branch, field, value)
    password = str(payload.get('senha', ''))
    if password and branch.usuario:
        if len(password) < 8:
            return JsonResponse({'detail': 'A nova palavra-passe deve ter pelo menos 8 caracteres.'}, status=400)
        branch.usuario.set_password(password)
        branch.usuario.save(update_fields=['password'])
    branch.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='FILIAL_ACTUALIZADA', entidade='Filial', objeto_id=str(branch.pk), dados={'nome': branch.nome, 'ativa': branch.ativo})
    return JsonResponse({'ok': True, 'filial': _react_branch_payload(branch)})


def _react_event_payload(evento):
    return {'id': evento.id, 'titulo': evento.titulo, 'descricao': evento.descricao, 'data_inicio': evento.data_inicio.isoformat(), 'data_fim': evento.data_fim.isoformat() if evento.data_fim else '', 'local': evento.local, 'tipo': evento.tipo, 'link_inscricao': evento.link_inscricao or '', 'destaque': evento.destaque}


def _react_event_values(payload, instance=None):
    titulo = str(payload.get('titulo', instance.titulo if instance else '')).strip()
    descricao = str(payload.get('descricao', instance.descricao if instance else '')).strip()
    local = str(payload.get('local', instance.local if instance else '')).strip()
    tipo = str(payload.get('tipo', instance.tipo if instance else ''))
    try:
        data_inicio = datetime.fromisoformat(str(payload.get('data_inicio', instance.data_inicio.isoformat() if instance else '')).replace('Z', '+00:00'))
        data_fim_raw = payload.get('data_fim', instance.data_fim.isoformat() if instance and instance.data_fim else '')
        data_fim = datetime.fromisoformat(str(data_fim_raw).replace('Z', '+00:00')) if data_fim_raw else None
    except (TypeError, ValueError):
        return None, 'Indique datas de início e fim válidas.'
    if len(titulo) < 3 or len(descricao) < 10 or not local or tipo not in dict(Evento._meta.get_field('tipo').choices) or (data_fim and data_fim < data_inicio):
        return None, 'Preencha título, descrição, local, tipo e datas válidos.'
    return {'titulo': titulo, 'descricao': descricao, 'local': local, 'tipo': tipo, 'data_inicio': data_inicio, 'data_fim': data_fim, 'link_inscricao': str(payload.get('link_inscricao', instance.link_inscricao if instance else '')).strip(), 'destaque': bool(payload.get('destaque', instance.destaque if instance else False))}, None


@login_required
@require_http_methods(['GET', 'POST'])
def react_gestor_events(request):
    """Lista e cria eventos associados ao centro do gestor autenticado."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if request.method == 'GET':
        return JsonResponse({'eventos': [_react_event_payload(evento) for evento in centro.eventos.all().order_by('-data_inicio')], 'tipos': [{'value': value, 'label': label} for value, label in Evento._meta.get_field('tipo').choices]})
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    values, error = _react_event_values(payload)
    if error:
        return JsonResponse({'detail': error}, status=400)
    evento = Evento.objects.create(centro=centro, **values)
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='EVENTO_CRIADO', entidade='Evento', objeto_id=str(evento.pk), dados={'titulo': evento.titulo})
    return JsonResponse({'ok': True, 'evento': _react_event_payload(evento)}, status=201)


@login_required
@require_http_methods(['PATCH', 'DELETE'])
def react_gestor_event_detail(request, evento_id):
    """Actualiza ou remove um evento pertencente ao centro do gestor autenticado."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    evento = get_object_or_404(Evento, id=evento_id, centro=centro)
    if request.method == 'DELETE':
        titulo = evento.titulo
        evento.delete()
        AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='EVENTO_REMOVIDO', entidade='Evento', objeto_id=str(evento_id), dados={'titulo': titulo})
        return JsonResponse({'ok': True, 'evento_id': evento_id})
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    values, error = _react_event_values(payload, instance=evento)
    if error:
        return JsonResponse({'detail': error}, status=400)
    for field, value in values.items():
        setattr(evento, field, value)
    evento.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='EVENTO_ACTUALIZADO', entidade='Evento', objeto_id=str(evento.pk), dados={'titulo': evento.titulo})
    return JsonResponse({'ok': True, 'evento': _react_event_payload(evento)})


def _react_media_url(field):
    try:
        return field.url if field else ''
    except (ValueError, AttributeError):
        return ''


def _react_profile_payload(centro, perfil):
    return {
        'centro': {
            'nome': centro.nome or '', 'email': centro.email or '', 'telefone': centro.telefone or '',
            'site': centro.site or '', 'pais': centro.pais, 'endereco': centro.endereco or '',
            'cidade': centro.cidade or '', 'provincia': centro.provincia or '',
        },
        'perfil': {
            'descricao': perfil.descricao or '', 'missao': perfil.missao or '', 'visao': perfil.visao or '',
            'valores': perfil.valores or '', 'ano_fundacao': perfil.ano_fundacao or '',
            'horario_funcionamento': perfil.horario_funcionamento or '', 'tipo': perfil.tipo or '',
            'modalidade': perfil.modalidade, 'facebook': perfil.facebook or '', 'instagram': perfil.instagram or '',
            'linkedin': perfil.linkedin or '', 'youtube': perfil.youtube or '', 'tiktok': perfil.tiktok or '',
            'whatsapp': perfil.whatsapp or '', 'imagem_url': _react_media_url(perfil.imagem), 'banner_url': _react_media_url(perfil.banner),
        },
        'galeria': [{'id': imagem.id, 'titulo': imagem.titulo or '', 'url': _react_media_url(imagem.imagem), 'ordem': imagem.ordem} for imagem in centro.galeria_imagens.all().order_by('ordem', 'id')],
    }


@login_required
@require_http_methods(['GET', 'PATCH'])
def react_gestor_profile(request):
    """Consulta e actualiza os dados institucionais públicos do centro principal."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if filial:
        return JsonResponse({'detail': 'A edição do perfil institucional é reservada ao gestor principal do centro.'}, status=403)
    perfil, _ = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
    if request.method == 'GET':
        return JsonResponse(_react_profile_payload(centro, perfil))
    try:
        payload = json.loads(request.body or '{}')
    except (TypeError, ValueError):
        return JsonResponse({'detail': 'O pedido deve conter dados JSON válidos.'}, status=400)
    dados_centro = payload.get('centro', {})
    dados_perfil = payload.get('perfil', {})
    if not isinstance(dados_centro, dict) or not isinstance(dados_perfil, dict):
        return JsonResponse({'detail': 'Os dados do centro e do perfil devem ser objectos válidos.'}, status=400)
    nome = str(dados_centro.get('nome', centro.nome or '')).strip()
    email = str(dados_centro.get('email', centro.email or '')).strip().lower()
    if len(nome) < 3 or '@' not in email:
        return JsonResponse({'detail': 'Indique um nome de centro e e-mail institucionais válidos.'}, status=400)
    if CentroDeFormacao.objects.exclude(pk=centro.pk).filter(email__iexact=email).exists():
        return JsonResponse({'detail': 'Já existe outro centro com este e-mail institucional.'}, status=400)
    for field in ['nome', 'email', 'telefone', 'site', 'pais', 'endereco', 'cidade', 'provincia']:
        if field in dados_centro:
            setattr(centro, field, str(dados_centro[field]).strip() or None)
    if centro.pais not in dict(CentroDeFormacao.PAIS_CHOICES):
        return JsonResponse({'detail': 'Selecione um país válido.'}, status=400)
    for field in ['descricao', 'missao', 'visao', 'valores', 'horario_funcionamento', 'tipo', 'facebook', 'instagram', 'linkedin', 'youtube', 'tiktok', 'whatsapp']:
        if field in dados_perfil:
            setattr(perfil, field, str(dados_perfil[field]).strip() or None)
    if 'ano_fundacao' in dados_perfil:
        try:
            perfil.ano_fundacao = int(dados_perfil['ano_fundacao']) if dados_perfil['ano_fundacao'] else None
        except (TypeError, ValueError):
            return JsonResponse({'detail': 'Indique um ano de fundação válido.'}, status=400)
    if 'modalidade' in dados_perfil:
        modalidade = str(dados_perfil['modalidade'])
        if modalidade not in {'Presencial', 'Online', 'Híbrido'}:
            return JsonResponse({'detail': 'Selecione uma modalidade institucional válida.'}, status=400)
        perfil.modalidade = modalidade
    centro.save()
    perfil.save()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='PERFIL_INSTITUCIONAL_ACTUALIZADO', entidade='CentroDeFormacao', objeto_id=str(centro.pk), dados={'nome': centro.nome})
    return JsonResponse({'ok': True, **_react_profile_payload(centro, perfil)})


@login_required
@require_http_methods(['POST'])
def react_gestor_profile_media(request):
    """Recebe exclusivamente a imagem de identidade ou o banner público do centro principal."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if filial:
        return JsonResponse({'detail': 'A edição do perfil institucional é reservada ao gestor principal do centro.'}, status=403)
    campo = request.POST.get('campo')
    ficheiro = request.FILES.get('ficheiro')
    if campo not in {'imagem', 'banner'} or not ficheiro:
        return JsonResponse({'detail': 'Indique um tipo de imagem permitido e selecione um ficheiro.'}, status=400)
    if not str(ficheiro.content_type or '').startswith('image/') or ficheiro.size > 5 * 1024 * 1024:
        return JsonResponse({'detail': 'Envie uma imagem com até 5 MB.'}, status=400)
    perfil, _ = PerfilCentroDeFormacao.objects.get_or_create(centro=centro)
    setattr(perfil, campo, ficheiro)
    perfil.save(update_fields=[campo])
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='PERFIL_MEDIA_ACTUALIZADA', entidade='PerfilCentroDeFormacao', objeto_id=str(perfil.pk), dados={'campo': campo})
    return JsonResponse({'ok': True, 'campo': campo, 'url': _react_media_url(getattr(perfil, campo))})


@login_required
@require_http_methods(['POST'])
def react_gestor_profile_gallery(request):
    """Adiciona uma imagem à galeria pública do centro principal com validação de ficheiro e categoria."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if filial:
        return JsonResponse({'detail': 'A edição da galeria institucional é reservada ao gestor principal do centro.'}, status=403)
    ficheiro = request.FILES.get('imagem')
    categoria = request.POST.get('categoria', 'OUTRO')
    if not ficheiro or categoria not in {'SALAS', 'LABS', 'EVENTOS', 'OUTRO'}:
        return JsonResponse({'detail': 'Selecione uma imagem e uma categoria válidas.'}, status=400)
    if not str(ficheiro.content_type or '').startswith('image/') or ficheiro.size > 5 * 1024 * 1024:
        return JsonResponse({'detail': 'Envie uma imagem com até 5 MB.'}, status=400)
    imagem = GaleriaImagem.objects.create(
        centro=centro, imagem=ficheiro, categoria=categoria,
        titulo=request.POST.get('titulo', '').strip()[:100],
        descricao=request.POST.get('descricao', '').strip() or None,
        ordem=centro.galeria_imagens.count(),
    )
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='GALERIA_IMAGEM_ADICIONADA', entidade='GaleriaImagem', objeto_id=str(imagem.pk), dados={'categoria': categoria})
    return JsonResponse({'ok': True, 'imagem': {'id': imagem.id, 'titulo': imagem.titulo or '', 'url': _react_media_url(imagem.imagem), 'ordem': imagem.ordem}}, status=201)


@login_required
@require_http_methods(['DELETE'])
def react_gestor_profile_gallery_detail(request, imagem_id):
    """Remove uma imagem de galeria pertencente ao centro principal autenticado."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if filial:
        return JsonResponse({'detail': 'A edição da galeria institucional é reservada ao gestor principal do centro.'}, status=403)
    imagem = get_object_or_404(GaleriaImagem, id=imagem_id, centro=centro)
    imagem.delete()
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='GALERIA_IMAGEM_REMOVIDA', entidade='GaleriaImagem', objeto_id=str(imagem_id), dados={})
    return JsonResponse({'ok': True, 'imagem_id': imagem_id})


@login_required
@require_http_methods(['POST'])
def react_gestor_enrollment_certificate(request, inscricao_id):
    """Emite certificado presencial apenas quando os critérios académicos mínimos estiverem cumpridos."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if not permite(centro, 'permite_gerar_certificado', permitir_periodo_teste=True):
        return JsonResponse({'detail': 'O plano actual não permite a emissão de certificados.'}, status=403)
    inscricao = get_object_or_404(_react_gestor_inscricoes_queryset(centro, filial).filter(status='A'), id=inscricao_id)
    if not inscricao.turma_escolhida:
        return JsonResponse({'detail': 'O aluno deve estar associado a uma turma antes de receber certificado.'}, status=400)
    presencas = Presenca.objects.filter(turma=inscricao.turma_escolhida, inscricao=inscricao)
    total = presencas.count()
    percentagem = (presencas.filter(estado__in=['PRESENTE', 'ATRASO']).count() / total * 100) if total else 0
    if total == 0 or percentagem < 75:
        return JsonResponse({'detail': f'Certificado bloqueado: a assiduidade actual é de {percentagem:.0f}% e o mínimo exigido é 75%.'}, status=400)
    nota_final = NotaAluno.objects.filter(turma=inscricao.turma_escolhida, inscricao=inscricao, avaliacao='Nota Final').first()
    if not nota_final or nota_final.nota < 10:
        nota = str(nota_final.nota) if nota_final else 'não registada'
        return JsonResponse({'detail': f'Certificado bloqueado: a nota final é {nota}; o mínimo exigido é 10 valores.'}, status=400)
    from cursos_app.models import CertificadoCurso
    certificado, criado = CertificadoCurso.objects.get_or_create(inscricao=inscricao)
    AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CERTIFICADO_EMITIDO' if criado else 'CERTIFICADO_CONFIRMADO', entidade='CertificadoCurso', objeto_id=str(certificado.pk), dados={'inscricao_id': inscricao.pk})
    return JsonResponse({'ok': True, 'criado': criado, 'certificado': {'id': str(certificado.id), 'codigo_verificacao': certificado.codigo_verificacao}})


@login_required
@require_http_methods(['GET', 'POST'])
def react_gestor_courses(request):
    """Lista os metadados necessários ao formulário React e cria cursos no centro da sessão."""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return JsonResponse({'detail': 'Esta conta não possui um centro de formação associado.'}, status=403)
    if request.method == 'POST':
        if filial:
            return JsonResponse({'detail': 'A criação de cursos deve ser realizada pelo gestor principal do centro.'}, status=403)
        form = CursoForm(request.POST, request.FILES, centro=centro)
        if not form.is_valid():
            return JsonResponse({'detail': 'Corrija os campos assinalados.', 'errors': form.errors.get_json_data()}, status=400)
        curso = form.save(commit=False)
        curso.centro = centro
        curso.save()
        form.save_m2m()
        AuditoriaCentro.objects.create(centro=centro, utilizador=request.user, acao='CURSO_CRIADO', entidade='Curso', objeto_id=str(curso.pk), dados={'titulo': curso.titulo})
        return JsonResponse({'ok': True, 'curso': {'id': curso.id, 'titulo': curso.titulo, 'publicado': curso.publicado}}, status=201)
    form = CursoForm(centro=centro)
    def choices(name):
        return [{'value': value, 'label': label} for value, label in form.fields[name].choices if value not in (None, '')]
    return JsonResponse({
        'categorias': list(Categoria.objects.values('id', 'nome').order_by('nome')),
        'instrutores': list(Instrutor.objects.filter(centro_de_formacao=centro, ativo=True).values('id', 'nome').order_by('nome')),
        'escolhas': {nome: choices(nome) for nome in ['nivel', 'idioma', 'duracao', 'moeda', 'modalidade', 'tipo_cobranca_inscricao', 'documento_requerido']},
    })
