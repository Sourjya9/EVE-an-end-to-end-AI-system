"""
Unit and Integration Tests for FastAPI API Endpoints.
"""

import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_chat_and_conversation_lifecycle(async_client: AsyncClient):
    # 1. Non-streaming chat request (creates conversation)
    chat_payload = {
        "message": "Hello Eve, who are you?",
        "stream": False,
    }
    res = await async_client.post("/api/chat", json=chat_payload)
    assert res.status_code == 200
    chat_data = res.json()
    assert "conversation_id" in chat_data
    assert "content" in chat_data
    conv_id = chat_data["conversation_id"]

    # 2. List conversations
    list_res = await async_client.get("/api/conversations")
    assert list_res.status_code == 200
    conversations = list_res.json()
    assert any(c["id"] == conv_id for c in conversations)

    # 3. Get conversation detail
    detail_res = await async_client.get(f"/api/conversations/{conv_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["messages"]) >= 2  # user + assistant

    # 4. Delete conversation
    del_res = await async_client.delete(f"/api/conversations/{conv_id}")
    assert del_res.status_code == 200

    # 5. Verify deleted
    get_again = await async_client.get(f"/api/conversations/{conv_id}")
    assert get_again.status_code == 404


@pytest.mark.asyncio
async def test_document_upload_and_search(async_client: AsyncClient):
    # 1. Upload a text document
    file_content = b"Eve uses pgvector for high-performance cosine similarity searches in PostgreSQL."
    files = {"file": ("eve_specs.txt", io.BytesIO(file_content), "text/plain")}

    upload_res = await async_client.post("/api/documents/upload", files=files)
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["status"] == "indexed"
    doc_id = upload_data["document_id"]

    # 2. List documents
    docs_res = await async_client.get("/api/documents")
    assert docs_res.status_code == 200
    docs = docs_res.json()
    assert any(d["id"] == doc_id for d in docs)

    # 3. Semantic Search
    search_payload = {"query": "What does Eve use for vector search?", "top_k": 3}
    search_res = await async_client.post("/api/search", json=search_payload)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total_results"] >= 1
    assert "pgvector" in search_data["results"][0]["content"]

    # 4. Delete document
    del_doc = await async_client.delete(f"/api/documents/{doc_id}")
    assert del_doc.status_code == 200
