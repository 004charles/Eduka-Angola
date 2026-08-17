import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from notification_service.contracts import NotificationEvent
from notification_service.security import InvalidEventSignature, sign_event, verify_event_signature
from notification_service.store import EventStore


class NotificationServiceTests(unittest.TestCase):
    def test_signature_round_trip_and_replay_protection(self):
        body = b'{"event_id":"evt_12345678","event_type":"book.published"}'
        signature = sign_event(body, "test-secret", "1700000000")
        verify_event_signature(body, signature, "test-secret", now=1700000000)
        with self.assertRaises(InvalidEventSignature):
            verify_event_signature(body, signature, "test-secret", now=1700000401)

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
