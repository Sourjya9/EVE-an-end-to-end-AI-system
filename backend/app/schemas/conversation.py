"""
Conversation Schemas.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.chat import Citation


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    citations: list[Citation] | None = None
    token_count: int | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    title: str | None = Field(default="New Conversation", max_length=255)


class ConversationResponse(BaseModel):
    id: str
    title: str
    user_id: str | None = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    id: str
    title: str
    user_id: str | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
