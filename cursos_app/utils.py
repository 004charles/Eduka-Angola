from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import threading

def enviar_email_inscricao(inscricao, tipo='pendente', link_curso=None):
    """
    Envia e-mails de notificação de inscrição.
    tipo: 'pendente' ou 'status'
    """
    aluno = inscricao.aluno
    curso = inscricao.curso
    
    contexto = {
        'aluno': aluno,
        'curso': curso,
        'suporte_email': getattr(settings, 'SUPORTE_EMAIL', settings.DEFAULT_FROM_EMAIL),
        'link_curso': link_curso,
        'inscricao': inscricao,
    }
    
    if tipo == 'pendente':
        assunto = f"Inscrição recebida: {curso.titulo}"
        template = 'emails/inscricao_pendente.html'
    else:
        assunto = f"Status da inscrição: {curso.titulo} — {inscricao.get_status_display()}"
        template = 'emails/inscricao_status.html'
        contexto.update({
            'status_legivel': inscricao.get_status_display(),
            'status_codigo': inscricao.status,
            'pagamento_simulado': getattr(inscricao, 'pagamento_simulado', False),
        })

    html = render_to_string(template, contexto)
    txt = strip_tags(html)

    msg = EmailMultiAlternatives(
        subject=assunto,
        body=txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[aluno.email],
    )
    msg.attach_alternative(html, "text/html")
    msg.send()

def _enviar_email_async(msg):
    try:
        msg.send()
    except Exception as e:
        print(f"Erro ao enviar e-mail em background: {e}")

def notificar_seguidores(objeto, tipo_conteudo='CURSO'):
    """
    Hub central para notificar seguidores sobre novas publicações.
    Canais: Notificação interna (Site), E-mail e WhatsApp (Simulado).
    """
    from usuarios.models import NotificacaoAluno
    from gestoreduka.models import CentroSeguimento
    
    centro = objeto.centro
    centro_nome = centro.nome if centro and centro.nome else "Centro de Formação"
    seguidores = CentroSeguimento.objects.filter(centro=centro).select_related('aluno__usuario')
    
    # Preparar conteúdo baseado no tipo
    if tipo_conteudo == 'CURSO':
        titulo_notif = f"Novo Curso: {objeto.titulo}"
        msg_base = f"O centro {centro_nome} acabou de publicar o curso '{objeto.titulo}'."
        link = f"/cursos/{objeto.slug}/"
    elif tipo_conteudo == 'EVENTO':
        titulo_notif = f"Novo Evento: {objeto.titulo}"
        msg_base = f"Fica atento! O centro {centro_nome} tem um novo evento: '{objeto.titulo}'."
        link = f"/gestoreduka/perfil/" # Link para o perfil onde lista eventos
    elif tipo_conteudo == 'ANUNCIO':
        titulo_notif = objeto.titulo
        msg_base = f"Novidade do centro {centro_nome}: {objeto.titulo}"
        link = f"/gestoreduka/perfil/"

    for seguimento in seguidores:
        aluno = seguimento.aluno
        usuario = aluno.usuario
        
        # 1. Notificação Interna (Site)
        NotificacaoAluno.objects.create(
            aluno=aluno,
            titulo=titulo_notif,
            mensagem=msg_base,
            link=link,
            tipo=tipo_conteudo
        )
        
        # 2. Notificação por E-mail
        try:
            contexto = {
                'aluno': aluno,
                'objeto': objeto,
                'centro': centro,
                'titulo': titulo_notif,
                'mensagem': msg_base,
                'link': f"{settings.SITE_URL}{link}" if hasattr(settings, 'SITE_URL') else link
            }
            html = render_to_string('emails/notificacao_seguidor.html', contexto)
            txt = strip_tags(html)
            
            msg = EmailMultiAlternatives(
                subject=f"[EdukAngola] {titulo_notif}",
                body=txt,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email],
            )
            msg.attach_alternative(html, "text/html")
            
            # Enviar em background para não travar a requisição
            t = threading.Thread(target=_enviar_email_async, args=(msg,))
            t.start()
            
        except Exception as e:
            print(f"Erro ao processar e-mail de notificação: {e}")

        # 3. Notificação por WhatsApp (Simulação/Log)
        telefone = "N/A"
        try:
            perfil = aluno.perfil
            telefone = perfil.telefone if perfil and perfil.telefone else "N/A"
        except Exception:
            pass
            
        print(f"[WHATSAPP MOCK] Enviando para {telefone}: {msg_base}")

def processar_simulacao_pagamento(inscricao):
    """
    Processa a simulação de pagamento de uma inscrição.
    """
    if inscricao.status != 'P':
        return False, "Esta inscrição já foi processada."

    inscricao.pagamento_simulado = True
    inscricao.forma_pagamento = 'SIMULADO'
    inscricao.valor_pago = inscricao.curso.preco_atual
    inscricao.data_pagamento = timezone.now()
    inscricao.status = 'A'
    if not inscricao.codigo_simulacao:
        inscricao.codigo_simulacao = f"SIM_{inscricao.curso.id}_{inscricao.aluno.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
    inscricao.data_simulacao = timezone.now()
    inscricao.data_confirmacao = timezone.now()

    inscricao.save()

    # Enviar email de confirmação
    try:
        inscricao.enviar_email_status()
    except:
        pass

    return True, "Pagamento simulado com sucesso! Inscrição confirmada."

def atribuir_turma_automatica(inscricao):
    """
    Atribui uma turma automaticamente baseada na disponibilidade.
    """
    if inscricao.turma_escolhida or inscricao.status != 'A':
        return False
    
    turma_disponivel = inscricao.curso.get_turma_menos_lotada()
    if turma_disponivel:
        inscricao.turma_escolhida = turma_disponivel
        inscricao.save()
        return True
    return False
