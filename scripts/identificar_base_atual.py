import os
from urllib.parse import urlparse

url = os.getenv('DATABASE_URL')
if not url:
    print('DATABASE_ENGINE sqlite_or_default')
else:
    parsed = urlparse(url)
    print('DATABASE_SCHEME', parsed.scheme)
    print('DATABASE_HOST', parsed.hostname or '')
    print('DATABASE_PORT', parsed.port or '')
    print('DATABASE_NAME', (parsed.path or '').lstrip('/'))
