"""
LangGraph Agent Nodes.

Individual, testable functional nodes for Eve's reasoning graph:
1. classify_request: Identifies user intent and determines if document retrieval is necessary.
2. retrieve_context: Generates query embeddings and queries pgvector.
3. generate_response: Produces a grounded or conversational response using Groq.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.state import AgentState
from app.ai.llm.groq_client import groq_client
from app.ai.rag.embeddings import jina_client
from app.ai.rag.retriever import retriever
from app.core.config import settings
from app.core.logging import logger
from app.core.observability.opik import opik_tracer


async def classify_request(state: AgentState) -> dict[str, Any]:
    """
    Classifies the user query into direct chat or RAG retrieval.
    Can be expanded in future to support tool calling or multi-hop routing.
    """
    with opik_tracer.trace_span("node_classify_request", {"query": state["query"]}):
        query = state["query"].lower().strip()

        # Simple high-speed heuristic: Greetings and basic questions don't need RAG
        greetings = [
            "hello",
            "hi",
            "hey",
            "who are you",
            "what can you do",
            "good morning",
            "good evening",
        ]
        if any(query.startswith(g) for g in greetings) or len(query.split()) <= 2:
            return {
                "request_type": "direct_chat",
                "needs_retrieval": False,
                "classification_reason": "Short conversational greeting or generic prompt",
            }

        # Knowledge or document retrieval triggers
        rag_keywords = [
            "document",
            "doc",
            "pdf",
            "file",
            "uploaded",
            "summary",
            "summarize",
            "search",
            "what does",
            "according to",
            "find",
            "explain",
            "policy",
            "contract",
            "spec",
            "report",
            "notes",
            "based on",
        ]
        needs_rag = any(kw in query for kw in rag_keywords)

        # By default in an assistant with documents, queries longer than 3 words
        # benefit from checking indexed knowledge unless explicitly conversational
        if not needs_rag and len(query.split()) > 3:
            needs_rag = True

        return {
            "request_type": "rag_retrieval" if needs_rag else "direct_chat",
            "needs_retrieval": needs_rag,
            "classification_reason": "Query contains information-seeking intent"
            if needs_rag
            else "Direct conversation",
        }


async def retrieve_context(
    state: AgentState, session: AsyncSession | None = None
) -> dict[str, Any]:
    """
    Generates embedding for the query and retrieves relevant document chunks from PostgreSQL.
    """
    with opik_tracer.trace_span("node_retrieve_context", {"query": state["query"]}):
        if not state.get("needs_retrieval", False) or session is None:
            return {"retrieved_chunks": [], "citations": []}

        try:
            query_vector = await jina_client.embed_query(state["query"])
            search_results = await retriever.search(
                session=session,
                query_embedding=query_vector,
                top_k=settings.RAG_TOP_K,
            )

            retrieved_chunks: list[dict[str, Any]] = []
            citations: list[dict[str, Any]] = []

            for item in search_results:
                chunk_dict = item.model_dump()
                retrieved_chunks.append(chunk_dict)
                citations.append(
                    {
                        "document_id": item.document_id,
                        "filename": item.filename,
                        "chunk_index": item.chunk_index,
                        "score": item.score,
                        "snippet": item.content[:200]
                        + ("..." if len(item.content) > 200 else ""),
                    }
                )

            logger.info(
                f"Retrieved {len(retrieved_chunks)} relevant context chunks for query."
            )
            return {
                "retrieved_chunks": retrieved_chunks,
                "citations": citations,
            }
        except Exception as exc:
            logger.error(f"Error in retrieve_context node: {exc}")
            return {
                "retrieved_chunks": [],
                "citations": [],
                "error": f"Retrieval failed: {exc}",
            }


async def generate_response(state: AgentState) -> dict[str, Any]:
    """
    Constructs the prompt and generates the response using Groq LLM.
    If context chunks were retrieved, grounds the answer in those chunks.
    """
    with opik_tracer.trace_span(
        "node_generate_response",
        {"chunks_count": len(state.get("retrieved_chunks", []))},
    ):
        chunks = state.get("retrieved_chunks", [])
        system_base = state.get("system_prompt") or (
            "You are Eve, an intelligent, helpful, and concise AI assistant. "
            "Respond accurately and politely. When provided with context excerpts from uploaded documents, "
            "ground your response strictly in the context and cite relevant sources."
        )

        messages: list[dict[str, str]] = []

        if chunks:
            context_blocks = []
            for c in chunks:
                context_blocks.append(
                    f"--- Source: {c['filename']} (Chunk #{c['chunk_index']}) ---\n{c['content']}"
                )
            full_context = "\n\n".join(context_blocks)

            rag_system_prompt = (
                f"{system_base}\n\n"
                f"RELEVANT CONTEXT FROM USER DOCUMENTS:\n"
                f"{full_context}\n\n"
                f"Instructions: Use the above context to answer the user's question. "
                f"If the context does not contain enough information to answer, state clearly what you do not know."
            )
            messages.append({"role": "system", "content": rag_system_prompt})
        else:
            messages.append({"role": "system", "content": system_base})

        # Append prior conversational turns
        for h in state.get("history", []):
            messages.append({"role": h["role"], "content": h["content"]})

        # Append current user query
        messages.append({"role": "user", "content": state["query"]})

        try:
            reply = await groq_client.generate_response(messages)
            return {
                "response_content": reply,
                "error": None,
            }
        except Exception as exc:
            logger.error(f"Error in generate_response node: {exc}")
            return {
                "response_content": "I apologize, but I encountered an issue generating a response. Please check the backend logs or try again.",
                "error": str(exc),
            }
