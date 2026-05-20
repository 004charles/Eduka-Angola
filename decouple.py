import os

def config(key, default=None, cast=None):
    """Simple replacement for python‑decouple's config.
    Retrieves environment variables and applies an optional ``cast``.
    """
    value = os.getenv(key, default)
    if cast and value is not None:
        try:
            return cast(value)
        except Exception:
            return default
    return value
