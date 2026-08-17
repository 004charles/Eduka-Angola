import json
import os
import unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eduangolacore.settings")
import django

django.setup()
from datetime import datetime, timezone
from unittest.mock import patch

from core.notification_events import publish_notification_event


class NotificationEventPublisherTests(unittest.TestCase):
    def test_is_disabled_explicitly_without_configuration(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("NOTIFICATION_SERVICE_URL", None)
            os.environ.pop("NOTIFICATION_SERVICE_SHARED_SECRET", None)
            result = publish_notification_event("book.published", "evt_12345678", {"book_id": 4})
        self.assertEqual(result["disabled"], True)

    @patch("core.notification_events.requests.post")
    def test_publishes_signed_event(self, post):
        post.return_value.raise_for_status.return_value = None
        post.return_value.json.return_value = {"accepted": True, "event_id": "evt_12345678", "duplicate": False}
        with patch.dict(os.environ, {"NOTIFICATION_SERVICE_URL": "http://notifications.test", "NOTIFICATION_SERVICE_SHARED_SECRET": "test-secret"}):
            result = publish_notification_event(
                "book.published",
                "evt_12345678",
                {"book_id": 4},
                occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            )
        self.assertTrue(result["accepted"])
        request = post.call_args
        body = request.kwargs["data"]
        self.assertEqual(json.loads(body)["event_type"], "book.published")
        self.assertTrue(request.kwargs["headers"]["X-Edukangola-Event-Signature"].startswith("t="))


if __name__ == "__main__":
    unittest.main()
