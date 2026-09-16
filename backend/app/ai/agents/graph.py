r"""
LangGraph StateGraph Assembly.

Assembles and compiles Eve\'s decision-making state machine:
  [START] -> classify_request -> (conditional: needs_retrieval?)
               /            \
             [YES]          [NO]
               |              |
         retrieve_context     |
               \              /
                v            v
               generate_response -> [END]
"""

from typing import Any

from langgraph.graph import END, StateGraph  # type: ignore[import-untyped]
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.nodes import (
    classify_request,
    generate_response,
    retrieve_context,
)
from app.ai.agents.state import AgentState


def route_after_classification(state: AgentState) -> str:
    """Conditional router determining next step based on retrieval requirement."""
    if state.get("needs_retrieval", False):
        return "retrieve_context"
    return "generate_response"


def build_eve_graph(session: AsyncSession | None = None):
    """
    Constructs and compiles the LangGraph StateGraph.
    Passes database session closure to retrieve_context node when provided.
    """
    workflow = StateGraph(AgentState)

    # 1. Add functional nodes
    workflow.add_node("classify_request", classify_request)

    async def retrieve_context_wrapper(state: AgentState) -> dict[str, Any]:
        return await retrieve_context(state, session=session)

    workflow.add_node("retrieve_context", retrieve_context_wrapper)
    workflow.add_node("generate_response", generate_response)

    # 2. Define edges
    workflow.set_entry_point("classify_request")

    workflow.add_conditional_edges(
        "classify_request",
        route_after_classification,
        {
            "retrieve_context": "retrieve_context",
            "generate_response": "generate_response",
        },
    )

    workflow.add_edge("retrieve_context", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()


async def execute_agent_workflow(
    query: str,
    conversation_id: str | None = None,
    history: list[dict[str, str]] | None = None,
    system_prompt: str | None = None,
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    """
    Convenience runner executing the complete LangGraph agent loop.
    Returns final state dictionary containing response_content, citations, and execution metadata.
    """
    initial_state: AgentState = {
        "query": query,
        "conversation_id": conversation_id,
        "system_prompt": system_prompt,
        "history": history or [],
        "request_type": "unknown",
        "needs_retrieval": False,
        "classification_reason": None,
        "retrieved_chunks": [],
        "citations": [],
        "response_content": "",
        "error": None,
    }

    graph = build_eve_graph(session=session)
    final_state = await graph.ainvoke(initial_state)
    return final_state
