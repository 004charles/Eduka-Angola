import os
import signal
import time

from .processor import NotificationProcessor
from .store import EventStore


running = True


def stop(_signum, _frame):
    global running
    running = False


def main():
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    store = EventStore(os.getenv('NOTIFICATION_DATABASE_PATH', './data/notifications.sqlite3'))
    processor = NotificationProcessor(store)
    interval = max(5, int(os.getenv('NOTIFICATION_WORKER_INTERVAL_SECONDS', '30')))
    while running:
        result = processor.process_pending(limit=50)
        if result['processed'] or result['failed']:
            print(f"Processamento: {result}", flush=True)
        time.sleep(interval)


if __name__ == '__main__':
    main()
