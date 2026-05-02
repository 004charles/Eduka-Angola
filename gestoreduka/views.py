import re
import os
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
    CategoriaCentro, AnuncioCentro
)
from cursos_app.models import Curso, Categoria, Instrutor, Inscricao, Turma
from planos.models import AssinaturaMembro, Plano
from usuarios.models import Aluno
from usuarios.decorators import aluno_logado_e_centros
from .forms import CursoForm, AnuncioForm

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
        
    # Estatísticas Gerais (Filtrar por filial se aplicável)
    cursos_qs = filial.cursos.all() if filial else centro.cursos.all()
    total_cursos = cursos_qs.count()
    
    inscricoes_qs = Inscricao.objects.filter(curso__centro=centro)
    if filial:
        inscricoes_qs = inscricoes_qs.filter(curso__filial=filial)
        
    total_inscricoes = inscricoes_qs.count()
    inscricoes_pendentes = inscricoes_qs.filter(status='P').count()
    
    # Receita Real (baseada em pagamentos confirmados)
    receita_total = inscricoes_qs.filter(
        status='A'
    ).aggregate(total=Sum('valor_pago'))['total'] or 0
    
    # Meta de cursos (exemplo baseado no plano)
    assinatura = getattr(centro, 'assinatura', None)
    limite_cursos = assinatura.plano.limite_cursos if assinatura and assinatura.plano else 5
    
    # Cursos Populares
    cursos_populares = cursos_qs.annotate(
        num_alunos=Count('inscricoes', filter=Q(inscricoes__status='A'))
    ).order_by('-num_alunos')[:4]
    
    # Inscrições Recentes
    recent_enrollments = inscricoes_qs.select_related('aluno', 'curso').order_by('-data_inscricao')[:6]
    
    context = {
        'centro': centro,
        'filial': filial,
        'is_filial': filial is not None,
        'stats': {
            'total_cursos': total_cursos,
            'total_inscricoes': total_inscricoes,
            'inscricoes_pendentes': inscricoes_pendentes,
            'receita_total': receita_total,
            'limite_cursos': limite_cursos,
            'percentual_cursos': (total_cursos / limite_cursos * 100) if limite_cursos > 0 else 0,
            'total_seguidores': centro.seguidores.count()
        },
        'cursos_populares': cursos_populares,
        'recent_enrollments': recent_enrollments,
        'assinatura': assinatura
    }
    
    return render(request, 'centro_dashboard.html', context)

def gerenciar_inscricoes(request):
    """
    View para o gestor gerenciar todas as inscrições do centro ou filial.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    inscricoes_qs = Inscricao.objects.filter(curso__centro=centro)
    if filial:
        inscricoes_qs = inscricoes_qs.filter(curso__filial=filial)
        
    inscricoes_list = inscricoes_qs.select_related('aluno', 'curso', 'turma_escolhida').order_by('-data_inscricao')
    
    # Filtros
    status = request.GET.get('status')
    if status:
        inscricoes_list = inscricoes_list.filter(status=status)
    
    paginator = Paginator(inscricoes_list, 15)
    page_number = request.GET.get('page')
    inscricoes = paginator.get_page(page_number)
    
    return render(request, 'gestor/inscricoes.html', {
        'centro': centro,
        'filial': filial,
        'inscricoes': inscricoes,
        'selected_status': status
    })

def gerenciar_assinatura(request):
    """
    View de monetização: Gestor vê seu plano e pode assinar ou mudar.
    Para filiais, isso geralmente não se aplica, mas será mantido para visualização.
    """
    if not request.user.is_authenticated:
        return redirect('login_gestor')
    
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    assinatura = getattr(centro, 'assinatura', None)
    planos_disponiveis = Plano.objects.filter(ativo=True).exclude(id=assinatura.plano.id if assinatura and assinatura.plano else None)
    
    return render(request, 'gestor/assinatura.html', {
        'centro': centro,
        'filial': filial,
        'assinatura': assinatura,
        'planos_disponiveis': planos_disponiveis
    })

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
        inscricoes_qs = inscricoes_qs.filter(curso__filial=filial)
        cursos_qs = filial.cursos.all()
    
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
        turmas_qs = turmas_qs.filter(curso__filial=filial)
        
    turmas = turmas_qs.select_related('curso', 'instrutor_principal').order_by('-data_inicio')
    
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
        
    cursos_context = filial.cursos.filter(ativo=True) if filial else centro.cursos.filter(ativo=True)
    instrutores_context = filial.instrutores.filter(ativo=True) if filial else centro.instrutores.filter(ativo=True)
    
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
        instrutor_id = request.POST.get('instrutor_principal')
        
        try:
            curso = get_object_or_404(Curso, id=curso_id, centro=centro)
            if filial and curso.filial != filial:
                raise Exception("Curso não pertence à sua filial.")
                
            instrutor = Instrutor.objects.get(id=instrutor_id) if instrutor_id else None
            
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
                vagas_totais=int(vagas_totais),
                instrutor_principal=instrutor
            )
            
            messages.success(request, f'Turma "{turma.nome}" criada com sucesso!')
            return redirect('gerenciar_turmas')
        except Exception as e:
            messages.error(request, f'Erro ao criar turma: {str(e)}')
    
    return render(request, 'gestor/turmas/form.html', {
        'centro': centro,
        'filial': filial,
        'cursos': cursos_context,
        'instrutores': instrutores_context,
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
    if filial and turma.curso.filial != filial:
        messages.error(request, "Permissão negada.")
        return redirect('gerenciar_turmas')
        
    cursos_context = filial.cursos.filter(ativo=True) if filial else centro.cursos.filter(ativo=True)
    instrutores_context = filial.instrutores.filter(ativo=True) if filial else centro.instrutores.filter(ativo=True)
    
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
        
        instrutor_id = request.POST.get('instrutor_principal')
        turma.instrutor_principal = Instrutor.objects.get(id=instrutor_id) if instrutor_id else None
        
        turma.save()
        messages.success(request, f'Turma "{turma.nome}" atualizada com sucesso!')
        return redirect('gerenciar_turmas')
    
    return render(request, 'gestor/turmas/form.html', {
        'centro': centro,
        'filial': filial,
        'turma': turma,
        'cursos': cursos_context,
        'instrutores': instrutores_context,
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
            return render(request, "confirmar_cadastro.html", {"convite": convite, "post_data": request.POST})

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
    
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES, centro=centro)
        if form.is_valid():
            try:
                curso = form.save(commit=False)
                curso.centro = centro
                curso.filial = filial  # Associa à filial se existir
                
                # Se for salvar como rascunho
                if request.POST.get('rascunho'):
                    curso.rascunho = True
                    curso.publicado = False
                    curso.save()
                    form.save_m2m()
                    messages.success(request, 'Curso salvo como rascunho com sucesso!')
                    return redirect('listar_cursos')
                else:
                    # Salva e redireciona para overview
                    curso.rascunho = True
                    curso.publicado = False
                    curso.save()
                    form.save_m2m()
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
    if filial and curso.filial != filial:
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
        if filial and curso.filial != filial:
            messages.error(request, "Permissão negada.")
            return redirect('listar_cursos')
            
        # Validações finais antes de publicar
        if not curso.titulo:
            messages.error(request, "O curso precisa ter um título.")
            return redirect('curso_overview', curso_id=curso_id)
        
        if not curso.descricao:
            messages.error(request, "O curso precisa ter uma descrição.")
            return redirect('curso_overview', curso_id=curso_id)
        
        if not curso.instrutores.exists():
            messages.error(request, "O curso precisa ter pelo menos um instrutor.")
            return redirect('curso_overview', curso_id=curso_id)
        
        # Publica o curso
        curso.rascunho = False
        curso.publicado = True
        curso.data_publicacao = timezone.now()
        curso.save()
        
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
    
    cursos_qs = filial.cursos.all() if filial else centro.cursos.all()
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
    if filial and curso.filial != filial:
        messages.error(request, "Permissão negada.")
        return redirect('listar_cursos')
    
    if request.method == 'POST':
        form = CursoForm(request.POST, request.FILES, instance=curso, centro=centro)
        if form.is_valid():
            try:
                form.save()
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
    
    context = {
        'form': form,
        'curso': curso,
        'centro': centro,
        'filial': filial
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
        if filial and curso.filial != filial:
            return JsonResponse({'success': False, 'error': 'Permissão negada'})
            
        curso.publicado = True
        curso.save()
        
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
        if filial and curso.filial != filial:
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
        if filial and curso.filial != filial:
            messages.error(request, "Permissão negada.")
            return redirect('listar_cursos')
            
        curso.delete()
        
        messages.success(request, 'Curso excluído com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao excluir curso: {str(e)}')
    
    return redirect('listar_cursos')




# views.py
from django.http import JsonResponse
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
        
        # Redirecionar para a página de chat do aluno com a conversa selecionada
        return redirect(f'{reverse("aluno_chat")}?conversa_id={conversa.id}')
        
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
    cursos_ids = filial.cursos.values_list('id', flat=True) if filial else centro.cursos.values_list('id', flat=True)
    
    # Encontrar todas as inscrições nesses cursos
    from cursos_app.models import Inscricao
    inscricoes = Inscricao.objects.filter(curso_id__in=cursos_ids)
    alunos_ids = inscricoes.values_list('aluno_id', flat=True).distinct()
    
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
    
    cursos_ids = filial.cursos.values_list('id', flat=True) if filial else centro.cursos.values_list('id', flat=True)
    
    from cursos_app.models import Inscricao
    inscricoes = Inscricao.objects.filter(aluno=aluno, curso_id__in=cursos_ids).select_related('curso', 'turma_escolhida').order_by('-data_inscricao')
    
    if not inscricoes.exists():
        messages.warning(request, "O aluno selecionado não possui histórico neste Centro/Filial.")
        return redirect('gerenciar_alunos')
        
    return render(request, 'gestor/alunos/dossie.html', {
        'centro': centro,
        'filial': filial,
        'aluno': aluno,
        'inscricoes': inscricoes
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
        ).select_related('curso__filial', 'curso', 'aluno__usuario').order_by('-data_pagamento', '-data_inscricao')
        
        # Agregação global
        total_receita = inscricoes_pagas.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
        
        # Agregação por filial (null = Centro Mãe)
        receita_centro_mae = inscricoes_pagas.filter(curso__filial__isnull=True).aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
        
        # Receitas das filiais
        filiais_receita = []
        for fil in centro.filiais.all():
            receitas_f = inscricoes_pagas.filter(curso__filial=fil).aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
            if receitas_f > 0:
                filiais_receita.append({'nome': fil.nome, 'total': receitas_f})
                
    else:
        # É GESTOR_FILIAL - só os cursos da filial
        inscricoes_pagas = Inscricao.objects.filter(
            curso__filial=filial,
            valor_pago__gt=0
        ).select_related('curso', 'aluno__usuario').order_by('-data_pagamento', '-data_inscricao')
        
        total_receita = inscricoes_pagas.aggregate(Sum('valor_pago'))['valor_pago__sum'] or 0
        receita_centro_mae = 0
        filiais_receita = []

    # Pagamentos recentes
    pagamentos_recentes = inscricoes_pagas[:50]
    
    return render(request, 'gestor/financeiro/dashboard.html', {
        'centro': centro,
        'filial': filial,
        'total_receita': total_receita,
        'receita_centro_mae': receita_centro_mae,
        'filiais_receita': filiais_receita,
        'pagamentos_recentes': pagamentos_recentes
    })
@login_required
def listar_anuncios(request):
    """Listagem de anúncios do centro para o gestor"""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    anuncios = centro.anuncios.all().order_by('-data_publicacao')
    
    return render(request, 'gestor/anuncios/listar.html', {
        'centro': centro,
        'anuncios': anuncios
    })

@login_required
def criar_anuncio(request):
    """Criação de um novo anúncio institucional"""
    centro, filial = get_gestor_context(request.user)
    if not centro:
        return redirect('login_gestor')
        
    if request.method == 'POST':
        from .forms import AnuncioForm
        form = AnuncioForm(request.POST, request.FILES)
        if form.is_valid():
            anuncio = form.save(commit=False)
            anuncio.centro = centro
            anuncio.save()
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
