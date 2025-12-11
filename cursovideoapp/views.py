from django.shortcuts import render, get_object_or_404
from .models import Curso_video, Aula

def lista_cursos(request):
    cursos = Curso_video.objects.all()
    return render(request, "cursos/lista.html", {"cursos": cursos})

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Curso_video, Aula, ProgressoAula, Aluno

# views.py
def detalhe_curso(request, slug):
    curso = get_object_or_404(Curso_video, slug=slug)
    aulas = curso.aulas.all().order_by('ordem')
    
    # Obter cursos recomendados (excluindo o curso atual)
    cursos_recomendados = Curso_video.objects.exclude(id=curso.id)[:10]
    
    # Verificar se o aluno está logado
    aluno_logado = False
    aluno_inscrito = False
    progresso_geral = 0
    
    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            aluno_logado = True
            
            aluno_inscrito = curso.inscritos.filter(id=aluno.id).exists()
            
            # Calcular progresso geral do aluno no curso
            if aulas.exists():
                aulas_concluidas = ProgressoAula.objects.filter(
                    aluno=aluno, 
                    aula__in=aulas, 
                    concluida=True
                ).count()
                progresso_geral = int((aulas_concluidas / aulas.count()) * 100) if aulas.count() > 0 else 0
                
        except Aluno.DoesNotExist:
            pass
    
    total_visualizacoes = sum(aula.visualizacoes for aula in aulas) if aulas.exists() else 0
    
    return render(request, "cursos/detalhe.html", {
        "curso": curso,
        "aulas": aulas,
        "aluno_logado": aluno_logado,
        "aluno_inscrito": aluno_inscrito,
        "progresso_geral": progresso_geral,
        "total_visualizacoes": total_visualizacoes,
        "cursos_recomendados": cursos_recomendados
    })

    
@require_POST
def toggle_inscricao(request, slug):
    if 'aluno' not in request.session:
        return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
    
    try:
        aluno = Aluno.objects.get(id=request.session['aluno'])
    except Aluno.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado'}, status=401)
    
    curso = get_object_or_404(Curso_video, slug=slug)
    
    if curso.inscritos.filter(id=aluno.id).exists():
        curso.inscritos.remove(aluno)
        inscrito = False
    else:
        curso.inscritos.add(aluno)
        inscrito = True
    
    return JsonResponse({
        'inscrito': inscrito,
        'total_inscritos': curso.total_inscritos()
    })


from django.http import HttpResponseForbidden

def ver_aula(request, curso_slug, pk):
    curso = get_object_or_404(Curso_video, slug=curso_slug)
    aula = get_object_or_404(Aula, pk=pk, curso=curso)
    
    # Verificar se o aluno tem acesso a esta aula
    if not verificar_acesso_aula(request, aula):
        return HttpResponseForbidden("Você precisa completar a aula anterior primeiro.")
    
    # Registrar visualização
    aula.visualizacoes += 1
    aula.save()
    
    # Obter todas as aulas do curso
    aulas = curso.aulas.all().order_by('ordem')
    
    # Preparar informações de progresso e acesso
    progresso = None
    aulas_info = []
    
    if 'aluno' in request.session:
        try:
            aluno = Aluno.objects.get(id=request.session['aluno'])
            progresso, created = ProgressoAula.objects.get_or_create(
                aluno=aluno,
                aula=aula
            )
            
            # Preparar informações de acesso para todas as aulas
            for aula_item in aulas:
                aula_liberada = verificar_acesso_aula(request, aula_item)
                progresso_aula = ProgressoAula.objects.filter(
                    aluno=aluno,
                    aula=aula_item
                ).first()
                
                aulas_info.append({
                    'aula': aula_item,
                    'liberada': aula_liberada,
                    'concluida': progresso_aula.concluida if progresso_aula else False,
                    'progresso': progresso_aula.progresso_percentual() if progresso_aula else 0
                })
                
        except Aluno.DoesNotExist:
            # Se não encontrar o aluno, criar informações básicas
            for aula_item in aulas:
                aulas_info.append({
                    'aula': aula_item,
                    'liberada': aula_item.ordem == 1,  # Só a primeira aula liberada
                    'concluida': False,
                    'progresso': 0
                })
    else:
        # Usuário não logado - só a primeira aula liberada
        for aula_item in aulas:
            aulas_info.append({
                'aula': aula_item,
                'liberada': aula_item.ordem == 1,
                'concluida': False,
                'progresso': 0
            })
    
    return render(request, "cursos/assistir.html", {
        "curso": curso,
        "aula": aula,
        "aulas_info": aulas_info,
        "progresso": progresso
    })

def verificar_acesso_aula(request, aula):
    """Verifica se o aluno tem acesso à aula baseado no progresso"""
    # Se a aula não requer conclusão anterior, liberar acesso
    if not aula.requer_conclusao_anterior:
        return True
    
    # Se o usuário não está logado, não pode acessar aulas que requerem progresso
    if 'aluno' not in request.session:
        return False
    
    try:
        aluno = Aluno.objects.get(id=request.session['aluno'])
    except Aluno.DoesNotExist:
        return False
    
    # Se é a primeira aula, liberar acesso
    if aula.ordem == 1:
        return True
    
    # Buscar a aula anterior
    aula_anterior = Aula.objects.filter(
        curso=aula.curso, 
        ordem=aula.ordem - 1
    ).first()
    
    if not aula_anterior:
        return True
    
    try:
        progresso_anterior = ProgressoAula.objects.get(
            aluno=aluno,
            aula=aula_anterior
        )
        return progresso_anterior.concluida
    except ProgressoAula.DoesNotExist:
        return False

@require_POST
def atualizar_progresso(request, aula_id):
    # Verificar se o aluno está logado
    if 'aluno' not in request.session:
        return JsonResponse({'error': 'Usuário não autenticado'}, status=401)
    
    try:
        aluno = Aluno.objects.get(id=request.session['aluno'])
    except Aluno.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado'}, status=401)
    
    aula = get_object_or_404(Aula, pk=aula_id)
    tempo_assistido = request.POST.get('tempo_assistido', 0)
    concluida = request.POST.get('concluida', False) == 'true'
    
    progresso, created = ProgressoAula.objects.get_or_create(
        aluno=aluno,
        aula=aula
    )
    
    progresso.tempo_assistido = int(float(tempo_assistido))
    if concluida:
        progresso.concluida = True
    progresso.save()
    
    return JsonResponse({
        'success': True,
        'progresso_percentual': progresso.progresso_percentual()
    })

    


