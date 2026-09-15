"""
Health Check Schemas.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    version: str = Field(..., example="0.1.0")
    environment: str = Field(..., example="development")
    database: str = Field(..., example="connected")
