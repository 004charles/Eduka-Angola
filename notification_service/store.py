import json
import sqlite3
from pathlib import Path
from threading import Lock


class EventStore:
    def __init__(self, database_path: str):
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialise()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialise(self):
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS inbound_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'accepted',
                    received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS deliveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    recipient_id INTEGER NOT NULL,
                    channel TEXT NOT NULL,
                    dedupe_key TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    reason TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(event_id, recipient_id, channel, dedupe_key)
                );
                """
            )

    def accept_event(self, event) -> bool:
        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO inbound_events
                (event_id, event_type, occurred_at, payload_json)
                VALUES (?, ?, ?, ?)
                """,
                (event.event_id, event.event_type, event.occurred_at.isoformat(), json.dumps(event.payload, ensure_ascii=False)),
            )
            return cursor.rowcount == 1

    def count_events(self) -> int:
        with self._connect() as connection:
            return connection.execute("SELECT COUNT(*) FROM inbound_events").fetchone()[0]

    def pending_events(self, limit: int = 50):
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT event_id, event_type, occurred_at, payload_json FROM inbound_events WHERE status = 'accepted' ORDER BY received_at LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_event_processed(self, event_id: str):
        with self._lock, self._connect() as connection:
            connection.execute("UPDATE inbound_events SET status = 'processed' WHERE event_id = ?", (event_id,))
