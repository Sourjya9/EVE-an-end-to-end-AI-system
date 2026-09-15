"""
Document Chunk Model with pgvector Embedding.
"""

import uuid
from typing import Any, Dict, Optional, TYPE_CHECKING
from sqlalchemy import ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.core.config import settings
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.document import Document


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True, default=dict)

    # pgvector embedding column (1024 dimensions default for Jina v3)
    embedding: Mapped[Optional[Any]] = mapped_column(Vector(settings.JINA_EMBEDDING_DIM), nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    __table_args__ = (
        Index(
            "ix_document_chunks_embedding",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
