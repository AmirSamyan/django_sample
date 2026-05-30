"""Celery app exposure.

Keep this import tolerant so local tooling (linting/tests) can run even when
Celery isn't installed in the current environment.
"""

try:
    from .celery import app as celery_app
except Exception:  # pragma: no cover
    celery_app = None

__all__ = ("celery_app",)
