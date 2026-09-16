"""
Chat and Streaming Schemas.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    score: float
    snippet: str


class ChatRequest(BaseModel):
    conversation_id: str | None = Field(
        default=None, description="ID of existing conversation or None to create new"
    )
    message: str = Field(..., min_length=1, description="User query or message")
    stream: bool = Field(
        default=True, description="Whether to stream response tokens via SSE"
    )
    system_prompt: str | None = Field(
        default=None, description="Optional override system prompt"
    )


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    role: str = "assistant"
    content: str
    citations: list[Citation] = Field(default_factory=list)
    created_at: datetime


class StreamChunk(BaseModel):
    delta: str = ""
    citations: list[Citation] | None = None
    conversation_id: str | None = None
    done: bool = False
