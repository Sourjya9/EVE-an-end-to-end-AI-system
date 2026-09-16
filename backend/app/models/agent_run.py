"""
Agent Run Audit Log Model.
"""

import uuid
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    request_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "direct_chat", "rag_retrieval", etc.
    needs_retrieval: Mapped[bool] = mapped_column(default=False, nullable=False)
    retrieved_chunk_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    execution_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True, default=dict
    )
