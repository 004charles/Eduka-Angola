from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


EventType = Literal[
    "course.published",
    "class.opened",
    "book.published",
    "event.published",
    "learning.reminder",
    "calendar.notice",
    "weekly.digest.requested",
]


class NotificationEvent(BaseModel):
    event_id: str = Field(min_length=8, max_length=120)
    event_type: EventType
    occurred_at: datetime
    source: str = Field(default="edukangola-django", max_length=80)
    schema_version: int = Field(default=1, ge=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class EventAccepted(BaseModel):
    accepted: bool = True
    event_id: str
    duplicate: bool = False


class DeliveryStatus(BaseModel):
    event_id: str
    recipient_id: int
    channel: Literal["platform", "email"]
    status: Literal["pending", "sent", "failed", "skipped"]
    reason: str | None = None
