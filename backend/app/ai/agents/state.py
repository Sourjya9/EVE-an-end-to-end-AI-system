"""
LangGraph Agent State Definition.

Defines the typed dictionary tracking conversational and workflow state
across classification, retrieval, and generation graph nodes.
"""

from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
import operator


class AgentState(TypedDict):
    """Immutable state container passed across LangGraph nodes."""

    # Incoming request info
    query: str
    conversation_id: Optional[str]
    system_prompt: Optional[str]
    history: List[Dict[str, str]]

    # Classification node outputs
    request_type: str  # "direct_chat", "rag_retrieval", "tool_execution"
    needs_retrieval: bool
    classification_reason: Optional[str]

    # Retrieval node outputs
    retrieved_chunks: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]

    # Generation node outputs
    response_content: str
    error: Optional[str]
