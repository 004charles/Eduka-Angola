"""Very small shim for dj_database_url used in settings.
Provides a ``config`` function that returns a Django DATABASES dict.
If DATABASE_URL env var is set, it will try to parse a Postgres URL
(simple split) but for most local/dev cases we fallback to SQLite.
"""
import os
from urllib.parse import urlparse

def config(url=None, default=None, conn_max_age=0, conn_health_checks=False):
    # Use provided URL or env var
    db_url = url or os.getenv('DATABASE_URL')
    if not db_url:
        # No URL – fallback to SQLite using DEFAULT from settings if provided
        return default if default is not None else {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(os.getcwd(), 'db.sqlite3'),
        }
    # Very naive parsing – only handle postgres://user:pass@host:port/name
    parsed = urlparse(db_url)
    if parsed.scheme.startswith('postgres'):
        name = parsed.path.lstrip('/')
        return {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': name,
            'USER': parsed.username or '',
            'PASSWORD': parsed.password or '',
            'HOST': parsed.hostname or '',
            'PORT': parsed.port or '',
            'CONN_MAX_AGE': conn_max_age,
            'OPTIONS': {'sslmode': 'require'} if conn_health_checks else {},
        }
    # Fallback – treat as SQLite path
    return {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': db_url,
        'CONN_MAX_AGE': conn_max_age,
    }
