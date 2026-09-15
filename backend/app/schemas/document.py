"""
Document Schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    chunk_count: int
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
