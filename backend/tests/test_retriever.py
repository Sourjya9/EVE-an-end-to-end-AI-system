"""
Unit Tests for Vector Retrieval.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.rag.retriever import retriever
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


@pytest.mark.asyncio
async def test_retriever_empty_database(db_session: AsyncSession):
    query_vector = [0.1] * 1024
    results = await retriever.search(db_session, query_vector, top_k=5)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_retriever_ranking(db_session: AsyncSession):
    # 1. Create a document
    doc = Document(
        filename="test_guide.txt",
        file_type="txt",
        file_size_bytes=100,
        status="indexed",
        chunk_count=2,
    )
    db_session.add(doc)
    await db_session.flush()

    # 2. Add two chunks with known mock embeddings
    # Chunk 1 aligns strongly with query_vec
    vec1 = [0.9] + [0.0] * 1023
    vec2 = [0.0] + [0.9] * 1023
    query_vec = [1.0] + [0.0] * 1023

    c1 = DocumentChunk(
        document_id=doc.id,
        chunk_index=0,
        content="Chunk 1 strongly matches query vector",
        embedding=vec1,
        metadata_json={"tag": "high_match"},
    )
    c2 = DocumentChunk(
        document_id=doc.id,
        chunk_index=1,
        content="Chunk 2 is orthogonal to query",
        embedding=vec2,
        metadata_json={"tag": "low_match"},
    )
    db_session.add_all([c1, c2])
    await db_session.commit()

    # 3. Retrieve
    results = await retriever.search(db_session, query_vec, top_k=2)
    assert len(results) == 2
    assert results[0].chunk_id == c1.id
    assert results[0].score > results[1].score
    assert results[0].filename == "test_guide.txt"
