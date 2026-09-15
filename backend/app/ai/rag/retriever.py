"""
Semantic Vector Retriever.

Executes vector similarity search using pgvector cosine distance operator (<=>)
against stored document chunks, with pure python fallback for SQLite test environments.
"""

import math
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.logging import logger
from app.core.observability.opik import opik_tracer
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.rag import SearchResultItem


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Fallback cosine similarity computation for tests."""
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorRetriever:
    """Encapsulates semantic retrieval and ranking over pgvector embeddings."""

    async def search(
        self,
        session: AsyncSession,
        query_embedding: List[float],
        top_k: int = settings.RAG_TOP_K,
        document_id: Optional[str] = None,
    ) -> List[SearchResultItem]:
        """
        Retrieves top_k document chunks most similar to query_embedding.
        Uses pgvector cosine distance operator (<=>).
        """
        with opik_tracer.trace_span("retriever_search", {"top_k": top_k, "document_id": document_id}):
            # Check database dialect to support both PostgreSQL (pgvector) and SQLite (tests)
            bind = session.bind or session.get_bind()
            dialect_name = bind.dialect.name if bind else "postgresql"

            if dialect_name == "postgresql":
                # Cosine distance: 0 is identical, 2 is opposite.
                # Similarity: 1 - distance
                distance_expr = DocumentChunk.embedding.cosine_distance(query_embedding)
                query = (
                    select(
                        DocumentChunk,
                        Document.filename,
                        distance_expr.label("distance"),
                    )
                    .join(Document, DocumentChunk.document_id == Document.id)
                    .where(Document.status == "indexed")
                )

                if document_id:
                    query = query.where(DocumentChunk.document_id == document_id)

                query = query.order_by(distance_expr).limit(top_k)

                result = await session.execute(query)
                rows = result.all()

                results: List[SearchResultItem] = []
                for chunk, filename, distance in rows:
                    similarity_score = max(0.0, round(1.0 - float(distance), 4))
                    results.append(
                        SearchResultItem(
                            chunk_id=chunk.id,
                            document_id=chunk.document_id,
                            filename=filename,
                            chunk_index=chunk.chunk_index,
                            content=chunk.content,
                            score=similarity_score,
                            metadata=chunk.metadata_json or {},
                        )
                    )
                return results

            else:
                # SQLite fallback: load chunks and compute similarity in Python
                query = (
                    select(DocumentChunk, Document.filename)
                    .join(Document, DocumentChunk.document_id == Document.id)
                    .where(Document.status == "indexed")
                )
                if document_id:
                    query = query.where(DocumentChunk.document_id == document_id)

                result = await session.execute(query)
                rows = result.all()

                scored: List[tuple] = []
                for chunk, filename in rows:
                    if chunk.embedding is not None:
                        emb = list(chunk.embedding)
                        score = _cosine_similarity(query_embedding, emb)
                        scored.append((chunk, filename, score))

                # Sort descending by score
                scored.sort(key=lambda x: x[2], reverse=True)
                top_items = scored[:top_k]

                return [
                    SearchResultItem(
                        chunk_id=c.id,
                        document_id=c.document_id,
                        filename=fn,
                        chunk_index=c.chunk_index,
                        content=c.content,
                        score=round(sc, 4),
                        metadata=c.metadata_json or {},
                    )
                    for c, fn, sc in top_items
                ]


retriever = VectorRetriever()
