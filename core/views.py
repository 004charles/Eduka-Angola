from django.shortcuts import render, redirect
from cursos_app.models import Curso, Categoria, Aluno
from django.conf import settings
from django.shortcuts import redirect
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q

def index(request):
    agora = timezone.now()
    proximos_dias = agora + timedelta(days=7)

    # Cursos em destaque
    cursos_destaque = Curso.objects.filter(
        destaque=True,
        publicado=True,
        ativo=True
    ).select_related('centro').prefetch_related('instrutores')

    # Cursos mais recentes (usado para o zigue-zague)
    cursos_recentes = list(
        Curso.objects.filter(
            publicado=True,
            ativo=True
        ).order_by('-data_inicio')[:20]
    )

    todos_cursos = Curso.objects.filter(
        publicado=True,
        ativo=True
    ).order_by('-data_inicio')

    cursos_zigue1 = todos_cursos[::2]  # cursos nas posições pares
    cursos_zigue2 = todos_cursos[1::2]  # cursos nas posições ímpares

    # Cursos gratuitos
    cursos_gratuitos = Curso.objects.filter(
        preco=0,
        publicado=True,
        ativo=True
    ).order_by('-data_inicio')[:10]

    # Cursos com início nos próximos dias
    cursos_proximos = Curso.objects.filter(
        publicado=True,
        ativo=True,
        data_inicio__gte=agora,
        data_inicio__lte=proximos_dias
    ).order_by('data_inicio')

    # Categorias com contagem de cursos ativos/publicados
    categorias = Categoria.objects.annotate(
        num_cursos=Count('curso', filter=Q(curso__publicado=True, curso__ativo=True))
    )

    # Contexto para o template
    context = {
        'cursos_destaque': cursos_destaque,
        'cursos_recentes': cursos_recentes,
        'cursos_gratuitos': cursos_gratuitos,
        'cursos_proximos': cursos_proximos,
        'cursos_zigue1': cursos_zigue1,
        'cursos_zigue2': cursos_zigue2,
        'categoria': categorias,
        'DEBUG': settings.DEBUG,
        'aluno_logado': False,
    }

    # Verificar se o aluno está logado
    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            context.update({
                'aluno_logado': True,
                'aluno_nome': aluno.nome,
            })
        except Aluno.DoesNotExist:
            pass

    return render(request, 'core/index.html', context)
    
def erro_404_view(request, exception):
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

    return render(request, '404.html', context, status=404)


