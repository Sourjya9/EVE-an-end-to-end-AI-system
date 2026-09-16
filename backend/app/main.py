"""
Eve FastAPI Application Entrypoint.

Configures application lifespan, CORS policies, routers, OpenAPI metadata,
and observability integrations.
"""

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.errors import register_error_handlers
from app.api.routers import chat, documents, health, search
from app.core.config import settings
from app.core.logging import logger
from app.core.observability.sentry import init_sentry
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager handling startup initialization and shutdown cleanup."""
    logger.info(
        f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]"
    )

    # 1. Initialize Sentry
    init_sentry()

    # 2. In development, auto-verify DB tables and pgvector extension
    try:
        async with engine.begin() as conn:
            # Try enabling pgvector extension if connected to PostgreSQL
            if conn.dialect.name == "postgresql":
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    logger.info("pgvector extension verified.")
                except Exception as ext_err:
                    logger.warning(
                        f"Could not initialize pgvector extension: {ext_err}"
                    )

            # Create tables if not existing
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database schema verified.")
    except Exception as db_err:
        logger.warning(
            f"Database connection could not be established during startup: {db_err}"
        )

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-Style End-to-End AI Assistant Backend",
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests_and_latency(request: Request, call_next):
    """Structured request logging middleware recording request path and execution latency."""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    # Do not spam logs with health check probes
    if not request.url.path.startswith("/health"):
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)"
        )
    return response


# Register exception handlers
register_error_handlers(app)

# Include Routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(search.router)


@app.get("/", tags=["Root"])
async def root_endpoint():
    """Root redirect / information endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }
