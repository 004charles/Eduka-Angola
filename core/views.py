from datetime import timedelta

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Count, Q, Prefetch, Value, F
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone

from cursos_app.models import Curso, Categoria, Favorito, Instrutor, Turma
from usuarios.models import Aluno, PerfilAluno
from usuarios.decorators import aluno_logado_e_centros

from blog.models import Post
from gestoreduka.models import (
    AreaFormacao, AnuncioCentro, Certificacao, CentroDeFormacao,
    CentroSeguimento, Depoimento, Diferencial, Equipe, Estatistica,
    Evento, Filial, Parceria, ReelCentro, Recurso,
)
from cursovideoapp.models import Curso_video, FavoritoCursoVideo, TurmaVideo
from estagio.models import Estagio

from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Galeria, SobreNos, MensagemContato, Publicidade
from avaliacoes.utils import get_centro_da_semana
from cursos_app.utils_secoes import get_home_sections_data


def recomendar_cursos(aluno, limite=8):
    """
    Fallback para recomendação de cursos caso o módulo de Inteligência Artificial esteja desativado.
    Retorna os cursos ativos mais recentes do portal.
    """
    try:
        from inteligencia.utils import recomendar_cursos as ai_recomendar
        return ai_recomendar(aluno, limite)
    except (ImportError, Exception):
        return list(Curso.objects.filter(publicado=True, ativo=True).select_related('centro').order_by('-id')[:limite])


from django.core.cache import cache

def index(request):
    """
    Página inicial do portal Edukangola com lógica de Landing Gate e cache inteligente.
    """
    # Redirecionar para onboarding se for aluno e não completou
    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            if not hasattr(aluno, 'perfil') or not aluno.perfil.onboarding_completo:
                return redirect('aluno_onboarding')
        except AttributeError:
            pass
        
    # Tentar obter dados globais do cache (seções que não mudam por user)
    cache_key = 'home_global_data_v4'
    global_data = cache.get(cache_key)
    
    if global_data is None:
        # 1. Catálogo real publicado e ativo
        cursos_publicados_qs = Curso.objects.filter(
            publicado=True, ativo=True
        ).select_related('centro', 'categoria')
        total_cursos_publicados = cursos_publicados_qs.count()
        cursos_destaque = list(cursos_publicados_qs.filter(destaque=True).prefetch_related('instrutores')[:10])
        cursos_populares = list(cursos_publicados_qs.annotate(
            num_inscricoes=Count('inscricoes', filter=Q(inscricoes__status='A'))
        ).order_by('-num_inscricoes', '-visualizacoes')[:6])
        cursos_recentes = list(cursos_publicados_qs.order_by('-data_criacao')[:6])
        cursos_vitrine = cursos_destaque or cursos_recentes
        cursos_tecnologia = list(cursos_publicados_qs.filter(
            Q(categoria__nome__icontains='Tecnologia') |
            Q(categoria__nome__icontains='Informática') |
            Q(categoria__nome__icontains='Programação')
        )[:6])
        cursos_idiomas = list(cursos_publicados_qs.filter(
            Q(categoria__nome__icontains='Língua') |
            Q(categoria__nome__icontains='Idioma') |
            Q(categoria__nome__icontains='Inglês') |
            Q(categoria__nome__icontains='Francês')
        )[:6])
        cursos_internacionais = list(cursos_publicados_qs.filter(
            centro__pais__isnull=False
        ).exclude(centro__pais='AO')[:6])

        # 2. Cursos de vídeo (Originais vs Parceiros)
        cursos_video_originais = list(Curso_video.objects.filter(centro__isnull=True, destaque=True).select_related('instrutor')[:5])
        cursos_video_parceiros = list(Curso_video.objects.filter(centro__isnull=False, destaque=True).select_related('centro', 'instrutor')[:5])
        
        # 3. Primeiro instrutor a dar curso em vídeo
        primeiro_instrutor_video = Instrutor.objects.filter(cursos_video__isnull=False).select_related('centro_de_formacao').first()

        # 4. Posts do blog
        posts = list(Post.objects.filter(status='publicado').select_related('categoria').prefetch_related('tags')[:3])

        # 5. Instrutores ativos
        instrutores = list(Instrutor.objects.filter(ativo=True).select_related('centro_de_formacao')[:12])

        # 6. Centros ativos (Otimizado)
        total_centros_ativos = CentroDeFormacao.objects.filter(ativo=True).count()
        centros = list(CentroDeFormacao.objects.filter(ativo=True).annotate(
            priority_home=Coalesce('assinatura__plano__destaque_home', Value(False))
        ).select_related('perfil', 'avaliacao_hibrida').order_by('-priority_home', 'nome')[:12])
        
        # 7. Centros para o Trilho de Destaques
        centros_destaque = list(CentroDeFormacao.objects.filter(
            ativo=True, 
            perfil__banner__isnull=False
        ).exclude(perfil__banner='').select_related('perfil').order_by('id')[:12])
        
        # 8. Galeria de imagens
        imagens = list(Galeria.objects.all()[:6])
        
        # 9. Primeiros alunos com foto
        primeiros_alunos = list(PerfilAluno.objects.filter(
            foto_de_perfil__isnull=False
        ).exclude(foto_de_perfil='').select_related('aluno').order_by('aluno__data_cadastro')[:3])
        
        # 10. Estágios ativos
        estagios = list(Estagio.objects.filter(ativo=True).select_related('area', 'centro_formacao')[:6])
        
        # 11. Centro da Semana
        centro_semana = get_centro_da_semana()

        # 12. Categorias principais. Mantemos a navegação completa, mas os cartões
        # editoriais devem mostrar apenas categorias com oferta real.
        categorias = list(Categoria.objects.annotate(
            num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
        ).order_by('-num_cursos', 'nome')[:10])
        categorias_com_cursos = [categoria for categoria in categorias if categoria.num_cursos > 0]

        # 13. Depoimentos
        depoimentos = list(Depoimento.objects.filter(aprovado=True).order_by('-data')[:8])

        global_data = {
            'cursos_destaque': cursos_destaque,
            'cursos_vitrine': cursos_vitrine,
            'cursos_populares': cursos_populares,
            'cursos_recentes': cursos_recentes,
            'cursos_tecnologia': cursos_tecnologia,
            'cursos_idiomas': cursos_idiomas,
            'cursos_internacionais': cursos_internacionais,
            'total_cursos_publicados': total_cursos_publicados,
            'total_centros_ativos': total_centros_ativos,
            'categorias_com_cursos': categorias_com_cursos,
            'cursos_video_originais': cursos_video_originais,
            'cursos_video_parceiros': cursos_video_parceiros,
            'primeiro_instrutor_video': primeiro_instrutor_video,
            'posts': posts,
            'instrutores': instrutores,
            'centros': centros,
            'centros_destaque': centros_destaque,
            'imagens': imagens,
            'primeiros_alunos': primeiros_alunos,
            'sobre': SobreNos.objects.last(),
            'estagios': estagios,
            'centro_semana': centro_semana,
            'categorias': categorias,
            'depoimentos': depoimentos,
            'publicidades': list(Publicidade.objects.filter(ativo=True).exclude(posicao='EMPRESAS')),
            'banner_empresas': Publicidade.objects.filter(ativo=True, posicao='EMPRESAS').first(),
        }
        cache.set(cache_key, global_data, 600) # 10 minutos

    # Secções Dinâmicas (Já possui cache interno em get_home_sections_data)
    secoes_dinamicas = get_home_sections_data()

    # Dados personalizados do Aluno (Não cacheáveis globalmente)
    cursos_recomendados = []
    aluno_nome = None
    favoritos = []
    favoritos_video = []
    centros_seguidos = []
    aluno_logado = False

    if request.user.is_authenticated and request.user.tipo_usuario == 'ALUNO':
        try:
            aluno = request.user.aluno_profile
            aluno_logado = True
            aluno_nome = aluno.nome
            
            # Recomendações IA
            cursos_recomendados = recomendar_cursos(aluno, limite=8)
            
            # Favoritos e Seguimentos
            favoritos = list(Favorito.objects.filter(aluno=aluno).values_list('curso_id', flat=True))
            favoritos_video = list(FavoritoCursoVideo.objects.filter(aluno=aluno).values_list('curso_id', flat=True))
            centros_seguidos = list(CentroSeguimento.objects.filter(aluno=aluno).values_list('centro_id', flat=True))
        except AttributeError:
            pass

    # Recuperar histórico de visualizações recentes
    viewed_cursos_ids = request.session.get('viewed_cursos', [])
    viewed_video_cursos_ids = request.session.get('viewed_video_cursos', [])
    viewed_centros_ids = request.session.get('viewed_centros', [])

    viewed_cursos = []
    if viewed_cursos_ids:
        # Recuperar e ordenar conforme a sessão (mais recente primeiro)
        cursos_dict = Curso.objects.in_bulk(viewed_cursos_ids)
        viewed_cursos = [cursos_dict[id] for id in viewed_cursos_ids if id in cursos_dict]
        
    viewed_video_cursos = []
    if viewed_video_cursos_ids:
        video_cursos_dict = Curso_video.objects.in_bulk(viewed_video_cursos_ids)
        viewed_video_cursos = [video_cursos_dict[id] for id in viewed_video_cursos_ids if id in video_cursos_dict]
        
    viewed_centros = []
    if viewed_centros_ids:
        centros_dict = CentroDeFormacao.objects.in_bulk(viewed_centros_ids)
        viewed_centros = [centros_dict[id] for id in viewed_centros_ids if id in centros_dict]
        
    show_recently_viewed = bool(viewed_cursos or viewed_video_cursos or viewed_centros)

    context = {
        **global_data,
        'viewed_cursos': viewed_cursos,
        'viewed_video_cursos': viewed_video_cursos,
        'viewed_centros': viewed_centros,
        'show_recently_viewed': show_recently_viewed,
        'secoes_dinamicas': secoes_dinamicas,
        'instrutores_lista': global_data['instrutores'],
        'cursos_recomendados': cursos_recomendados,
        'aluno_logado': aluno_logado,
        'aluno_nome': aluno_nome,
        'favoritos': favoritos,
        'favoritos_video': favoritos_video,
        'centros_seguidos': centros_seguidos,
        'DEBUG': settings.DEBUG,
    }

    return render(request, 'core/index.html', context)


def public_home_data(request):
    """Dados públicos, factuais e compactos para a index React da Eduka-Angola."""
    hoje = timezone.localdate()
    # A aplicação React expõe apenas formações presenciais de centros. As outras
    # modalidades continuam disponíveis para a gestão interna no GestorEduka,
    # sem serem devolvidas por esta API pública.
    cursos_qs = Curso.objects.filter(
        publicado=True,
        ativo=True,
        modalidade='PRESENCIAL',
    ).select_related('centro', 'categoria')

    def formatar_valor(valor):
        return f"{valor:,.0f} Kz".replace(',', ' ')

    def serializar_curso(curso):
        valor_inicial = curso.valor_a_cobrar_online()
        imagem_url = curso.get_imagem_url
        return {
            'id': curso.id,
            'titulo': curso.titulo,
            'categoria_id': curso.categoria_id,
            'categoria': curso.categoria.nome if curso.categoria else 'Sem categoria',
            'centro': curso.centro.nome or 'Centro de formação',
            'provincia': curso.centro.provincia or '',
            'cidade': curso.centro.cidade or '',
            'descricao_curta': curso.descricao_curta or '',
            'descricao': curso.descricao,
            'carga_horaria': curso.carga_horaria,
            'nivel': curso.nivel,
            'nivel_label': curso.get_nivel_display(),
            'idioma': curso.idioma,
            'idioma_label': curso.get_idioma_display(),
            'modalidade_codigo': curso.modalidade,
            'modalidade': curso.get_modalidade_display(),
            'is_gratuito': curso.is_gratuito,
            'certificado': curso.certificado,
            'destaque': curso.destaque,
            'imagem_url': imagem_url,
            'data_publicacao': curso.data_criacao.isoformat(),
            'detalhe_url': reverse('curso_detalhe', kwargs={'id': curso.id}),
            'inscricao_url': reverse('ficha_inscricao', kwargs={'curso_id': curso.id}),
            'pagamento': {
                'valor_inicial': float(valor_inicial),
                'agora': formatar_valor(valor_inicial) if valor_inicial > 0 else 'Sem pagamento no ato',
                'descricao': curso.descricao_cobranca_online(),
            },
        }

    turmas_qs = Turma.objects.filter(
        status='ABERTA',
        data_inicio__gte=hoje,
        vagas_disponiveis__gt=0,
        curso__publicado=True,
        curso__ativo=True,
    ).select_related('curso', 'curso__centro', 'curso__categoria', 'filial').order_by('data_inicio', 'horario_inicio')[:24]

    turmas = []
    for turma in turmas_qs:
        curso = serializar_curso(turma.curso)
        curso.update({
            'turma_id': turma.id,
            'turma_nome': turma.nome,
            'inicio': turma.data_inicio.isoformat(),
            'inicio_formatado': turma.data_inicio.strftime('%d/%m/%Y'),
            'turno': turma.get_turno_display(),
            'horario': turma.horario_formatado,
            'dias': turma.dias_semana_formatado,
            'vagas_disponiveis': turma.vagas_disponiveis,
            'local': turma.local or (turma.filial.nome if turma.filial else turma.curso.centro.nome),
            'sala': turma.sala or '',
        })
        turmas.append(curso)

    centros_qs = CentroDeFormacao.objects.filter(
        ativo=True,
        cursos__publicado=True,
        cursos__ativo=True,
    ).select_related('perfil').annotate(
        total_cursos_publicos=Count('cursos', filter=Q(cursos__publicado=True, cursos__ativo=True), distinct=True)
    ).order_by('-total_cursos_publicos', 'nome')[:8]

    centros = []
    for centro in centros_qs:
        perfil = getattr(centro, 'perfil', None)
        modalidades = list(cursos_qs.filter(centro=centro).values_list('modalidade', flat=True).distinct())
        centros.append({
            'id': centro.id,
            'nome': centro.nome or 'Centro de formação',
            'provincia': centro.provincia or '',
            'cidade': centro.cidade or '',
            'verificado': bool(perfil and perfil.verificado),
            'total_cursos': centro.total_cursos_publicos,
            'modalidades': [dict(Curso.MODALIDADE_CHOICES).get(item, item) for item in modalidades],
            'perfil_url': f'/centros/{centro.id}',
        })

    cursos = [serializar_curso(curso) for curso in cursos_qs.order_by('-data_criacao')[:24]]
    video_cursos = []
    for video in Curso_video.objects.select_related('instrutor', 'centro', 'categoria').prefetch_related('aulas', 'turmas').order_by('-data_publicacao')[:24]:
        preco = float(video.preco or 0)
        aceita_turmas = bool(video.centro_id and not video.is_original_edukangola)
        proxima_turma = video.turmas.filter(status='ABERTA', data_inicio__gte=hoje, vagas_disponiveis__gt=0).order_by('data_inicio').first() if aceita_turmas else None
        video_cursos.append({
            'id': f'video-{video.id}',
            'curso_video_id': video.id,
            'video_slug': video.slug,
            'is_video': True,
            'is_pago': video.is_pago,
            'is_original_edukangola': video.is_original_edukangola,
            'tem_turmas': aceita_turmas,
            'origem_label': 'Original Edukangola' if video.is_original_edukangola else 'Publicado por centro',
            'titulo': video.titulo,
            'categoria': video.categoria.nome if video.categoria else 'Sem categoria',
            'categoria_id': video.categoria_id,
            'centro': video.centro.nome if video.centro else 'Edukangola',
            'provincia': video.centro.provincia if video.centro else '',
            'cidade': video.centro.cidade if video.centro else '',
            'instrutor': video.instrutor.nome if video.instrutor else '',
            'descricao_curta': video.descricao[:220],
            'descricao': video.descricao,
            'modalidade_codigo': 'VIDEO',
            'modalidade': 'Curso em vídeo',
            'is_gratuito': video.is_gratuito,
            'certificado': False,
            'destaque': video.destaque,
            'imagem_url': video.get_imagem_url,
            'data_publicacao': video.data_publicacao.isoformat(),
            'detalhe_url': video.get_absolute_url(),
            'inscricao_url': reverse('cursovideoapp:toggle_inscricao', kwargs={'slug': video.slug}),
            'total_aulas': video.aulas.count(),
            'duracao_total': video.duracao_total() or '',
            'proxima_turma': {
                'id': proxima_turma.id,
                'nome': proxima_turma.nome,
                'inicio': proxima_turma.data_inicio.isoformat(),
                'inicio_formatado': proxima_turma.data_inicio.strftime('%d/%m/%Y'),
            } if proxima_turma else None,
            'pagamento': {
                'valor_inicial': preco,
                'agora': formatar_valor(preco) if preco > 0 else 'Sem pagamento no ato',
                'descricao': 'Acesso gratuito' if video.is_gratuito else 'Pagamento do vídeo-curso',
            },
        })
    provincias = sorted({curso['provincia'] for curso in cursos if curso['provincia']})

    return JsonResponse({
        'turmas_abertas': turmas,
        'cursos': cursos,
        'video_cursos': video_cursos,
        'provincias': provincias,
        'centros_destaque': centros,
        'atualizado_em': timezone.now().isoformat(),
    })


def public_center_profile(request, centro_id):
    """Perfil público de um centro para a experiência React da Edukangola."""
    centro = CentroDeFormacao.objects.filter(id=centro_id, ativo=True).select_related('perfil').first()
    if not centro:
        return JsonResponse({'detail': 'Centro de formação não encontrado.'}, status=404)

    perfil = getattr(centro, 'perfil', None)
    aluno = getattr(request.user, 'aluno_profile', None) if request.user.is_authenticated else None
    seguindo = bool(aluno and CentroSeguimento.objects.filter(aluno=aluno, centro=centro).exists())

    def arquivo_url(arquivo):
        try:
            return arquivo.url if arquivo else ''
        except (ValueError, AttributeError):
            return ''

    def formatar_valor(valor):
        return f"{valor:,.0f} Kz".replace(',', ' ')

    cursos_qs = centro.cursos.filter(
        publicado=True,
        ativo=True,
        modalidade='PRESENCIAL',
    ).select_related('categoria').order_by('-destaque', '-data_criacao')

    cursos = []
    for curso in cursos_qs[:12]:
        valor_inicial = curso.valor_a_cobrar_online()
        cursos.append({
            'id': curso.id,
            'titulo': curso.titulo,
            'categoria': curso.categoria.nome if curso.categoria else 'Formação profissional',
            'descricao_curta': curso.descricao_curta or curso.descricao or '',
            'imagem_url': curso.get_imagem_url,
            'nivel': curso.get_nivel_display(),
            'carga_horaria': curso.carga_horaria or '',
            'pagamento': {
                'agora': formatar_valor(valor_inicial) if valor_inicial > 0 else 'Sem pagamento no ato',
                'descricao': curso.descricao_cobranca_online(),
            },
        })

    formadores = []
    for formador in Instrutor.objects.filter(centro_de_formacao=centro, ativo=True).order_by('nome')[:8]:
        formadores.append({
            'id': formador.id,
            'nome': formador.nome,
            'titulo': formador.titulo or formador.get_area_especializacao_display(),
            'biografia': formador.biografia or '',
            'foto_url': arquivo_url(formador.foto),
        })

    galeria = []
    for imagem in centro.galeria_imagens.all().order_by('ordem', '-data_upload')[:8]:
        galeria.append({
            'id': imagem.id,
            'titulo': imagem.titulo or imagem.get_categoria_display(),
            'descricao': imagem.descricao or '',
            'categoria': imagem.get_categoria_display(),
            'imagem_url': arquivo_url(imagem.imagem),
        })

    certificacoes = [{
        'id': item.id, 'nome': item.nome, 'orgao_emissor': item.orgao_emissor,
        'descricao': item.descricao or '', 'logo_url': arquivo_url(item.logo),
    } for item in Certificacao.objects.filter(centro=centro)]
    diferenciais = [{
        'id': item.id, 'titulo': item.titulo, 'descricao': item.descricao, 'icone': item.icone or '',
    } for item in Diferencial.objects.filter(centro=centro)]
    areas_formacao = [{
        'id': item.id, 'nome': item.nome, 'descricao': item.descricao or '', 'icone': item.icone or '',
    } for item in AreaFormacao.objects.filter(centro=centro).order_by('ordem')]
    recursos = [{
        'id': item.id, 'nome': item.nome, 'descricao': item.descricao, 'icone': item.icone or '',
    } for item in Recurso.objects.filter(centro=centro)]
    equipa = [{
        'id': item.id, 'nome': item.nome, 'cargo': item.cargo, 'biografia': item.biografia or '',
        'formacao': item.formacao or '', 'experiencia': item.experiencia or '',
        'linkedin': item.linkedin or '', 'foto_url': arquivo_url(item.foto),
    } for item in Equipe.objects.filter(centro=centro).order_by('ordem')[:8]]
    depoimentos = [{
        'id': item.id, 'nome': item.nome, 'cargo': item.cargo or '', 'texto': item.texto,
        'nota': item.nota, 'foto_url': arquivo_url(item.foto),
    } for item in Depoimento.objects.filter(centro=centro, aprovado=True).order_by('-data')[:6]]
    estatisticas = [{
        'id': item.id, 'titulo': item.titulo, 'valor': item.valor, 'icone': item.icone or '',
    } for item in Estatistica.objects.filter(centro=centro).order_by('ordem')[:4]]
    anuncios = [{
        'id': item.id, 'titulo': item.titulo, 'conteudo': item.conteudo, 'importante': item.importante,
        'data_publicacao': item.data_publicacao.isoformat(), 'imagem_url': arquivo_url(item.imagem),
    } for item in AnuncioCentro.objects.filter(centro=centro, ativo=True).order_by('-data_publicacao')[:4]]
    eventos = [{
        'id': item.id, 'titulo': item.titulo, 'descricao': item.descricao, 'tipo': item.get_tipo_display(),
        'inicio': item.data_inicio.isoformat(),
        'inicio_formatado': timezone.localtime(item.data_inicio).strftime('%d/%m/%Y · %H:%M'),
        'local': item.local, 'link_inscricao': item.link_inscricao or '', 'imagem_url': arquivo_url(item.imagem),
    } for item in Evento.objects.filter(centro=centro, data_inicio__gte=timezone.now()).order_by('data_inicio')[:4]]
    reels = [{
        'id': item.id, 'titulo': item.titulo, 'descricao': item.descricao or '', 'video_url': arquivo_url(item.video),
        'thumbnail_url': arquivo_url(item.thumbnail), 'duracao': item.duracao,
        'visualizacoes': item.visualizacoes, 'curtidas': item.curtidas,
    } for item in ReelCentro.objects.filter(centro=centro, publico=True).order_by('-destaque', '-data_publicacao')[:6]]
    parcerias = [{
        'id': item.id, 'nome': item.nome_empresa, 'tipo': item.tipo_parceria, 'descricao': item.descricao or '',
        'localizacao': item.localizacao or '', 'website': item.website or '', 'logo_url': arquivo_url(item.logo),
    } for item in Parceria.objects.filter(centro=centro, ativa=True)[:8]]
    filiais = [{
        'id': item.id, 'nome': item.nome, 'endereco': item.endereco, 'telefone': item.telefone or '',
        'email': item.email or '', 'whatsapp': item.whatsapp or '',
    } for item in Filial.objects.filter(centro_principal=centro, ativo=True)]
    estagios = [{
        'id': item.id, 'titulo': item.titulo, 'slug': item.slug, 'resumo': item.resumo,
        'area': item.area.nome if item.area else '', 'modalidade': item.get_modalidade_display(),
        'vagas_restantes': item.vagas_restantes, 'data_limite': item.data_limite_inscricao.strftime('%d/%m/%Y'),
        'imagem_url': arquivo_url(item.imagem_principal),
    } for item in Estagio.objects.filter(
        centro_formacao=centro, ativo=True, vagas_disponiveis__gt=0,
        data_limite_inscricao__gte=timezone.localdate(),
    ).select_related('area').order_by('-destaque', 'data_limite_inscricao')[:6]]
    cursos_video = [{
        'id': item.id, 'slug': item.slug, 'titulo': item.titulo, 'descricao': item.descricao or '',
        'categoria': item.categoria.nome if item.categoria else 'Vídeo-curso', 'imagem_url': item.get_imagem_url,
        'total_aulas': item.aulas.count(), 'preco': formatar_valor(item.preco) if item.preco else 'Acesso gratuito',
    } for item in Curso_video.objects.filter(centro=centro).select_related('categoria').prefetch_related('aulas').order_by('-data_publicacao')[:8]]

    categorias = list(dict.fromkeys(cursos_qs.values_list('categoria__nome', flat=True)))
    localizacao = ', '.join(item for item in [centro.cidade, centro.provincia] if item)
    sociais = {
        'facebook': perfil.facebook if perfil else '',
        'instagram': perfil.instagram if perfil else '',
        'linkedin': perfil.linkedin if perfil else '',
        'youtube': perfil.youtube if perfil else '',
        'tiktok': perfil.tiktok if perfil else '',
    }

    return JsonResponse({
        'id': centro.id,
        'nome': centro.nome or 'Centro de formação',
        'verificado': bool(perfil and perfil.verificado),
        'logo_url': arquivo_url(perfil.imagem) if perfil else '',
        'banner_url': arquivo_url(perfil.banner) if perfil else '',
        'descricao': (perfil.descricao if perfil else '') or '',
        'missao': (perfil.missao if perfil else '') or '',
        'visao': (perfil.visao if perfil else '') or '',
        'valores': (perfil.valores if perfil else '') or '',
        'ano_fundacao': perfil.ano_fundacao if perfil else None,
        'tipo': (perfil.tipo if perfil else '') or '',
        'modalidade': (perfil.modalidade if perfil else '') or '',
        'localizacao': localizacao,
        'endereco': centro.endereco or '',
        'telefone': centro.telefone or '',
        'email': centro.email or '',
        'site': centro.site or '',
        'whatsapp': (perfil.whatsapp if perfil else '') or '',
        'horario_funcionamento': (perfil.horario_funcionamento if perfil else '') or '',
        'video_apresentacao_url': arquivo_url(perfil.video_apresentacao) if perfil else '',
        'sociais': {chave: valor for chave, valor in sociais.items() if valor},
        'seguimento': {
            'autenticado': bool(aluno),
            'seguindo': seguindo,
            'total_seguidores': centro.seguidores.count(),
        },
        'total_cursos': cursos_qs.count(),
        'categorias': [categoria for categoria in categorias if categoria],
        'cursos': cursos,
        'formadores': formadores,
        'galeria': galeria,
        'certificacoes': certificacoes,
        'diferenciais': diferenciais,
        'areas_formacao': areas_formacao,
        'recursos': recursos,
        'equipa': equipa,
        'depoimentos': depoimentos,
        'estatisticas': estatisticas,
        'anuncios': anuncios,
        'eventos': eventos,
        'reels': reels,
        'parcerias': parcerias,
        'filiais': filiais,
        'estagios': estagios,
        'cursos_video': cursos_video,
    })


def public_video_course_detail(request, slug):
    """Currículo público de um vídeo-curso, com aulas reais sem expor URLs privadas."""
    curso = Curso_video.objects.select_related('instrutor', 'centro', 'categoria').prefetch_related('aulas', 'turmas').filter(slug=slug).first()
    if not curso:
        return JsonResponse({'detail': 'Vídeo-curso não encontrado.'}, status=404)

    aulas = []
    for aula in curso.aulas.all().order_by('ordem', 'id'):
        aulas.append({
            'id': aula.id,
            'ordem': aula.ordem,
            'titulo': aula.titulo,
            'descricao': aula.descricao or '',
            'duracao': aula.duracao_formatada(),
            'tem_exercicio': hasattr(aula, 'exercicio'),
        })

    preco = float(curso.preco or 0)
    aceita_turmas = bool(curso.centro_id and not curso.is_original_edukangola)
    turmas = []
    if aceita_turmas:
        for turma in curso.turmas.filter(status='ABERTA', data_inicio__gte=timezone.localdate(), vagas_disponiveis__gt=0).order_by('data_inicio'):
            turmas.append({
                'id': turma.id,
                'nome': turma.nome,
                'inicio_formatado': turma.data_inicio.strftime('%d/%m/%Y'),
                'dias': turma.dias_semana or 'Dias a confirmar',
                'horario': turma.horario_formatado(),
                'vagas_disponiveis': turma.vagas_disponiveis,
            })
    return JsonResponse({
        'id': curso.id,
        'slug': curso.slug,
        'is_video': True,
        'is_pago': curso.is_pago,
        'is_gratuito': curso.is_gratuito,
        'is_original_edukangola': curso.is_original_edukangola,
        'tem_turmas': aceita_turmas,
        'origem_label': 'Original Edukangola' if curso.is_original_edukangola else 'Publicado por centro',
        'titulo': curso.titulo,
        'descricao': curso.descricao,
        'categoria': curso.categoria.nome if curso.categoria else 'Sem categoria',
        'imagem_url': curso.get_imagem_url,
        'instrutor': curso.instrutor.nome if curso.instrutor else '',
        'centro': curso.centro.nome if curso.centro else 'Edukangola',
        'total_aulas': len(aulas),
        'duracao_total': curso.duracao_total() or '',
        'detalhe_url': curso.get_absolute_url(),
        'inscricao_url': reverse('cursovideoapp:toggle_inscricao', kwargs={'slug': curso.slug}),
        'pagamento': {
            'valor_inicial': preco,
            'agora': f'{preco:,.0f} Kz'.replace(',', ' ') if preco > 0 else 'Sem pagamento no ato',
            'descricao': 'Acesso gratuito' if curso.is_gratuito else 'Pagamento do vídeo-curso',
        },
        'aulas': aulas,
        'turmas': turmas,
    })


def offline_view(request):
    """
    Renderiza a página offline quando o utilizador perde a ligação à Internet.
    O Service Worker irá servir esta página a partir do cache.
    """
    return render(request, 'core/offline.html')




#-------------------------fim homes-----------------------------------------


def erro_404_view(request, exception):
    """
    Exibe uma página personalizada para erros 404 (Página não encontrada).
    """
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

    return render(request, '404.html', context, status=404)

def erro_500_view(request):
    """
    Página de erro genérica para falhas internas do servidor (Erro 500).
    """
    """
    Custom 500 error handler.
    """
    context = {}
    return render(request, '500.html', context, status=500)


def sobre(request):
    """
    Apresenta informações sobre a plataforma Edukangola e sua missão, incluindo depoimentos dinâmicos.
    """
    imagens = Galeria.objects.all()[:6]
    sobre_nos = SobreNos.objects.last()
    depoimentos = Depoimento.objects.filter(aprovado=True).order_by('-data')

    context = {
        'aluno_logado': False,
        'imagens': imagens,
        'sobre': sobre_nos,
        'depoimentos': depoimentos,
        'instrutores': Instrutor.objects.filter(ativo=True),
        'centros': CentroDeFormacao.objects.filter(ativo=True).exclude(perfil__imagem='').select_related('perfil'),
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

    return render(request, 'core/sobre.html', context)


def privacidade(request):
    """
    Página com os termos de privacidade e uso dos dados dos usuários.
    """
    imagens = Galeria.objects.all()[:6]

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

    return render(request, 'core/privacidade.html', context)


def contato(request):
    """
    Página de contacto funcional. 
    Lida com a exibição de informações e processamento do formulário.
    """
    sobre = SobreNos.objects.last()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        assunto = request.POST.get('assunto')
        mensagem_texto = request.POST.get('mensagem')
        
        # 1. Salvar na Base de Dados
        MensagemContato.objects.create(
            nome=nome,
            email=email,
            assunto=assunto,
            mensagem=mensagem_texto
        )
        
        # 2. Enviar Notificação por E-mail
        logo_url = request.build_absolute_uri(settings.STATIC_URL + 'assets/images/logo/Eduka-removebg-preview.png')
        
        context_email = {
            'nome': nome,
            'email': email,
            'assunto': assunto,
            'mensagem': mensagem_texto,
            'logo_url': logo_url,
            'empresa_nome': "Eduka-Angola",
            'endereco': sobre.endereco if sobre else "Luanda, Angola",
            'telefone': sobre.telefone if sobre else "+244 923 908 353",
            'email_contato': sobre.email_contato if sobre else settings.EMAIL_HOST_USER,
            'site_url': request.build_absolute_uri('/'),
        }
        
        html_message = render_to_string('core/emails/contato_notificacao.html', context_email)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=f"Eduka-Angola: {assunto}",
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(request, "Sua mensagem foi enviada com sucesso! Entraremos em contacto em breve.")
        except Exception as e:
            messages.warning(request, "Sua mensagem foi registada, mas houve um problema ao enviar a notificação. Mas não se preocupe, nós a leremos no sistema!")
            
        return redirect('contato')

    context = {
        'aluno_logado': False,
        'sobre': sobre,
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

    return render(request, 'core/contato.html', context)


def faq(request):
    """
    Página de Perguntas Frequentes (FAQ).
    """
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

    return render(request, 'core/faq.html', context)


def pagamento_sucesso(request):
    """
    Página de sucesso do pagamento.
    """
    context = {
        'aluno_logado': False,
        'referencia': request.GET.get('reference', 'N/A'),
        'transaction_id': request.GET.get('transaction_id', 'N/A'),
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
            
    return render(request, 'core/pagamento_sucesso.html', context)


def pagamento_cancelado(request):
    """
    Página de cancelamento do pagamento.
    """
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
            
            pass
            
    return render(request, 'core/pagamento_cancelado.html', context)


def fundo_bolsas(request):
    """
    Página do Fundo de Bolsas de Estudo e Oportunidades do EdukAngola.
    Exibe os patrocinadores e programas de bolsas ativos sem filtro lateral e sem lista de cursos.
    """
    from bolsas.models import Patrocinador, Bolsa

    patrocinadores = Patrocinador.objects.filter(ativo=True)
    bolsas_ativas = Bolsa.objects.filter(status='ATIVA').select_related('patrocinador', 'aluno', 'curso')

    context = {
        'aluno_logado': False,
        'patrocinadores': patrocinadores,
        'bolsas_ativas': bolsas_ativas,
        'total_bolsas': bolsas_ativas.count(),
        'total_patrocinadores': patrocinadores.count(),
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

    return render(request, 'core/fundo_bolsas.html', context)


import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pagamentos.models import Pagamento
from django.db.models import Sum
from django.db.models.functions import TruncMonth

def dashboard_callback(request, context):
    """
    Callback nativo do Django Unfold para injetar cartões de métricas (KPIs) nativos e estatísticas geradas via Matplotlib.
    """
    total_alunos = Aluno.objects.count()
    total_centros = CentroDeFormacao.objects.filter(ativo=True).count()
    total_cursos = Curso.objects.filter(publicado=True, ativo=True).count()
    
    receita_dict = Pagamento.objects.filter(status='CONCLUIDO').aggregate(total=Sum('valor'))
    receita_total = receita_dict['total'] or 0

    # Gerar Gráfico via Matplotlib (Python Pure Data Science)
    vendas_mensais = (
        Pagamento.objects.filter(status='CONCLUIDO')
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total=Sum('valor'))
        .order_by('-mes')[:6]
    )

    labels = [item['mes'].strftime('%b/%Y') if item['mes'] else 'Atual' for item in reversed(list(vendas_mensais))]
    valores = [float(item['total'] or 0) for item in reversed(list(vendas_mensais))]

    if not labels or len(labels) == 0:
        labels = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"]
        valores = [150000, 320000, 450000, 600000, 850000, 1200000]

    # Renderizar Figura Matplotlib
    fig, ax = plt.subplots(figsize=(7, 3.2), dpi=120)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    bars = ax.bar(labels, [v / 1000 for v in valores], color='#2f57ef', width=0.45, edgecolor='none')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.0f}k Kz',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),  # 4 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold', color='#2f57ef')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cbd5e1')
    ax.spines['bottom'].set_color('#cbd5e1')
    ax.tick_params(axis='x', colors='#64748b', labelsize=9)
    ax.tick_params(axis='y', colors='#64748b', labelsize=8)
    ax.set_ylabel('Milhares (Kz)', fontsize=9, color='#64748b')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    chart_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    context.update({
        "kpi": [
            {
                "title": "Total de Estudantes",
                "metric": f"{total_alunos:,}",
                "footer": "Alunos registados na plataforma",
            },
            {
                "title": "Centros de Formação",
                "metric": f"{total_centros:,}",
                "footer": "Instituições ativas credenciadas",
            },
            {
                "title": "Cursos Publicados",
                "metric": f"{total_cursos:,}",
                "footer": "Formações presenciais e vídeo-cursos",
            },
            {
                "title": "Faturação Processada",
                "metric": f"{receita_total:,.0f} Kz",
                "footer": "Pagamentos concluídos via Multicaixa",
            },
        ],
        "chart_python": chart_image_base64,
    })
    return context
