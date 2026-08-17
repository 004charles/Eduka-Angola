import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from notification_service.contracts import NotificationEvent
from notification_service.security import InvalidEventSignature, sign_event, verify_event_signature
from notification_service.store import EventStore
from notification_service.processor import NotificationProcessor
from unittest.mock import MagicMock, patch


class NotificationServiceTests(unittest.TestCase):
    def test_signature_round_trip_and_replay_protection(self):
        body = b'{"event_id":"evt_12345678","event_type":"book.published"}'
        signature = sign_event(body, "test-secret", "1700000000")
        verify_event_signature(body, signature, "test-secret", now=1700000000)
        with self.assertRaises(InvalidEventSignature):
            verify_event_signature(body, signature, "test-secret", now=1700000401)

    def test_processor_delivers_platform_channel(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {
            'DJANGO_INTERNAL_API_URL': 'https://django.example',
            'NOTIFICATION_SERVICE_DJANGO_SECRET': 'internal-secret',
            'BREVO_API_KEY': '',
            'DEFAULT_FROM_EMAIL': '',
        }, clear=False), patch('notification_service.processor.requests.get') as get, patch('notification_service.processor.requests.post') as post:
            store = EventStore(str(Path(directory) / 'notifications.sqlite3'))
            event = NotificationEvent(
                event_id='evt_course_1234',
                event_type='course.published',
                occurred_at=datetime.now(timezone.utc),
                payload={'course_id': 4, 'title': 'Python', 'link': '/cursos/4'},
            )
            store.accept_event(event)
            recipient_response = MagicMock()
            recipient_response.json.return_value = {'destinatarios': [{'id': 7, 'nome': 'Aluno', 'email': 'aluno@example.com'}]}
            get.return_value = recipient_response
            post.return_value = MagicMock()
            result = NotificationProcessor(store).process_pending()
            self.assertEqual(result, {'processed': 1, 'delivered': 1, 'failed': 0})
            self.assertEqual(get.call_args.kwargs['params']['channel'], 'platform')
            self.assertEqual(post.call_count, 1)

    def test_store_accepts_event_once(self):
        with tempfile.TemporaryDirectory() as directory:
            store = EventStore(str(Path(directory) / "notifications.sqlite3"))
            event = NotificationEvent(
                event_id="evt_12345678",
                event_type="book.published",
                occurred_at=datetime.now(timezone.utc),
                payload={"book_id": 4},
            )
            self.assertTrue(store.accept_event(event))
            self.assertFalse(store.accept_event(event))
            self.assertEqual(store.count_events(), 1)


if __name__ == "__main__":
    unittest.main()
