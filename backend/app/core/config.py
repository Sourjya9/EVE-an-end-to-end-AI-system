"""
Application Configuration Module.

Loads environment variables using Pydantic Settings.
Ensures zero hardcoded secrets and validates configuration at startup.
"""

from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Eve AI Assistant"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development", description="Runtime environment: development, staging, production")
    DEBUG: bool = Field(default=False, description="Enable verbose debug logging")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR")

    # API and CORS
    API_V1_STR: str = "/api"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database Settings (PostgreSQL + pgvector)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/eve",
        description="Async PostgreSQL connection string",
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_TIMEOUT: float = 30.0

    # Groq LLM Settings
    GROQ_API_KEY: str = Field(default="", description="API key for Groq Cloud inference")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", description="Model name for Groq chat completions")
    GROQ_TEMPERATURE: float = 0.2
    GROQ_MAX_TOKENS: int = 2048
    GROQ_TIMEOUT_SECONDS: float = 30.0

    # Jina AI Embeddings Settings
    JINA_API_KEY: str = Field(default="", description="API key for Jina AI Embeddings")
    JINA_EMBEDDING_MODEL: str = Field(default="jina-embeddings-v3", description="Jina embeddings model")
    JINA_EMBEDDING_DIM: int = Field(default=1024, description="Vector dimension size")
    JINA_API_URL: str = "https://api.jina.ai/v1/embeddings"

    # RAG Configuration
    RAG_TOP_K: int = Field(default=4, description="Number of top chunks to retrieve")
    RAG_CHUNK_SIZE: int = Field(default=800, description="Chunk character size for document splitting")
    RAG_CHUNK_OVERLAP: int = Field(default=150, description="Chunk overlap character count")
    MAX_UPLOAD_SIZE_BYTES: int = Field(default=10 * 1024 * 1024, description="Max upload file size (10MB)")

    # Observability & Monitoring
    SENTRY_DSN: str = Field(default="", description="Sentry DSN for error monitoring")
    OPIK_API_KEY: str = Field(default="", description="Comet Opik API key for LLM tracing")
    OPIK_WORKSPACE: str = Field(default="default", description="Opik workspace name")
    OPIK_PROJECT_NAME: str = Field(default="eve-assistant", description="Opik project name")
    AWS_REGION: str = Field(default="us-east-1", description="AWS Region for CloudWatch and cloud resources")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
