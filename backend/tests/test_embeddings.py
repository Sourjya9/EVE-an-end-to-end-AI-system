"""
Unit Tests for Vector Embeddings.
"""

import pytest

from app.ai.rag.embeddings import JinaEmbeddingClient, _cosine_similarity


@pytest.mark.asyncio
async def test_deterministic_mock_embeddings():
    client = JinaEmbeddingClient()
    client.api_key = ""  # Force mock mode

    texts = ["How does RAG work?", "Tell me about pgvector."]
    vectors = await client.embed_texts(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) == client.dimensions
    assert len(vectors[1]) == client.dimensions

    # Ensure repeatability
    vectors_repeat = await client.embed_texts(texts)
    assert vectors[0] == vectors_repeat[0]


def test_cosine_similarity_calculation():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert pytest.approx(_cosine_similarity(v1, v2), 0.001) == 1.0

    v3 = [0.0, 1.0, 0.0]
    assert pytest.approx(_cosine_similarity(v1, v3), 0.001) == 0.0
