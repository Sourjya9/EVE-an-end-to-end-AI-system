"""
LangGraph Agent State Definition.

Defines the typed dictionary tracking conversational and workflow state
across classification, retrieval, and generation graph nodes.
"""

from typing import Any

from typing_extensions import TypedDict


class AgentState(TypedDict):
    """Immutable state container passed across LangGraph nodes."""

    # Incoming request info
    query: str
    conversation_id: str | None
    system_prompt: str | None
    history: list[dict[str, str]]

    # Classification node outputs
    request_type: str  # "direct_chat", "rag_retrieval", "tool_execution"
    needs_retrieval: bool
    classification_reason: str | None

    # Retrieval node outputs
    retrieved_chunks: list[dict[str, Any]]
    citations: list[dict[str, Any]]

    # Generation node outputs
    response_content: str
    error: str | None
