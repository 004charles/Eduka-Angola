import json
import os

import requests

from .email_sender import EmailSender
from .store import EventStore


EVENT_COPY = {
    'course.published': ('Novo curso disponível', 'CURSO'),
    'class.opened': ('Nova turma aberta', 'CURSO'),
    'book.published': ('Novo livro na Biblioteca', 'SISTEMA'),
    'event.published': ('Novo evento publicado', 'EVENTO'),
    'learning.reminder': ('Continue a sua aprendizagem', 'SISTEMA'),
    'calendar.notice': ('Aviso de calendário', 'SISTEMA'),
    'weekly.digest.requested': ('O seu resumo semanal', 'SISTEMA'),
}


class NotificationProcessor:
    def __init__(self, store: EventStore):
        self.store = store
        self.django_url = os.getenv('DJANGO_INTERNAL_API_URL', '').rstrip('/')
        self.secret = os.getenv('NOTIFICATION_SERVICE_DJANGO_SECRET', '')
        self.email_sender = EmailSender()

    def process_pending(self, limit: int = 25) -> dict[str, int]:
        processed = 0
        delivered = 0
        failed = 0
        for row in self.store.pending_events(limit):
            try:
                delivered += self._process_row(row)
                self.store.mark_event_processed(row['event_id'])
                processed += 1
            except (requests.RequestException, ValueError, KeyError, RuntimeError) as exc:
                failed += 1
                print(f"Falha no evento {row['event_id']}: {exc}")
        return {'processed': processed, 'delivered': delivered, 'failed': failed}

    def _process_row(self, row) -> int:
        if not self.django_url or not self.secret:
            raise RuntimeError('Integração interna do Django não configurada')
        event_type = row['event_type']
        payload = json.loads(row['payload_json'])
        headers = {'X-Notification-Service-Key': self.secret}
        recipient_id = payload.get('recipient_id') if event_type == 'learning.reminder' else None
        title, kind = EVENT_COPY.get(event_type, ('Novidade Edukangola', 'SISTEMA'))
        message = self._message(event_type, payload)
        delivered = self._deliver_platform(event_type, recipient_id, headers, payload, title, kind, message)
        delivered += self._deliver_email(event_type, recipient_id, headers, payload, title, message)
        return delivered

    def _recipients(self, event_type, channel, recipient_id, headers):
        response = requests.get(
            f'{self.django_url}/auth/api/internal/notificacoes/destinatarios/',
            params={'event_type': event_type, 'channel': channel, **({'recipient_id': recipient_id} if recipient_id else {})},
            headers=headers,
            timeout=5,
        )
        response.raise_for_status()
        return response.json().get('destinatarios', [])

    def _deliver_platform(self, event_type, recipient_id, headers, payload, title, kind, message):
        delivered = 0
        for recipient in self._recipients(event_type, 'platform', recipient_id, headers):
            result = requests.post(
                f'{self.django_url}/auth/api/internal/notificacoes/criar/',
                headers={**headers, 'Content-Type': 'application/json'},
                json={'aluno_id': recipient['id'], 'titulo': title, 'mensagem': message, 'link': payload.get('link', '/'), 'tipo': kind},
                timeout=5,
            )
            result.raise_for_status()
            delivered += 1
        return delivered

    def _deliver_email(self, event_type, recipient_id, headers, payload, title, message):
        if not self.email_sender.configured:
            return 0
        delivered = 0
        for recipient in self._recipients(event_type, 'email', recipient_id, headers):
            self.email_sender.send(recipient_email=recipient['email'], recipient_name=recipient.get('nome', ''), subject=title, message=message, link=payload.get('link', '/'))
            delivered += 1
        return delivered

    @staticmethod
    def _message(event_type: str, payload: dict) -> str:
        title = payload.get('title') or payload.get('course_title') or 'uma nova oportunidade'
        if event_type == 'course.published':
            return f'O curso em vídeo ou formação presencial “{title}” já está disponível para explorar.'
        if event_type == 'class.opened':
            return f'A turma “{title}” abriu novas vagas. Consulte a data e os detalhes da formação.'
        if event_type == 'book.published':
            return f'O livro “{title}” foi adicionado à Biblioteca Edukangola.'
        if event_type == 'event.published':
            return f'O evento “{title}” já está publicado. Consulte os detalhes e os bilhetes disponíveis.'
        return payload.get('message') or 'Há uma novidade na sua jornada de aprendizagem.'
