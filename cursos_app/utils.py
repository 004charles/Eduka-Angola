from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

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

def notificar_seguidores(curso):
    """
    Notifica seguidores do centro sobre um novo curso publicado.
    """
    # Implementação pendente ou movida de outro lugar
    # Por enquanto, mantemos a assinatura para não quebrar o modelo
    pass

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
