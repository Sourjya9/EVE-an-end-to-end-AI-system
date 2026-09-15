"""
Unit Tests for LangGraph Agent Nodes and Workflow.
"""

import pytest
from app.ai.agents.nodes import classify_request, generate_response
from app.ai.agents.graph import execute_agent_workflow


@pytest.mark.asyncio
async def test_classify_request_greeting():
    state = {"query": "Hello Eve, how are you?", "history": []}
    res = await classify_request(state)
    assert res["request_type"] == "direct_chat"
    assert res["needs_retrieval"] is False


@pytest.mark.asyncio
async def test_classify_request_document_query():
    state = {"query": "What does the uploaded architecture document say about PostgreSQL?", "history": []}
    res = await classify_request(state)
    assert res["request_type"] == "rag_retrieval"
    assert res["needs_retrieval"] is True


@pytest.mark.asyncio
async def test_full_agent_workflow_execution():
    result = await execute_agent_workflow(
        query="What is Eve?",
        history=[],
        system_prompt="You are a helpful test assistant.",
    )
    assert "response_content" in result
    assert len(result["response_content"]) > 0
    assert result["error"] is None
