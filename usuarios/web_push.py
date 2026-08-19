"""Entrega Web Push VAPID própria, isolada do contrato público do frontend."""

from __future__ import annotations

import json
import logging

from django.conf import settings
from django.utils import timezone

from .models import NotificacaoAluno, PreferenciaNotificacaoAluno, SubscricaoWebPush

logger = logging.getLogger(__name__)


def web_push_configurada() -> bool:
    return bool(getattr(settings, 'VAPID_PUBLIC_KEY', '') and getattr(settings, 'VAPID_PRIVATE_KEY', ''))


def _preferencia_permite(preferencias: PreferenciaNotificacaoAluno, notificacao: NotificacaoAluno) -> bool:
    if not preferencias.receber_push:
        return False
    campo_por_tipo = {
        'CURSO': 'novos_cursos',
        'TURMA': 'novas_turmas',
        'LIVRO': 'novos_livros',
        'EVENTO': 'novos_eventos',
        'FERIADO': 'calendario_e_feriados',
        'APRENDIZAGEM': 'atualizacoes_aprendizagem',
    }
    campo = campo_por_tipo.get(notificacao.tipo)
    return not campo or bool(getattr(preferencias, campo, True))


def _payload(notificacao: NotificacaoAluno) -> dict[str, str]:
    return {
        'title': notificacao.titulo[:150],
        'body': notificacao.mensagem[:500],
        'url': notificacao.link or '/aluno',
        'tag': f'edukangola-{notificacao.tipo.lower()}-{notificacao.id}',
    }


def _marcar_falha(subscricao: SubscricaoWebPush, *, invalidar: bool = False) -> None:
    subscricao.ultima_falha_em = timezone.now()
    subscricao.falhas_consecutivas += 1
    if invalidar or subscricao.falhas_consecutivas >= 3:
        subscricao.ativa = False
    subscricao.save(update_fields=['ultima_falha_em', 'falhas_consecutivas', 'ativa', 'atualizada_em'])


def enviar_notificacao_web_push(notificacao_id: int) -> dict[str, int | bool]:
    """Envia uma notificação persistida aos dispositivos autorizados do respectivo aluno."""
    if not web_push_configurada():
        return {'configured': False, 'sent': 0, 'failed': 0}
    notificacao = NotificacaoAluno.objects.select_related('aluno').filter(id=notificacao_id).first()
    if not notificacao:
        return {'configured': True, 'sent': 0, 'failed': 0}
    preferencias, _ = PreferenciaNotificacaoAluno.objects.get_or_create(aluno=notificacao.aluno)
    if not _preferencia_permite(preferencias, notificacao):
        return {'configured': True, 'sent': 0, 'failed': 0}

    from pywebpush import WebPushException, webpush

    sent = failed = 0
    data = json.dumps(_payload(notificacao), ensure_ascii=False)
    subscriptions = SubscricaoWebPush.objects.filter(aluno=notificacao.aluno, ativa=True)
    for subscricao in subscriptions:
        try:
            webpush(
                subscription_info={
                    'endpoint': subscricao.endpoint,
                    'keys': {'p256dh': subscricao.chave_p256dh, 'auth': subscricao.chave_auth},
                },
                data=data,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={'sub': settings.VAPID_SUBJECT},
                ttl=60 * 60 * 12,
            )
            subscricao.ultimo_envio_em = timezone.now()
            subscricao.falhas_consecutivas = 0
            subscricao.save(update_fields=['ultimo_envio_em', 'falhas_consecutivas', 'atualizada_em'])
            sent += 1
        except WebPushException as exc:
            status = getattr(getattr(exc, 'response', None), 'status_code', None)
            _marcar_falha(subscricao, invalidar=status in {404, 410})
            logger.info('Falha ao entregar Web Push para subscrição %s (HTTP %s).', subscricao.id, status)
            failed += 1
        except Exception:
            _marcar_falha(subscricao)
            logger.exception('Erro inesperado na entrega Web Push para subscrição %s.', subscricao.id)
            failed += 1
    return {'configured': True, 'sent': sent, 'failed': failed}
