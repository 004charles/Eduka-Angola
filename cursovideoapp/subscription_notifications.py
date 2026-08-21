"""Avisos determinísticos de fim da subscrição Edukangola Vídeo."""
from __future__ import annotations

from datetime import timedelta
from html import escape
import os

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from core.email_utils import enviar_email_brevo
from usuarios.models import NotificacaoAluno, PreferenciaNotificacaoAluno

from .models import AssinaturaVideoAluno, AvisoExpiracaoSubscricaoVideo


JANELAS_AVISO_HORAS = (168, 72, 24)


def _rotulo_janela(antecedencia_horas: int) -> str:
    if antecedencia_horas % 24 == 0 and antecedencia_horas > 24:
        dias = antecedencia_horas // 24
        return f'{dias} dias'
    return '24 horas'


def _link_renovacao() -> str:
    base = getattr(settings, 'FRONTEND_URL', '') or os.environ.get('FRONTEND_URL', 'https://www.edukangola.com')
    return f'{base.rstrip("/")}/cursos-em-video'


def _enviar_email(aviso: AvisoExpiracaoSubscricaoVideo) -> bool:
    assinatura = aviso.assinatura
    aluno = assinatura.aluno
    email = getattr(aluno.usuario, 'email', '')
    if not email:
        return True
    prazo = _rotulo_janela(aviso.antecedencia_horas)
    fim = timezone.localtime(assinatura.data_fim).strftime('%d/%m/%Y às %H:%M')
    url = _link_renovacao()
    assunto = f'A sua subscrição Edukangola Vídeo termina em {prazo}'
    texto = (
        f'Olá, {aluno.nome}. A sua subscrição {assinatura.plano.nome} termina em {fim}. '
        f'Renove agora para continuar a aceder a todos os cursos em vídeo: {url}'
    )
    html = (
        f'<p>Olá, <strong>{escape(aluno.nome)}</strong>.</p>'
        f'<p>A sua subscrição <strong>{escape(assinatura.plano.nome)}</strong> termina em <strong>{escape(fim)}</strong>.</p>'
        f'<p>Renove agora para continuar a aceder a todos os cursos em vídeo sem interrupção.</p>'
        f'<p><a href="{escape(url)}">Renovar a subscrição Edukangola Vídeo</a></p>'
    )
    if getattr(settings, 'BREVO_API_KEY', ''):
        return enviar_email_brevo(email, assunto, html, texto, aluno.nome)
    return bool(send_mail(assunto, texto, getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@edukangola.com'), [email], html_message=html))


def processar_avisos_expiracao_subscricao_video(agora=None) -> dict[str, int]:
    """Cria e entrega avisos nas janelas de 7d, 3d e 24h sem repetir por subscrição."""
    agora = agora or timezone.now()
    resultado = {'avisos_criados': 0, 'notificacoes_plataforma': 0, 'emails_enviados': 0, 'emails_falhados': 0}
    assinaturas = AssinaturaVideoAluno.objects.filter(
        status='ATIVA', data_inicio__lte=agora, data_fim__gt=agora, data_fim__lte=agora + timedelta(days=7)
    ).select_related('aluno__usuario', 'plano')

    for assinatura in assinaturas:
        restante = assinatura.data_fim - agora
        for antecedencia_horas in JANELAS_AVISO_HORAS:
            limite_superior = timedelta(hours=antecedencia_horas)
            limite_inferior = timedelta(hours=max(0, antecedencia_horas - 24))
            if not limite_inferior < restante <= limite_superior:
                continue
            with transaction.atomic():
                aviso, criado = AvisoExpiracaoSubscricaoVideo.objects.select_for_update().get_or_create(
                    assinatura=assinatura, antecedencia_horas=antecedencia_horas
                )
                if criado:
                    resultado['avisos_criados'] += 1
                preferencias, _ = PreferenciaNotificacaoAluno.objects.get_or_create(aluno=assinatura.aluno)
                if preferencias.receber_na_plataforma and not aviso.notificacao_id:
                    prazo = _rotulo_janela(antecedencia_horas)
                    aviso.notificacao = NotificacaoAluno.objects.create(
                        aluno=assinatura.aluno,
                        titulo=f'A sua subscrição termina em {prazo}',
                        mensagem='Renove a subscrição Edukangola Vídeo para continuar a aprender sem interrupção.',
                        link='/cursos-em-video',
                        tipo='APRENDIZAGEM',
                    )
                    aviso.save(update_fields=('notificacao', 'atualizado_em'))
                    resultado['notificacoes_plataforma'] += 1
                if aviso.email_processado_em is None:
                    if preferencias.receber_por_email:
                        if _enviar_email(aviso):
                            resultado['emails_enviados'] += 1
                            aviso.email_processado_em = timezone.now()
                            aviso.save(update_fields=('email_processado_em', 'atualizado_em'))
                        else:
                            resultado['emails_falhados'] += 1
                    else:
                        aviso.email_processado_em = timezone.now()
                        aviso.save(update_fields=('email_processado_em', 'atualizado_em'))
    return resultado
