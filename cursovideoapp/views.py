from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import json
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from cursos_app.models import Categoria, Instrutor
from cursovideoapp.models import Curso_video, FavoritoCursoVideo, Aula, ProgressoAula, Certificado, Exercicio, Questao, Alternativa, ResultadoExercicio, RespostaEstudante
from django.core.cache import cache
from .utils import fetch_playlist_videos

@login_required
def importar_playlist_youtube(request, curso_id):
    """
    Importa todos os vídeos de uma playlist do YouTube como aulas de um curso.
    """
    curso = get_object_or_404(Curso_video, id=curso_id)
    
    # Verificar se o utilizador é o instrutor do curso ou superuser
    if not request.user.is_superuser:
        try:
            if curso.instrutor.usuario != request.user:
                return JsonResponse({'status': 'error', 'message': 'Não tens permissão.'}, status=403)
        except:
            return JsonResponse({'status': 'error', 'message': 'Erro de permissão.'}, status=403)

    if request.method == 'POST':
        playlist_url = request.POST.get('playlist_url')
        if not playlist_url:
            return JsonResponse({'status': 'error', 'message': 'URL da playlist é obrigatório.'})

        videos = fetch_playlist_videos(playlist_url)
        if not videos:
            return JsonResponse({'status': 'error', 'message': 'Nenhum vídeo encontrado ou erro na API.'})

        aulas_criadas = 0
        for v in videos:
            # Evitar duplicados se o URL já existir neste curso
            if not Aula.objects.filter(curso=curso, video_url=v['video_url']).exists():
                Aula.objects.create(
                    curso=curso,
                    titulo=v['titulo'],
                    video_url=v['video_url'],
                    duracao_segundos=v['duracao_segundos'],
                    ordem=v['ordem']
                )
                aulas_criadas += 1

        return JsonResponse({
            'status': 'success', 
            'message': f'Sucesso! {aulas_criadas} aulas importadas da playlist.',
            'total': len(videos)
        })

    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)

@login_required
def importar_playlist_admin(request, curso_id):
    """
    Exibe a página administrativa para importar playlist.
    """
    if not request.user.is_staff:
        return redirect('admin:index')
    
    curso = get_object_or_404(Curso_video, id=curso_id)
    return render(request, 'admin/importar_playlist.html', {'curso': curso})

@login_required
def emitir_certificado(request, curso_slug):
    """
    Gera ou exibe o certificado de conclusão do curso para o aluno logado.
    """
    curso = get_object_or_404(Curso_video, slug=curso_slug)
    try:
        aluno = request.user.aluno_profile
    except (ObjectDoesNotExist, AttributeError):
        return redirect('index')
    
    # Verificar se o aluno concluiu todas as aulas
    if not curso.verificar_conclusao(aluno):
        return redirect('cursovideoapp:detalhe_curso', slug=curso_slug)
    
    # Obter ou criar o certificado
    certificado, created = Certificado.objects.get_or_create(aluno=aluno, curso=curso)
    
    if created or not certificado.analise_ia_competencias:
        from .models import ResultadoExercicio
        from inteligencia.ai_utils import gerar_perfil_competencias_ia
        
        # Calcular métricas para a IA
        resultados = ResultadoExercicio.objects.filter(aluno=aluno, exercicio__aula__curso=curso)
        total_ex = resultados.count()
        media_nota = sum([r.pontuacao for r in resultados]) / total_ex if total_ex > 0 else 0
        
        # Preencher dados no certificado
        certificado.nota_final = media_nota
        certificado.total_exercicios_concluidos = total_ex
        
        # Chamar Gemini para gerar o perfil técnico
        perfil = gerar_perfil_competencias_ia(aluno.nome, curso.titulo, media_nota, total_ex)
        certificado.analise_ia_competencias = perfil
        certificado.save()
    
    # Calcular média das notas dos exercícios se ainda não tiver nota ou se for uma nova emissão
    resultados = ResultadoExercicio.objects.filter(aluno=aluno, exercicio__aula__curso=curso)
    if resultados.exists():
        media = resultados.aggregate(media=Avg('pontuacao'))['media']
        certificado.nota_final = media
        certificado.total_exercicios_concluidos = resultados.count()
        certificado.save()

    # Gerar link de verificação completo para o QR Code
    verificacao_url = request.build_absolute_uri(
        reverse('cursovideoapp:verificar_certificado', kwargs={'codigo': certificado.codigo_verificacao})
    )
    
    return render(request, 'cursovideo/certificado.html', {
        'certificado': certificado,
        'aluno': aluno,
        'curso': curso,
        'verificacao_url': verificacao_url
    })

def verificar_certificado(request, codigo):
    """
    Página pública para validar a autenticidade de um certificado.
    """
    certificado = get_object_or_404(Certificado, codigo_verificacao=codigo)
    return render(request, 'cursovideo/verificar_certificado.html', {
        'certificado': certificado
    })
from avaliacoes.models import Comentario
from cursos_app.forms import AvaliacaoForm

def sessao_ver_todos(request, sessao_tipo):
    """
    Lista todos os cursos de uma sessão específica (recentes, populares, etc).
    """
    qs = Curso_video.objects.all()
    titulo = "Cursos"
    
    if sessao_tipo == 'recentes':
        qs = qs.order_by('-data_publicacao')
        titulo = "Novos Lançamentos"
    elif sessao_tipo == 'populares':
        qs = qs.annotate(num_inscritos=Count('inscritos')).order_by('-num_inscritos')
        titulo = "Em Alta no EdukAngola"
    elif sessao_tipo == 'mais_assistidos':
        qs = qs.annotate(total_views=Sum('aulas__visualizacoes')).order_by('-total_views')
        titulo = "Cursos Mais Assistidos"
    elif sessao_tipo == 'tecnologia':
        qs = qs.filter(categoria__slug='tecnologia').order_by('-data_publicacao')
        titulo = "Domine a Tecnologia Actual"
    
    context = {
        'cursos': qs,
        'titulo': titulo,
        'sessao_tipo': sessao_tipo,
    }
    
    return render(request, 'cursovideo/sessao_lista.html', context)

def home_videos(request):
    """
    Catálogo de cursos em vídeo com suporte a busca e filtros, idêntico ao catálogo de cursos presenciais.
    """
    from django.core.paginator import Paginator

    # 1. Obter todos os cursos em vídeo
    cursos = Curso_video.objects.select_related('instrutor', 'categoria').prefetch_related('aulas').all()

    # 2. Obter parâmetros de filtros
    categoria_id = request.GET.get('categoria')
    preco = request.GET.get('preco')
    busca = request.GET.get('q')
    filtro_tempo = request.GET.get('tempo')  # 'semana'
    destaque_filtro = request.GET.get('destaque')  # 'true'
    para_voce = request.GET.get('para_voce')  # 'true'

    # Aplicar filtros de busca
    if busca:
        cursos = cursos.filter(
            Q(titulo__icontains=busca) | 
            Q(descricao__icontains=busca) |
            Q(instrutor__nome__icontains=busca)
        )

    # Aplicar filtro por categoria
    if categoria_id:
        cursos = cursos.filter(categoria_id=categoria_id)

    # Aplicar filtro de preço
    if preco == 'gratuitos':
        cursos = cursos.filter(is_pago=False)
    elif preco == 'pagina_100':
        cursos = cursos.filter(is_pago=True, preco__lte=100)
    elif preco == '100_500':
        cursos = cursos.filter(is_pago=True, preco__gte=100, preco__lte=500)
    elif preco == '500_plus':
        cursos = cursos.filter(is_pago=True, preco__gt=500)

    # Filtros rápidos da barra lateral
    if filtro_tempo == 'semana':
        uma_semana_atras = timezone.now() - timedelta(days=7)
        cursos = cursos.filter(data_publicacao__gte=uma_semana_atras)

    if destaque_filtro == 'true':
        cursos = cursos.filter(destaque=True)

    # Filtro de IA "Para Mim"
    if para_voce == 'true' and request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            from inteligencia.utils import recomendar_cursos
            cursos_recomendados_ids = recomendar_cursos(request.user.aluno_profile)
            if cursos_recomendados_ids:
                # Filtrar para mostrar apenas os cursos recomendados
                # Como recomendar_cursos retorna IDs de Curso padrão, adaptamos para Curso_video 
                # filtrando por categorias correspondentes ou permitindo fallback
                pass
        except ImportError:
            pass

    # Ordenação
    order = request.GET.get('order')
    if order == 'mais_procurados':
        cursos = cursos.annotate(num_inscritos=Count('inscritos')).order_by('-num_inscritos')
    else:
        # Padrão: mais recentes
        cursos = cursos.order_by('-data_publicacao')

    # Paginação
    paginator = Paginator(cursos, 12)  # 12 cursos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Obter categorias para os filtros
    categorias = Categoria.objects.annotate(
        total_cursos=Count('cursos_video')
    )

    context = {
        'cursos': page_obj,
        'page_obj': page_obj,
        'categorias': categorias,
        'total_cursos': cursos.count(),
        'filtros': {
            'categoria': categoria_id,
            'preco': preco,
            'busca': busca,
            'tempo': filtro_tempo,
            'destaque': destaque_filtro,
            'para_voce': para_voce,
        },
        'active_menu': 'cursos_video',
    }

    return render(request, 'cursovideo/catalogo.html', context)


@require_POST
def toggle_favorito_video(request):
    """
    API para alternar o status de favorito de um curso em vídeo.
    """
    if not request.user.is_authenticated or request.user.tipo_usuario != 'ALUNO':
        return JsonResponse({'status': 'error', 'message': 'Não autorizado'}, status=403)
    
    try:
        data = json.loads(request.body)
        curso_id = data.get('curso_id')
        curso = Curso_video.objects.get(id=curso_id)
        
        try:
            aluno = request.user.aluno_profile
        except (ObjectDoesNotExist, AttributeError):
            return JsonResponse({'status': 'error', 'message': 'Perfil de aluno não encontrado'}, status=403)
        
        favorito, created = FavoritoCursoVideo.objects.get_or_create(aluno=aluno, curso=curso)
        
        if not created:
            favorito.delete()
            return JsonResponse({'status': 'removed'})
        
        return JsonResponse({'status': 'added'})
        
    except Curso_video.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Curso não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def api_load_more_videos(request):
    """
    API para carregar mais cursos em vídeo.
    """
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 4))
        tipo_filtro = request.GET.get('tipo', 'recentes')
        categoria_slug = request.GET.get('categoria', None)
        
        qs = Curso_video.objects.all()
        
        if categoria_slug:
            qs = qs.filter(categoria__slug=categoria_slug)
            
        if tipo_filtro == 'populares':
            qs = qs.annotate(num=Count('inscritos')).order_by('-num')
        else:
            qs = qs.order_by('-data_publicacao')
            
        cursos = qs[offset:offset+limit]
        
        data = []
        favoritos = []
        if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
             try:
                 aluno = request.user.aluno_profile
                 favoritos = list(FavoritoCursoVideo.objects.filter(
                     aluno=aluno, 
                     curso__in=cursos
                 ).values_list('curso_id', flat=True))
             except (ObjectDoesNotExist, AttributeError):
                 favoritos = []

        for curso in cursos:
            # Fallback for image
            img_url = curso.capa.url if curso.capa else '/static/assets/images/course/default-course.jpg'
            
            data.append({
                'id': curso.id,
                'titulo': curso.titulo,
                'imagem_url': img_url,
                'instrutor': curso.instrutor.nome,
                'visualizacoes': 0, # Video model might not have views yet
                'is_favorito': curso.id in favoritos,
                # 'url_detalhe': reverse('curso_video_detalhe', args=[curso.id]) # Update with real URL name
            })
            
        return JsonResponse({'cursos': data, 'has_more': qs.count() > offset + limit})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def analytics_mercado(request):
    """
    Página de inteligência de mercado que mostra gaps de competências em Angola
    e conecta cursos/centros a essas necessidades usando o Gemini.
    """
    from inteligencia.ai_utils import analisar_mercado_angola_ia
    from .models import Curso_video
    
    # Preparar contexto dos cursos para a IA
    cursos_nomes = ", ".join([c.titulo for c in Curso_video.objects.all()[:15]])
    
    # Tentar obter análise da IA
    ai_data = analisar_mercado_angola_ia(cursos_nomes)
    
    if ai_data:
        market_gaps = ai_data.get('gaps', [])
        insight_texto = ai_data.get('insight_texto', "")
        top_centros = ai_data.get('top_centros_sugeridos', [])
        is_real_ai = True
    else:
        # Fallback caso a IA falhe ou não haja API Key
        market_gaps = [
            {"skill": "Cibersegurança", "demanda": 85, "oferta": 20, "tendencia": "up"},
            {"skill": "Análise de Dados", "demanda": 92, "oferta": 35, "tendencia": "up"},
            {"skill": "Energias Renováveis", "demanda": 75, "oferta": 15, "tendencia": "up"},
            {"skill": "Marketing Digital E-commerce", "demanda": 88, "oferta": 50, "tendencia": "stable"},
        ]
        insight_texto = "O mercado angolano está em fase de transição digital, com forte procura por competências técnicas em infraestrutura e serviços digitais."
        top_centros = ["ISPTEC", "Centro de Formação Angola", "Digital Hub Luanda"]
        is_real_ai = False
    
    cursos_sugeridos = Curso_video.objects.filter(destaque=True)[:4]
    
    context = {
        'market_gaps': market_gaps,
        'insight_texto': insight_texto,
        'top_centros': top_centros,
        'cursos_sugeridos': cursos_sugeridos,
        'is_real_ai': is_real_ai,
        'total_cursos': Curso_video.objects.count(),
        'hoje': timezone.now(),
    }
    return render(request, 'cursovideo/analytics.html', context)

# --- Restored Views ---

def lista_cursos(request):
    """
    Exibe a lista de todos os cursos em vídeo, com suporte a busca.
    """
    query = request.GET.get('q', '')
    qs = Curso_video.objects.select_related('instrutor', 'categoria').all()
    titulo = "Todos os Cursos"
    
    if query:
        qs = qs.filter(Q(titulo__icontains=query) | Q(descricao__icontains=query))
        titulo = f"Resultados para: '{query}'"
        
    context = {
        'cursos': qs,
        'titulo': titulo,
        'query': query,
    }
    return render(request, 'cursovideo/sessao_lista.html', context)

def detalhe_curso(request, slug):
    """
    Exibe os detalhes de um curso em vídeo, incluindo aulas e avaliações.
    """
    curso = get_object_or_404(Curso_video.objects.select_related('instrutor', 'categoria'), slug=slug)
    
    # Atualizar histórico de visualizações recentes
    viewed = request.session.get('viewed_video_cursos', [])
    if curso.id in viewed:
        viewed.remove(curso.id)
    viewed.insert(0, curso.id)
    request.session['viewed_video_cursos'] = viewed[:3]

    
    # 1. Verificar se o aluno está inscrito e logado
    aluno_logado = request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO'
    aluno_obj = None
    aluno_inscrito = False
    
    if aluno_logado:
        try:
            aluno_obj = request.user.aluno_profile
            aluno_inscrito = curso.inscritos.filter(id=aluno_obj.id).exists()
        except (ObjectDoesNotExist, AttributeError):
            aluno_logado = False

    # 2. Carregar comentários e avaliações (Paginados: Top 5 principais)
    comentarios_all = Comentario.objects.select_related('aluno').filter(
        curso_video=curso,
        aprovado=True,
        parent__isnull=True
    ).order_by('-data_comentario')
    
    comentarios = comentarios_all[:5]
    total_principais = comentarios_all.count()

    # 3. Verificar comentário existente e formulário
    comentario_existente = None
    if aluno_obj:
        comentario_existente = Comentario.objects.filter(
            aluno=aluno_obj, 
            curso_video=curso
        ).first()
    
    avaliacao_form = None
    if aluno_logado and aluno_inscrito:
        avaliacao_form = AvaliacaoForm(instance=comentario_existente)

    # 4. Outros dados (aulas, cursos recomendados)
    aulas = curso.aulas.all().order_by('ordem')
    total_visualizacoes = aulas.aggregate(total=Count('id'))['total'] # Placeholder simple logic
    
    cursos_recomendados = Curso_video.objects.exclude(id=curso.id)[:6]
            
    # 4. Calcular progresso do curso se aluno logado e inscrito
    progresso_total = 0
    if aluno_inscrito:
        total_aulas = curso.aulas.count()
        if total_aulas > 0:
            aulas_concluidas = ProgressoAula.objects.filter(
                aluno=aluno_obj, 
                aula__curso=curso, 
                concluida=True
            ).count()
            progresso_total = int((aulas_concluidas / total_aulas) * 100)
            
    return render(request, 'cursovideo/detalhe_curso.html', {
        'curso': curso,
        'aluno_logado': aluno_logado,
        'aluno_inscrito': aluno_inscrito,
        'aulas': aulas,
        'comentarios': comentarios,
        'total_principais': total_principais,
        'avaliacao_form': avaliacao_form,
        'comentario_existente': comentario_existente,
        'total_visualizacoes': curso.aulas.all().count(), # Simplificado para exemplo
        'cursos_recomendados': cursos_recomendados,
        'progresso_total': progresso_total,
    })

@login_required
def toggle_inscricao(request, slug):
    """
    Inscreve ou remove a inscrição de um aluno em um curso.
    """
    curso = get_object_or_404(Curso_video, slug=slug)
    
    if request.user.tipo_usuario != 'ALUNO':
        return redirect('cursovideoapp:detalhe_curso', slug=slug)
        
    try:
        aluno = request.user.aluno_profile
    except (ObjectDoesNotExist, AttributeError):
        # Se for um Aluno sem perfil (deveria ser raro, mas acontece)
        messages.error(request, "Perfil de aluno não encontrado. Por favor, complete o seu registo.")
        return redirect('index')

    if curso.inscritos.filter(id=aluno.id).exists():
        curso.inscritos.remove(aluno)
        messages.success(request, f"Inscrição no curso '{curso.titulo}' removida com sucesso.")
    else:
        if getattr(curso, 'is_pago', False) and getattr(curso, 'preco', 0) > 0:
            from pagamentos.services import PaymentService
            try:
                servico = PaymentService()
                pagamento = servico.criar_pagamento(
                    usuario=request.user,
                    tipo_pagamento='INSCRICAO_VIDEO',
                    valor=float(curso.preco),
                    moeda='AOA',
                    curso=None,
                    url_sucesso=request.build_absolute_uri(reverse('cursovideoapp:detalhe_curso', kwargs={'slug': slug})),
                    url_cancelamento=request.build_absolute_uri(reverse('cursovideoapp:detalhe_curso', kwargs={'slug': slug})),
                    metadados={'acao': 'inscricao_video', 'curso_video_id': str(curso.id)}
                )
                messages.info(request, "Você está sendo redirecionado para o pagamento seguro via Prontu.")
                return redirect(pagamento.url_pagamento)
            except Exception as e:
                messages.error(request, f"Erro ao iniciar pagamento: {str(e)}")
        else:
            curso.inscritos.add(aluno)
            messages.success(request, f"Inscrição realizada com sucesso! Bem-vindo(a) ao curso.")
        
    return redirect('cursovideoapp:detalhe_curso', slug=slug)

@login_required
def ver_aula(request, curso_slug, pk):
    """
    Interface de visualização de uma aula específica do curso com lógica de desbloqueio sequencial.
    """
    curso = get_object_or_404(Curso_video, slug=curso_slug)
    aula_atual = get_object_or_404(Aula, pk=pk, curso=curso)
    
    # Atualizar histórico de visualizações recentes
    viewed = request.session.get('viewed_video_cursos', [])
    if curso.id in viewed:
        viewed.remove(curso.id)
    viewed.insert(0, curso.id)
    request.session['viewed_video_cursos'] = viewed[:3]
    
    # Verificar se o usuário é o instrutor deste curso
    is_instrutor = False
    if request.user.tipo_usuario == 'INSTRUTOR':
        if hasattr(request.user, 'instrutor_profile') and curso.instrutor == request.user.instrutor_profile:
            is_instrutor = True
    
    aluno = None
    if not is_instrutor:
        # Se não for o instrutor, verificar inscrição de aluno
        try:
            aluno = request.user.aluno_profile
        except (ObjectDoesNotExist, AttributeError):
            return redirect('index')
            
        if not curso.inscritos.filter(id=aluno.id).exists():
            return redirect('cursovideoapp:detalhe_curso', slug=curso_slug)
    
    aulas = curso.aulas.all().order_by('ordem')
    
    # Lógica de desbloqueio sequencial e progresso (Apenas para Alunos)
    concluidas_ids = set()
    if aluno:
        progressos = ProgressoAula.objects.filter(aluno=aluno, aula__curso=curso)
        concluidas_ids = set(progressos.filter(concluida=True).values_list('aula_id', flat=True))
    else:
        # Instrutor vê tudo desbloqueado
        pass
    
    aulas_status = []
    # A primeira aula está sempre desbloqueada
    aula_anterior_concluida = True 
    
    for i, aula in enumerate(aulas):
        if is_instrutor or i == 0 or not aula.requer_conclusao_anterior:
            is_unlocked = True
        else:
            # Desbloqueada se a anterior estiver concluída
            is_unlocked = aulas[i-1].id in concluidas_ids
            
        aulas_status.append({
            'id': aula.id,
            'titulo': aula.titulo,
            'pk': aula.pk,
            'duracao_formatada': aula.duracao_formatada(),
            'is_unlocked': is_unlocked,
            'is_completed': aula.id in concluidas_ids,
            'ordem': aula.ordem,
            'requer_conclusao_anterior': aula.requer_conclusao_anterior
        })
    
    # Verificação de segurança: impedir acesso via URL a aulas bloqueadas
    aula_atual_info = next((item for item in aulas_status if item['id'] == aula_atual.id), None)
    if not aula_atual_info or not aula_atual_info['is_unlocked']:
        # Encontrar a última aula desbloqueada para redirecionar
        ultima_desbloqueada = next((item for item in reversed(aulas_status) if item['is_unlocked']), None)
        if ultima_desbloqueada:
            return redirect('cursovideoapp:ver_aula', curso_slug=curso_slug, pk=ultima_desbloqueada['pk'])
        return redirect('cursovideoapp:detalhe_curso', slug=curso_slug)

    proxima_aula = aulas.filter(ordem__gt=aula_atual.ordem).first()
    aula_anterior = aulas.filter(ordem__lt=aula_atual.ordem).last()
    
    # Calcular progresso total
    total_aulas = len(aulas_status)
    aulas_concluidas = sum(1 for item in aulas_status if item['is_completed'])
    progresso_total = int((aulas_concluidas / total_aulas) * 100) if total_aulas > 0 else 0
    
    # Obter progresso atual para controle de avanço no player (Apenas Alunos)
    progresso_atual = None
    if aluno:
        progresso_atual, created = ProgressoAula.objects.get_or_create(aluno=aluno, aula=aula_atual)

    # Obter nota atual do aluno para esta aula
    nota_aula = None
    if aluno:
        from .models import NotaAula
        nota_aula = NotaAula.objects.filter(aluno=aluno, aula=aula_atual).first()

    # Obter comentários principais da aula (sem pai)
    comentarios = aula_atual.comentarios.filter(parent__isnull=True).select_related('aluno__usuario', 'instrutor').prefetch_related('respostas')

    # Obter resultado do exercício se houver
    resultado_exercicio = None
    if aluno and hasattr(aula_atual, 'exercicio'):
        resultado_exercicio = ResultadoExercicio.objects.filter(aluno=aluno, exercicio=aula_atual.exercicio).first()

    # Obter materiais gerais do curso (Material Único)
    from .models import MaterialCurso
    materiais_gerais = curso.materiais_gerais.all()

    return render(request, 'cursovideo/ver_aula.html', {
        'curso': curso,
        'aula_atual': aula_atual,
        'proxima_aula': proxima_aula,
        'aula_anterior': aula_anterior,
        'aulas_status': aulas_status,
        'aulas': aulas,
        'progresso_total': progresso_total,
        'progresso_atual': progresso_atual,
        'nota_aula': nota_aula,
        'comentarios': comentarios,
        'is_instrutor_preview': is_instrutor,
        'resultado_exercicio': resultado_exercicio,
        'materiais_gerais': materiais_gerais, # Adicionado aqui
    })

@require_POST
@login_required
def salvar_comentario_aula(request, aula_id):
    """
    API para salvar uma nova dúvida/comentário na aula ou responder a um existente.
    """
    aula = get_object_or_404(Aula, id=aula_id)
    texto = request.POST.get('texto', '').strip()
    parent_id = request.POST.get('parent_id')
    
    if not texto:
        return JsonResponse({'status': 'error', 'message': 'Texto vazio'}, status=400)
        
    from .models import ComentarioAula
    
    # Identificar autor (pode ser Aluno ou Instrutor)
    aluno = None
    instrutor = None
    if request.user.tipo_usuario == 'ALUNO':
        aluno = request.user.aluno_profile
    elif request.user.tipo_usuario == 'INSTRUTOR':
        instrutor = request.user.instrutor_profile
        
    parent = None
    if parent_id:
        parent = get_object_or_404(ComentarioAula, id=parent_id)
        
    comentario = ComentarioAula.objects.create(
        aluno=aluno,
        instrutor=instrutor,
        aula=aula,
        texto=texto,
        parent=parent
    )
    
    nome_autor = aluno.nome if aluno else instrutor.nome
    is_instrutor = instrutor is not None
    
    # --- INTEGRAÇÃO EDUKA AI ---
    resposta_ia = None
    if aluno and not parent: # Apenas para dúvidas novas de alunos
        from inteligencia.ai_utils import responder_duvida_ia
        resposta_texto = responder_duvida_ia(texto, aula.titulo, aula.descricao)
        
        # Criar resposta da IA como se fosse um comentário pai
        if resposta_texto:
            # Criamos como se fosse um instrutor 'Eduka AI' ou apenas um comentário especial
            # Por agora, vamos criar como um ComentarioAula sem autor humano
            ComentarioAula.objects.create(
                aula=aula,
                texto=f"🤖 **Eduka AI:** {resposta_texto}",
                parent=comentario
            )
            resposta_ia = resposta_texto

    return JsonResponse({
        'status': 'success', 
        'message': 'Enviado!',
        'id': comentario.id,
        'nome': nome_autor,
        'is_instrutor': is_instrutor,
        'texto': texto,
        'data': 'Agora mesmo',
        'resposta_ia': resposta_ia
    })

@require_POST
@login_required
def salvar_nota_aula(request, aula_id):
    """
    API para salvar ou atualizar a nota privada do aluno para uma aula.
    """
    if not request.user.tipo_usuario == 'ALUNO':
        return JsonResponse({'status': 'error', 'message': 'Não autorizado'}, status=403)
        
    aula = get_object_or_404(Aula, id=aula_id)
    aluno = request.user.aluno_profile
    conteudo = request.POST.get('conteudo', '')
    
    from .models import NotaAula
    nota, created = NotaAula.objects.update_or_create(
        aluno=aluno,
        aula=aula,
        defaults={'conteudo': conteudo}
    )
    
    return JsonResponse({'status': 'success', 'message': 'Nota salva com sucesso!'})


@login_required
def salvar_comentario_video(request, slug):
    """
    Salva ou atualiza uma avaliação (comentário) do aluno para o curso.
    """
    curso = get_object_or_404(Curso_video, slug=slug)
    
    if request.user.tipo_usuario != 'ALUNO':
        return redirect('cursovideoapp:detalhe_curso', slug=slug)
        
    try:
        aluno = request.user.aluno_profile
    except (ObjectDoesNotExist, AttributeError):
        return redirect('index')
    
    # 2. Verificar se aluno está inscrito
    if not curso.inscritos.filter(id=aluno.id).exists():
        return redirect('cursovideoapp:detalhe_curso', slug=slug)
    
    # 3. Verificar se já avaliou
    comentario_existente = Comentario.objects.filter(aluno=aluno, curso_video=curso).first()
    
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=comentario_existente)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.aluno = aluno
            comentario.curso_video = curso
            
            # Lógica de resposta
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    comentario.parent = Comentario.objects.get(id=parent_id)
                    # Respostas não têm avaliação/nota
                    comentario.avaliacao = 0 
                except Comentario.DoesNotExist:
                    pass
                    
            comentario.save()
            messages.success(request, "Sua interação foi enviada com sucesso!")
        else:
            # Exibir erros de validação (ex: comentário muito curto)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
            
    return redirect('cursovideoapp:detalhe_curso', slug=slug)

@require_POST
@login_required
def atualizar_progresso(request, aula_id):
    """
    Atualiza o tempo assistido e o status de conclusão de uma aula.
    """
    aula = get_object_or_404(Aula, id=aula_id)
    
    # Verificar se o usuário tem um perfil de aluno (pode ser admin testando)
    if not hasattr(request.user, 'aluno_profile') or not request.user.aluno_profile:
        return JsonResponse({'status': 'error', 'message': 'Perfil de aluno necessário'}, status=403)
        
    aluno = request.user.aluno_profile
    
    # Criar ou obter registro de progresso
    progresso, created = ProgressoAula.objects.get_or_create(
        aluno=aluno,
        aula=aula
    )
    
    # Receber dados do POST
    try:
        tempo_raw = request.POST.get('tempo_assistido', 0)
        tempo_assistido = int(float(tempo_raw))
        
        concluida_raw = request.POST.get('concluida', '').lower()
        concluida_solicitada = concluida_raw in ['true', '1', 'on', 'yes']
        
        agora = timezone.now()
        
        # 1. Validar Saltos no Tempo (Anti-Speedhacks e Hacks de Consola)
        if tempo_assistido > progresso.tempo_assistido:
            if progresso.tempo_assistido > 0:
                delta_real = (agora - progresso.data_ultimo_acesso).total_seconds()
                incremento = tempo_assistido - progresso.tempo_assistido
                
                # Tolerância de visualização: até 2.5x speed + 15 segundos buffer de atraso de rede
                limite = (delta_real * 2.5) + 15
                
                if incremento > limite:
                    # Detetado Hack: não guardamos o progresso.
                    return JsonResponse({
                        'success': False, 
                        'error': 'Manipulacão temporal detectada (Anti-Fraude). Por favor assista de forma contínua.',
                    }, status=403)
                    
            progresso.tempo_assistido = tempo_assistido
        
        # 2. Ignorar Pedidos de "Concluída" sem ter visto o vídeo
        if concluida_solicitada and not progresso.concluida:
            if aula.duracao_segundos > 0:
                percentagem = (progresso.tempo_assistido / aula.duracao_segundos) * 100
                if percentagem >= 90:  # Exige mínimo de 90% visto para libertar Certificado
                    progresso.concluida = True
            else:
                # Fallback caso a aula não possua duração cadastrada pelo gestor
                if progresso.tempo_assistido > 5:
                    progresso.concluida = True
            
        progresso.save()
        
        return JsonResponse({
            'success': True,
            'progresso_percentual': progresso.progresso_percentual(),
            'concluida': progresso.concluida
        })
    except (ValueError, TypeError) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def api_carregar_comentarios_video(request, curso_id):
    """Retorna comentários paginados para cursos em vídeo via JSON"""
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 5))
    
    comentarios = Comentario.objects.filter(
        curso_video_id=curso_id, 
        aprovado=True,
        parent__isnull=True
    ).select_related('aluno').order_by('-data_comentario')[offset:offset+limit]
    
    data = []
    for c in comentarios:
        respostas = []
        for r in c.respostas_comunidade.all():
            respostas.append({
                'aluno': r.aluno.nome,
                'comentario': r.comentario,
                'foto': r.aluno.get_foto_perfil_url() if hasattr(r.aluno, 'get_foto_perfil_url') else None,
            })
            
        data.append({
            'id': c.id,
            'aluno': c.aluno.nome,
            'foto': c.aluno.get_foto_perfil_url() if hasattr(c.aluno, 'get_foto_perfil_url') else None,
            'avaliacao': c.avaliacao,
            'comentario': c.comentario,
            'data': c.data_comentario.strftime('%d/%m/%Y'),
            'resposta': c.resposta,
            'resposta_data': c.resposta_data.strftime('%d/%m/%Y') if c.resposta_data else None,
            'respostas_comunidade': respostas
        })
    
    total_principais = Comentario.objects.filter(curso_video_id=curso_id, aprovado=True, parent__isnull=True).count()
    return JsonResponse({'comentarios': data, 'has_more': total_principais > offset + limit})

@login_required
def detalhes_exercicio(request, aula_id):
    """
    Exibe o exercício/quiz associado a uma aula.
    """
    aula = get_object_or_404(Aula, id=aula_id)
    exercicio = get_object_or_404(Exercicio, aula=aula)
    aluno = request.user.aluno_profile
    
    # Verificar se já respondeu
    resultado_existente = ResultadoExercicio.objects.filter(aluno=aluno, exercicio=exercicio).first()
    
    context = {
        'aula': aula,
        'exercicio': exercicio,
        'questoes': exercicio.questoes.all().prefetch_related('alternativas'),
        'resultado_existente': resultado_existente,
    }
    return render(request, 'cursovideo/exercicio.html', context)

@login_required
@require_POST
def submeter_exercicio(request, aula_id):
    """
    Processa as respostas do aluno e calcula a nota.
    """
    aula = get_object_or_404(Aula, id=aula_id)
    exercicio = get_object_or_404(Exercicio, aula=aula)
    aluno = request.user.aluno_profile
    
    questoes = exercicio.questoes.all()
    total_questoes = questoes.count()
    acertos = 0
    
    # Criar ou atualizar o resultado
    resultado, created = ResultadoExercicio.objects.get_or_create(
        aluno=aluno,
        exercicio=exercicio,
        defaults={'pontuacao': 0, 'acertos': 0, 'total_questoes': total_questoes}
    )
    
    # Limpar respostas anteriores se estiver a repetir
    resultado.respostas.all().delete()
    
    for questao in questoes:
        alternativa_id = request.POST.get(f'questao_{questao.id}')
        if alternativa_id:
            alternativa = get_object_or_404(Alternativa, id=alternativa_id, questao=questao)
            is_correta = alternativa.is_correta
            if is_correta:
                acertos += 1
            
            RespostaEstudante.objects.create(
                resultado=resultado,
                questao=questao,
                alternativa_escolhida=alternativa,
                correta=is_correta
            )
            
    pontuacao = (acertos / total_questoes * 100) if total_questoes > 0 else 0
    resultado.acertos = acertos
    resultado.total_questoes = total_questoes
    resultado.pontuacao = pontuacao
    resultado.save()
    
    return redirect('cursovideoapp:resultado_exercicio', resultado_id=resultado.id)

@login_required
def resultado_exercicio(request, resultado_id):
    """
    Exibe o resultado detalhado de um exercício.
    """
    resultado = get_object_or_404(ResultadoExercicio, id=resultado_id, aluno=request.user.aluno_profile)
    respostas = resultado.respostas.all().select_related('questao', 'alternativa_escolhida')
    
    # Pegar próxima aula para o botão de continuar
    proxima_aula = Aula.objects.filter(
        curso=resultado.exercicio.aula.curso, 
        ordem__gt=resultado.exercicio.aula.ordem
    ).order_by('ordem').first()
    
    return render(request, 'cursovideo/resultado_exercicio.html', {
        'resultado': resultado,
        'respostas': respostas,
        'proxima_aula': proxima_aula
    })

def orientador_ia_view(request):
    """Renderiza a página do Orientador Vocacional IA."""
    return render(request, 'cursovideo/orientador_ia.html')

@csrf_exempt
def api_orientacao_vocacional(request):
    """Endpoint API para processar a orientação vocacional."""
    if request.method == 'POST':
        from inteligencia.ai_utils import orientacao_vocacional_ia
        from .models import Curso_video
        from gestoreduka.models import CentroDeFormacao
        from django.db.models import Q
        
        perfil = request.POST.get('perfil', '')
        interesses = request.POST.get('interesses', '')
        
        # Obter lista de centros parceiros para a IA (garantindo que o nome não seja None)
        centros_qs = CentroDeFormacao.objects.filter(ativo=True).exclude(nome__isnull=True)
        centros_parceiros = ", ".join([c.nome for c in centros_qs if c.nome])
        
        data = orientacao_vocacional_ia(perfil, interesses, centros_parceiros)
        
        orientacao = data.get('orientacao', '')
        keywords = data.get('keywords', [])
        sugestoes_externas = data.get('sugestoes_externas', [])
        
        # Buscar cursos relacionados (Internos - Play)
        cursos_relacionados = []
        if keywords:
            query = Q()
            for kw in keywords:
                query |= Q(titulo__icontains=kw) | Q(descricao__icontains=kw) | Q(categoria__nome__icontains=kw)
            
            # Cursos de Vídeo (Play)
            cursos_qs = Curso_video.objects.filter(query).distinct()[:3]
            for c in cursos_qs:
                cursos_relacionados.append({
                    'titulo': c.titulo,
                    'url': reverse('cursovideoapp:detalhe_curso', kwargs={'slug': c.slug}),
                    'capa': c.capa.url if c.capa else '/static/assets/images/course/default-course.jpg',
                    'tipo': 'online'
                })

            # Cursos dos Centros (Presenciais/Híbridos)
            from cursos_app.models import Curso as CursoCentro
            cursos_centros_qs = CursoCentro.objects.filter(query, publicado=True).distinct()[:3]
            for cc in cursos_centros_qs:
                cursos_relacionados.append({
                    'titulo': cc.titulo,
                    'url': reverse('curso_detalhe', kwargs={'id': cc.id}),
                    'capa': cc.imagem.url if cc.imagem else '/static/assets/images/course/default-course.jpg',
                    'tipo': 'presencial',
                    'centro': cc.centro.nome,
                    'centro_id': cc.centro.id
                })
        
        return JsonResponse({
            'orientacao': orientacao,
            'cursos': cursos_relacionados,
            'sugestoes_externas': sugestoes_externas
        })
    return JsonResponse({'error': 'Método inválido'}, status=400)
