from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import Http404
from .forms import EscolaAdminForm, PerfilEscolaAdminForm
from .models import Escola, CursoEnsinoMedio, PerfilEscola, RepresentanteEscola, GaleriaEscola, ParceriaEscola
# from inteligencia.ai_utils import orientacao_escolar_ia

def onboarding_escolar(request):
    """
    Formulário/Wizard inicial para quem não sabe qual escola escolher.
    """
    if request.method == 'POST':
        # Capturar dados do form
        gostos = request.POST.get('gostos', '')
        notas = request.POST.get('notas', '')
        provincia = request.POST.get('provincia', 'Luanda')
        orcamento = request.POST.get('orcamento', 'Pública')
        nivel = request.POST.get('nivel', '9_classe')

        perfil_dict = {
            'nivel': nivel,
            'gostos': gostos,
            'notas': notas,
            'provincia': provincia,
            'orcamento': orcamento
        }

        # Listar os cursos disponíveis naquela província para contextualizar a IA
        cursos_disponiveis = CursoEnsinoMedio.objects.filter(escola__provincia__icontains=provincia).values_list('nome', flat=True).distinct()
        cursos_str = ", ".join(list(cursos_disponiveis)[:20]) if cursos_disponiveis else "Diversos cursos do Ensino Médio"

        # Chamar a Eduka AI
        resultado_ia = orientacao_escolar_ia(perfil_dict, cursos_str)

        # Salvar na sessão para a página de resultados
        request.session['resultado_orientacao_escolar'] = resultado_ia
        request.session['orientacao_provincia'] = provincia
        
        return redirect('escolas:resultado_orientacao')

    return render(request, 'escolas/onboarding.html')


def resultado_orientacao(request):
    """
    Mostra o veredito da IA e as escolas recomendadas na base de dados.
    """
    resultado_ia = request.session.get('resultado_orientacao_escolar')
    provincia = request.session.get('orientacao_provincia', '')

    if not resultado_ia:
        return redirect('escolas:onboarding_escolar')

    keywords = resultado_ia.get('keywords', [])
    
    # Query inteligente: Escolas na província que oferecem cursos correspondentes às keywords
    query = Q()
    for kw in keywords:
        query |= Q(cursos__nome__icontains=kw)

    escolas_recomendadas = Escola.objects.filter(ativa=True, provincia__icontains=provincia).filter(query).distinct()[:6]

    # Se a IA sugerir algo que não temos, mostramos as melhores da província de qualquer forma
    if not escolas_recomendadas.exists():
        escolas_recomendadas = Escola.objects.filter(ativa=True, provincia__icontains=provincia).distinct()[:6]

    context = {
        'ia': resultado_ia,
        'escolas': escolas_recomendadas,
        'provincia': provincia
    }
    return render(request, 'escolas/resultado_ia.html', context)


def lista_escolas(request):
    """
    Diretório geral de escolas.
    """
    escolas = Escola.objects.filter(ativa=True).prefetch_related('cursos', 'perfil')
    
    # Simples busca
    q = request.GET.get('q')
    if q:
        escolas = escolas.filter(Q(nome__icontains=q) | Q(municipio__icontains=q) | Q(cursos__nome__icontains=q)).distinct()

    context = {
        'escolas': escolas
    }
    return render(request, 'escolas/lista_escolas.html', context)


@staff_member_required
def admin_escolas(request):
    """
    Painel administrativo para gerenciar escolas.
    """
    escolas = Escola.objects.all().prefetch_related('cursos', 'perfil')
    q = request.GET.get('q')
    if q:
        escolas = escolas.filter(
            Q(nome__icontains=q) | Q(municipio__icontains=q) | Q(provincia__icontains=q)
        ).distinct()

    return render(request, 'escolas/admin/list.html', {'escolas': escolas})


@staff_member_required
def admin_criar_escola(request):
    escola = None
    if request.method == 'POST':
        form = EscolaAdminForm(request.POST)
        profile_form = PerfilEscolaAdminForm(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            escola = form.save()
            perfil = profile_form.save(commit=False)
            perfil.escola = escola
            perfil.save()
            profile_form.save_m2m()
            messages.success(request, 'Escola criada com sucesso.')
            return redirect('admin_escolas')
    else:
        form = EscolaAdminForm()
        profile_form = PerfilEscolaAdminForm()

    return render(request, 'escolas/admin/form.html', {
        'form': form,
        'profile_form': profile_form,
        'escola': escola,
    })


@staff_member_required
def admin_editar_escola(request, pk):
    escola = get_object_or_404(Escola, pk=pk)
    perfil = getattr(escola, 'perfil', None)
    if not perfil:
        perfil = PerfilEscola(escola=escola)

    if request.method == 'POST':
        form = EscolaAdminForm(request.POST, instance=escola)
        profile_form = PerfilEscolaAdminForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            perfil = profile_form.save(commit=False)
            perfil.escola = escola
            perfil.save()
            profile_form.save_m2m()
            messages.success(request, 'Escola atualizada com sucesso.')
            return redirect('admin_editar_escola', pk=escola.pk)
    else:
        form = EscolaAdminForm(instance=escola)
        profile_form = PerfilEscolaAdminForm(instance=perfil)

    return render(request, 'escolas/admin/form.html', {
        'form': form,
        'profile_form': profile_form,
        'escola': escola,
    })


def perfil_escola(request, pk):
    """
    Página pública com o perfil completo da escola.
    """
    escola = get_object_or_404(Escola.objects.prefetch_related('cursos', 'galeria', 'perfil'), pk=pk, ativa=True)
    return render(request, 'escolas/perfil_escola.html', {'escola': escola})


# ========== REPRESENTANTE ESCOLAR VIEWS ==========

def _check_representante(user, escola):
    """Helper para verificar se o usuário é representante da escola"""
    if not user.is_authenticated:
        return False
    
    representante = RepresentanteEscola.objects.filter(
        user=user, 
        escola=escola, 
        ativo=True
    ).exists()
    
    return representante or user.is_staff


@login_required
def dashboard_representante(request, escola_id=None):
    """
    Dashboard principal do representante da escola.
    Se não especificar escola_id, mostra a primeira escola do representante.
    """
    # Obter escolas do representante
    escolas = Escola.objects.filter(
        representantes__user=request.user,
        representantes__ativo=True
    ).distinct()
    
    if not escolas.exists():
        messages.error(request, 'Você não é representante de nenhuma escola.')
        return redirect('escolas:lista_escolas')
    
    # Definir escola atual
    if escola_id:
        escola = get_object_or_404(escolas, pk=escola_id)
    else:
        escola = escolas.first()
    
    # Obter dados relacionados
    cursos_count = escola.cursos.count()
    galeria_count = school_galeria_count = escola.galeria.count()
    parcerias_count = escola.parcerias.count()
    galeria_imagens = escola.galeria.all().order_by('-data_upload')[:10]
    
    context = {
        'escola': escola,
        'escolas': escolas,
        'cursos_count': cursos_count,
        'galeria_count': galeria_count,
        'parcerias_count': parcerias_count,
        'galeria_imagens': galeria_imagens,
    }
    
    return render(request, 'escolas/admin/dashboard.html', context)


@login_required
def editar_info_escola(request, escola_id):
    """
    Editar informações básicas da escola (Escola model).
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        form = EscolaAdminForm(request.POST, instance=escola)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações da escola atualizadas com sucesso!')
            return redirect('escolas:dashboard_representante_escola', escola_id=escola.id)
    else:
        form = EscolaAdminForm(instance=escola)
    
    context = {
        'form': form,
        'escola': escola,
        'title': f'Editar Informações - {escola.nome}',
    }
    
    return render(request, 'escolas/admin/escola_form.html', context)


@login_required
def editar_perfil_escola(request, escola_id):
    """
    Editar perfil da escola (PerfilEscola model - branding, missão, visão, etc).
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    # Obter ou criar PerfilEscola
    perfil, created = PerfilEscola.objects.get_or_create(escola=escola)
    
    if request.method == 'POST':
        form = PerfilEscolaAdminForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil da escola atualizado com sucesso!')
            return redirect('escolas:dashboard_representante_escola', escola_id=escola.id)
    else:
        form = PerfilEscolaAdminForm(instance=perfil)
    
    context = {
        'form': form,
        'escola': escola,
        'perfil': perfil,
        'title': f'Editar Perfil - {escola.nome}',
    }
    
    return render(request, 'escolas/admin/perfil_form.html', context)


@login_required
def gerenciar_cursos(request, escola_id):
    """
    Listar todos os cursos da escola.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    cursos = escola.cursos.all()
    
    context = {
        'escola': escola,
        'cursos': cursos,
        'title': f'Gerenciar Cursos - {escola.nome}',
    }
    
    return render(request, 'escolas/admin/cursos_list.html', context)


@login_required
def adicionar_curso(request, escola_id):
    """
    Adicionar novo curso à escola.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        classes_lecionadas = request.POST.get('classes_lecionadas')
        duracao_anos = request.POST.get('duracao_anos')
        periodos = request.POST.get('periodos')
        exige_exame = request.POST.get('exige_exame') == 'on'
        disciplinas_exame = request.POST.get('disciplinas_exame')
        vagas_anuais = request.POST.get('vagas_anuais', 0)
        mensalidade = request.POST.get('mensalidade', 0)
        taxa_inscricao = request.POST.get('taxa_inscricao', 0)
        
        curso = CursoEnsinoMedio(
            escola=escola,
            nome=nome,
            descricao=descricao,
            classes_lecionadas=classes_lecionadas,
            duracao_anos=duracao_anos,
            periodos=periodos,
            exige_exame=exige_exame,
            disciplinas_exame=disciplinas_exame,
            vagas_anuais=int(vagas_anuais) if vagas_anuais else 0,
            mensalidade=float(mensalidade) if mensalidade else 0,
            taxa_inscricao=float(taxa_inscricao) if taxa_inscricao else 0,
        )
        curso.save()
        messages.success(request, f'Curso "{nome}" adicionado com sucesso!')
        return redirect('escolas:gerenciar_cursos', escola_id=escola.id)
    
    context = {
        'escola': escola,
        'title': f'Adicionar Curso - {escola.nome}',
    }
    
    return render(request, 'escolas/admin/curso_form.html', context)


@login_required
def editar_curso(request, escola_id, curso_id):
    """
    Editar um curso existente.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    curso = get_object_or_404(CursoEnsinoMedio, pk=curso_id, escola=escola)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        curso.nome = request.POST.get('nome', curso.nome)
        curso.descricao = request.POST.get('descricao', curso.descricao)
        curso.classes_lecionadas = request.POST.get('classes_lecionadas', curso.classes_lecionadas)
        curso.duracao_anos = request.POST.get('duracao_anos', curso.duracao_anos)
        curso.periodos = request.POST.get('periodos', curso.periodos)
        curso.exige_exame = request.POST.get('exige_exame') == 'on'
        curso.disciplinas_exame = request.POST.get('disciplinas_exame', curso.disciplinas_exame)
        
        vagas = request.POST.get('vagas_anuais')
        curso.vagas_anuais = int(vagas) if vagas else 0
        
        mensalidade = request.POST.get('mensalidade')
        curso.mensalidade = float(mensalidade) if mensalidade else 0
        
        taxa = request.POST.get('taxa_inscricao')
        curso.taxa_inscricao = float(taxa) if taxa else 0
        
        curso.save()
        messages.success(request, f'Curso "{curso.nome}" atualizado com sucesso!')
        return redirect('escolas:gerenciar_cursos', escola_id=escola.id)
    
    context = {
        'escola': escola,
        'curso': curso,
        'title': f'Editar Curso - {escola.nome}',
    }
    
    return render(request, 'escolas/admin/curso_form.html', context)


@login_required
def deletar_curso(request, escola_id, curso_id):
    """
    Deletar um curso.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    curso = get_object_or_404(CursoEnsinoMedio, pk=curso_id, escola=escola)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        nome_curso = curso.nome
        curso.delete()
        messages.success(request, f'Curso "{nome_curso}" deletado com sucesso!')
        return redirect('escolas:gerenciar_cursos', escola_id=escola.id)
    
    context = {
        'escola': escola,
        'curso': curso,
    }
    
    return render(request, 'escolas/admin/curso_confirm_delete.html', context)


@login_required
def galeria_escola(request, escola_id):
    """
    Gerenciar galeria de imagens da escola.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        categoria = request.POST.get('categoria', 'GERAL')
        legenda = request.POST.get('legenda', '')
        imagem = request.FILES.get('imagem')
        
        if imagem:
            GaleriaEscola.objects.create(
                escola=escola,
                categoria=categoria,
                imagem=imagem,
                legenda=legenda,
            )
            messages.success(request, 'Imagem adicionada à galeria com sucesso!')
            return redirect('escolas:galeria_escola', escola_id=escola.id)
    
    galerias = escola.galeria.all().order_by('-id')
    
    context = {
        'escola': escola,
        'galerias': galerias,
        'categorias': GaleriaEscola._meta.get_field('categoria').choices,
        'title': f'Galeria - {escola.nome}',
    }
    
    return render(request, 'escolas/admin/galeria.html', context)


@login_required
def deletar_imagem(request, escola_id, imagem_id):
    """
    Deletar uma imagem da galeria.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    imagem = get_object_or_404(GaleriaEscola, pk=imagem_id, escola=escola)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        imagem.delete()
        messages.success(request, 'Imagem removida da galeria!')
        return redirect('escolas:galeria_escola', escola_id=escola.id)
    
    context = {
        'escola': escola,
        'imagem': imagem,
    }
    
    return render(request, 'escolas/admin/imagem_confirm_delete.html', context)


@login_required
def parcerias_escola(request, escola_id):
    """
    Gerenciar parcerias da escola.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        nome_empresa = request.POST.get('nome_empresa')
        descricao = request.POST.get('descricao')
        logo = request.FILES.get('logo')
        
        parceria = ParceriaEscola(
            escola=escola,
            nome_empresa=nome_empresa,
            descricao=descricao,
        )
        
        if logo:
            parceria.logo = logo
        
        parceria.save()
        messages.success(request, f'Parceria com "{nome_empresa}" adicionada com sucesso!')
        return redirect('escolas:parcerias_escola', escola_id=escola.id)
    
    parcerias = escola.parcerias.all()
    
    context = {
        'escola': escola,
        'parcerias': parcerias,
        'title': f'Parcerias - {escola.nome}',
    }
    
    return render(request, 'escolas/admin/parcerias.html', context)


@login_required
def editar_parceria(request, escola_id, parceria_id):
    """
    Editar uma parceria existente.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    parceria = get_object_or_404(ParceriaEscola, pk=parceria_id, escola=escola)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        parceria.nome_empresa = request.POST.get('nome_empresa', parceria.nome_empresa)
        parceria.descricao = request.POST.get('descricao', parceria.descricao)
        
        logo = request.FILES.get('logo')
        if logo:
            parceria.logo = logo
        
        parceria.save()
        messages.success(request, f'Parceria atualizada com sucesso!')
        return redirect('escolas:parcerias_escola', escola_id=escola.id)
    
    context = {
        'escola': escola,
        'parceria': parceria,
    }
    
    return render(request, 'escolas/admin/parceria_form.html', context)


@login_required
def deletar_parceria(request, escola_id, parceria_id):
    """
    Deletar uma parceria.
    """
    escola = get_object_or_404(Escola, pk=escola_id)
    parceria = get_object_or_404(ParceriaEscola, pk=parceria_id, escola=escola)
    
    # Verificar se é representante
    if not _check_representante(request.user, escola):
        raise Http404("Acesso negado")
    
    if request.method == 'POST':
        nome = parceria.nome_empresa
        parceria.delete()
        messages.success(request, f'Parceria com "{nome}" removida com sucesso!')
        return redirect('escolas:parcerias_escola', escola_id=escola.id)
    
    context = {
        'escola': escola,
        'parceria': parceria,
    }
    
    return render(request, 'escolas/admin/parceria_confirm_delete.html', context)
