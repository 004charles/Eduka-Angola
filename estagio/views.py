from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from estagio.models import Estagio, AreaEstagio, InscricaoEstagio
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def _modulo_estagios_ativo():
    from gestoreduka.models import ModuloPublico
    return ModuloPublico.objects.filter(chave=ModuloPublico.ESTAGIOS, ativo=True).exists()


def _serializar_estagio(estagio, detalhe=False, aluno=None):
    try:
        imagem_url = estagio.imagem_principal.url if estagio.imagem_principal else ''
    except (ValueError, AttributeError):
        imagem_url = ''
    item = {'slug': estagio.slug, 'titulo': estagio.titulo, 'resumo': estagio.resumo, 'descricao': estagio.descricao if detalhe else '', 'centro': estagio.centro_formacao.nome, 'area': estagio.area.nome if estagio.area else 'Área profissional', 'modalidade': estagio.get_modalidade_display(), 'modalidade_codigo': estagio.modalidade, 'tipo_remuneracao': estagio.get_tipo_remuneracao_display(), 'valor_remuneracao': float(estagio.valor_remuneracao) if estagio.valor_remuneracao is not None else None, 'beneficios': estagio.beneficios, 'duracao_meses': estagio.duracao_meses, 'carga_horaria_semanal': estagio.carga_horaria_semanal, 'vagas_restantes': estagio.vagas_restantes, 'local_trabalho': estagio.local_trabalho, 'cidade': estagio.cidade, 'provincia': estagio.provincia, 'requisitos': estagio.requisitos, 'competencias_desejadas': estagio.competencias_desejadas, 'data_inicio': estagio.data_inicio.isoformat(), 'data_limite_inscricao': estagio.data_limite_inscricao.isoformat(), 'aceita_candidaturas': estagio.esta_aceitando_inscricoes, 'imagem_url': imagem_url, 'detalhe_url': f'/estagios/{estagio.slug}'}
    if aluno:
        candidatura = InscricaoEstagio.objects.filter(estagio=estagio, aluno=aluno).first()
        item['candidatura'] = {'status': candidatura.get_status_display(), 'data': candidatura.data_inscricao.isoformat()} if candidatura else None
    return item


@require_http_methods(['GET'])
def react_estagios(request, slug=None):
    if not _modulo_estagios_ativo():
        return JsonResponse({'detail': 'O módulo de Estágios não está disponível neste momento.'}, status=404)
    aluno = getattr(request.user, 'aluno_profile', None) if request.user.is_authenticated and getattr(request.user, 'tipo_usuario', '') == 'ALUNO' else None
    estagios = Estagio.objects.filter(ativo=True, centro_formacao__ativo=True).select_related('centro_formacao', 'area')
    if slug:
        estagio = get_object_or_404(estagios, slug=slug)
        Estagio.objects.filter(pk=estagio.pk).update(visualizacoes=F('visualizacoes') + 1)
        return JsonResponse({'estagio': _serializar_estagio(estagio, detalhe=True, aluno=aluno)})
    termo, area, modalidade = request.GET.get('q', '').strip(), request.GET.get('area', '').strip(), request.GET.get('modalidade', '').strip()
    if termo:
        estagios = estagios.filter(Q(titulo__icontains=termo) | Q(descricao__icontains=termo) | Q(centro_formacao__nome__icontains=termo))
    if area:
        estagios = estagios.filter(area__slug=area)
    if modalidade:
        estagios = estagios.filter(modalidade=modalidade)
    return JsonResponse({'estagios': [_serializar_estagio(item, aluno=aluno) for item in estagios.order_by('-destaque', '-data_publicacao')[:60]], 'areas': [{'slug': item.slug, 'nome': item.nome} for item in AreaEstagio.objects.filter(ativa=True)], 'modalidades': [{'codigo': codigo, 'nome': nome} for codigo, nome in Estagio.MODALIDADE]})


@require_http_methods(['POST'])
def react_candidatar_estagio(request, slug):
    if not _modulo_estagios_ativo():
        return JsonResponse({'detail': 'O módulo de Estágios não está disponível neste momento.'}, status=404)
    if not request.user.is_authenticated:
        return JsonResponse({'detail': 'Entre na sua conta de aluno para se candidatar.'}, status=401)
    aluno = getattr(request.user, 'aluno_profile', None) if getattr(request.user, 'tipo_usuario', '') == 'ALUNO' else None
    if not aluno:
        return JsonResponse({'detail': 'Apenas alunos podem candidatar-se a estágios.'}, status=403)
    estagio = get_object_or_404(Estagio.objects.filter(ativo=True), slug=slug)
    if not estagio.esta_aceitando_inscricoes:
        return JsonResponse({'detail': 'Esta vaga já não aceita candidaturas.'}, status=409)
    if InscricaoEstagio.objects.filter(estagio=estagio, aluno=aluno).exists():
        return JsonResponse({'detail': 'Já enviou uma candidatura para este estágio.'}, status=409)
    carta = request.POST.get('carta_motivacao', '').strip()
    if len(carta) < 30:
        return JsonResponse({'detail': 'Escreva uma carta de motivação com pelo menos 30 caracteres.'}, status=400)
    candidatura = InscricaoEstagio.objects.create(estagio=estagio, aluno=aluno, carta_motivacao=carta, curriculo=request.FILES.get('curriculo'))
    return JsonResponse({'ok': True, 'message': 'A candidatura foi enviada ao centro. Acompanhe o estado na sua conta.', 'candidatura': {'status': candidatura.get_status_display(), 'data': candidatura.data_inscricao.isoformat()}}, status=201)

def estagios_por_area(request, area_slug=None):
    if area_slug:
        area = AreaEstagio.objects.get(slug=area_slug)
        estagios_recomendados = Estagio.objects.filter(
            area=area,
            ativo=True,
            destaque=True
        )[:8]
    else:
        estagios_recomendados = Estagio.objects.filter(
            ativo=True,
            destaque=True
        )[:8]
    
    context = {
        'estagios_recomendados': estagios_recomendados,
    }
    return render(request, 'seu_template.html', context)

def estagio_detalhe(request, slug):
    estagio = get_object_or_404(Estagio, slug=slug, ativo=True)
    
    # Incrementar visualizações
    estagio.visualizacoes += 1
    estagio.save()
    
    ja_candidatou = False
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        aluno = getattr(request.user, 'aluno_profile', None)
        if aluno:
            ja_candidatou = InscricaoEstagio.objects.filter(estagio=estagio, aluno=aluno).exists()
            
    context = {
        'estagio': estagio,
        'ja_candidatou': ja_candidatou,
    }
    return render(request, 'estagio/detalhe_estagio.html', context)

@login_required
def candidatar_estagio(request, slug):
    if request.method == 'POST':
        estagio = get_object_or_404(Estagio, slug=slug, ativo=True)
        aluno = getattr(request.user, 'aluno_profile', None)
        
        if not aluno:
            messages.error(request, "Apenas alunos podem se candidatar a vagas de estágio.")
            return redirect('estagio:estagio_detalhe', slug=slug)
            
        if InscricaoEstagio.objects.filter(estagio=estagio, aluno=aluno).exists():
            messages.warning(request, "Você já se candidatou a este estágio.")
            return redirect('estagio:estagio_detalhe', slug=slug)
            
        carta_motivacao = request.POST.get('carta_motivacao', '')
        curriculo = request.FILES.get('curriculo')
        
        InscricaoEstagio.objects.create(
            estagio=estagio,
            aluno=aluno,
            carta_motivacao=carta_motivacao,
            curriculo=curriculo
        )
        
        messages.success(request, "Sua candidatura foi enviada com sucesso! O centro entrará em contacto.")
        return redirect('estagio:estagio_detalhe', slug=slug)
        
    return redirect('estagio:lista_estagios')

def lista_estagios(request):
    q = request.GET.get('q', '')
    area_id = request.GET.get('area', '')
    modalidade = request.GET.get('modalidade', '')
    
    estagios = Estagio.objects.filter(ativo=True).order_by('-data_publicacao')
    
    if q:
        estagios = estagios.filter(
            Q(titulo__icontains=q) | 
            Q(descricao__icontains=q) | 
            Q(centro_formacao__nome__icontains=q)
        )
        
    if area_id:
        estagios = estagios.filter(area_id=area_id)
        
    if modalidade:
        estagios = estagios.filter(modalidade=modalidade)
        
    areas = AreaEstagio.objects.filter(ativa=True)
    
    context = {
        'estagios': estagios,
        'areas': areas,
        'q': q,
        'area_selecionada': area_id,
        'modalidade_selecionada': modalidade,
        'modalidades': Estagio.MODALIDADE,
    }
    return render(request, 'estagio/lista_estagios.html', context)
