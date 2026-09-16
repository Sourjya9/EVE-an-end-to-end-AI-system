"""
Sentry Error Monitoring Integration.

Captures unhandled exceptions and performance transactions in production,
while remaining a clean no-op if SENTRY_DSN is not configured.
"""

from app.core.config import settings
from app.core.logging import logger

try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


def init_sentry() -> None:
    """Initializes Sentry SDK if DSN is set and package is installed."""
    if not settings.SENTRY_DSN:
        logger.info("Sentry DSN not configured; error monitoring disabled.")
        return

    if not SENTRY_AVAILABLE:
        logger.warning("sentry-sdk not installed; skipping Sentry initialization.")
        return

    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            release=f"eve-backend@{settings.VERSION}",
            traces_sample_rate=0.2 if settings.ENVIRONMENT == "production" else 1.0,
            profiles_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 0.0,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            send_default_pii=False,
        )
        logger.info("Sentry initialized successfully.")
    except Exception as exc:
        logger.error(f"Failed to initialize Sentry: {exc}")


def capture_exception(exc: Exception, context: dict | None = None) -> None:
    """Manually captures an exception to Sentry with optional context tags."""
    if settings.SENTRY_DSN and SENTRY_AVAILABLE:
        if context:
            with sentry_sdk.push_scope() as scope:
                for k, v in context.items():
                    scope.set_extra(k, v)
                sentry_sdk.capture_exception(exc)
        else:
            sentry_sdk.capture_exception(exc)
