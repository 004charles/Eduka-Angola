from datetime import timedelta

from django.conf import settings
from django.shortcuts import render, redirect
from django.db.models import Count, Q, Prefetch, Value, F
from django.db.models.functions import Coalesce
from django.utils import timezone

from cursos_app.models import Curso, Categoria, Favorito, Instrutor
from usuarios.models import Aluno, PerfilAluno
from usuarios.decorators import aluno_logado_e_centros

from blog.models import Post
from gestoreduka.models import CentroDeFormacao, CentroSeguimento, Depoimento
from cursovideoapp.models import Curso_video, FavoritoCursoVideo
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
    cache_key = 'home_global_data_v3'
    global_data = cache.get(cache_key)
    
    if global_data is None:
        # 1. Cursos em destaque
        cursos_destaque = list(Curso.objects.filter(
            destaque=True, publicado=True, ativo=True
        ).select_related('centro').prefetch_related('instrutores')[:10])

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
        centros = list(CentroDeFormacao.objects.filter(ativo=True).annotate(
            priority_home=Coalesce('assinatura__plano__destaque_home', Value(False))
        ).select_related('perfil').order_by('-priority_home', 'nome')[:12])
        
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

        # 12. Categorias principais
        categorias = list(Categoria.objects.annotate(
            num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
        ).order_by('-num_cursos')[:10])

        # 13. Depoimentos
        depoimentos = list(Depoimento.objects.filter(aprovado=True).order_by('-data')[:8])

        global_data = {
            'cursos_destaque': cursos_destaque,
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
            'publicidades': list(Publicidade.objects.filter(ativo=True)),
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
