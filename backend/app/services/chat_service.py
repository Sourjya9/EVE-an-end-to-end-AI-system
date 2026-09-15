"""
Chat & Conversation Orchestration Service.

Manages conversational sessions, message persistence, LangGraph execution,
and Server-Sent Events (SSE) streaming with source citations.
"""

import json
import time
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.ai.agents.graph import execute_agent_workflow, build_eve_graph
from app.ai.agents.nodes import classify_request, retrieve_context
from app.ai.llm.groq_client import groq_client
from app.core.config import settings
from app.core.logging import logger
from app.models.agent_run import AgentRun
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse, Citation, StreamChunk
from app.schemas.conversation import (
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse,
)


class ChatService:
    """Manages chat conversations, message persistence, and AI execution."""

    async def create_conversation(
        self,
        session: AsyncSession,
        title: Optional[str] = "New Conversation",
        user_id: Optional[str] = None,
    ) -> Conversation:
        """Initializes a new persistent conversation thread."""
        conv = Conversation(title=title or "New Conversation", user_id=user_id)
        session.add(conv)
        await session.commit()
        await session.refresh(conv)
        return conv

    async def list_conversations(
        self,
        session: AsyncSession,
        user_id: Optional[str] = None,
    ) -> List[ConversationResponse]:
        """Lists recent conversations with message counts."""
        # Query conversations and join message count
        query = (
            select(
                Conversation,
                func.count(Message.id).label("message_count"),
            )
            .outerjoin(Message, Conversation.id == Message.conversation_id)
            .group_by(Conversation.id)
            .order_by(Conversation.updated_at.desc())
        )
        if user_id:
            query = query.where(Conversation.user_id == user_id)

        result = await session.execute(query)
        rows = result.all()

        responses: List[ConversationResponse] = []
        for conv, count in rows:
            responses.append(
                ConversationResponse(
                    id=conv.id,
                    title=conv.title,
                    user_id=conv.user_id,
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    message_count=count,
                )
            )
        return responses

    async def get_conversation(
        self,
        session: AsyncSession,
        conversation_id: str,
    ) -> ConversationDetailResponse:
        """Retrieves full conversation details including chronological messages."""
        query = (
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id)
        )
        result = await session.execute(query)
        conv = result.scalar_one_or_none()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        messages = [MessageResponse.model_validate(m) for m in conv.messages]
        return ConversationDetailResponse(
            id=conv.id,
            title=conv.title,
            user_id=conv.user_id,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=messages,
        )

    async def delete_conversation(
        self,
        session: AsyncSession,
        conversation_id: str,
    ) -> bool:
        """Deletes a conversation and all its messages."""
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await session.execute(query)
        conv = result.scalar_one_or_none()
        if not conv:
            return False

        await session.delete(conv)
        await session.commit()
        return True

    async def process_chat(
        self,
        session: AsyncSession,
        chat_req: ChatRequest,
        user_id: Optional[str] = None,
    ) -> ChatResponse:
        """Processes a standard non-streaming chat request with persistence."""
        start_time = time.time()

        # 1. Get or create conversation
        if chat_req.conversation_id:
            query = select(Conversation).where(Conversation.id == chat_req.conversation_id)
            result = await session.execute(query)
            conv = result.scalar_one_or_none()
            if not conv:
                conv = await self.create_conversation(session, title=chat_req.message[:50], user_id=user_id)
        else:
            conv = await self.create_conversation(session, title=chat_req.message[:50], user_id=user_id)

        # 2. Persist incoming user message
        user_msg = Message(
            conversation_id=conv.id,
            role="user",
            content=chat_req.message,
        )
        session.add(user_msg)
        await session.flush()

        # 3. Load conversation history
        history_query = (
            select(Message)
            .where(Message.conversation_id == conv.id, Message.id != user_msg.id)
            .order_by(Message.created_at)
            .limit(10)
        )
        history_res = await session.execute(history_query)
        history_msgs = [
            {"role": m.role, "content": m.content}
            for m in history_res.scalars().all()
        ]

        # 4. Execute LangGraph workflow
        agent_result = await execute_agent_workflow(
            query=chat_req.message,
            conversation_id=conv.id,
            history=history_msgs,
            system_prompt=chat_req.system_prompt,
            session=session,
        )

        response_content = agent_result.get("response_content", "")
        raw_citations = agent_result.get("citations", [])

        citations = [
            Citation(
                document_id=c["document_id"],
                filename=c["filename"],
                chunk_index=c["chunk_index"],
                score=c["score"],
                snippet=c["snippet"],
            )
            for c in raw_citations
        ]

        # 5. Persist assistant message
        asst_msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content=response_content,
            citations=[c.model_dump() for c in citations] if citations else None,
        )
        session.add(asst_msg)

        # 6. Record AgentRun audit log
        latency = (time.time() - start_time) * 1000
        agent_run = AgentRun(
            conversation_id=conv.id,
            request_type=agent_result.get("request_type", "chat"),
            needs_retrieval=agent_result.get("needs_retrieval", False),
            retrieved_chunk_count=len(agent_result.get("retrieved_chunks", [])),
            latency_ms=round(latency, 2),
            execution_metadata={
                "classification_reason": agent_result.get("classification_reason"),
            },
        )
        session.add(agent_run)
        await session.commit()

        return ChatResponse(
            conversation_id=conv.id,
            message_id=asst_msg.id,
            role="assistant",
            content=response_content,
            citations=citations,
            created_at=asst_msg.created_at,
        )

    async def stream_chat(
        self,
        session: AsyncSession,
        chat_req: ChatRequest,
        user_id: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Streams response tokens and citations as Server-Sent Events (SSE).
        Format: data: {"delta": "...", "citations": [...], "conversation_id": "...", "done": false}\n\n
        """
        start_time = time.time()

        # 1. Conversation resolution
        if chat_req.conversation_id:
            query = select(Conversation).where(Conversation.id == chat_req.conversation_id)
            result = await session.execute(query)
            conv = result.scalar_one_or_none()
            if not conv:
                conv = await self.create_conversation(session, title=chat_req.message[:50], user_id=user_id)
        else:
            conv = await self.create_conversation(session, title=chat_req.message[:50], user_id=user_id)

        # 2. Persist user message
        user_msg = Message(
            conversation_id=conv.id,
            role="user",
            content=chat_req.message,
        )
        session.add(user_msg)
        await session.commit()

        # 3. Step 1 of LangGraph: Classification & Retrieval
        state = {
            "query": chat_req.message,
            "conversation_id": conv.id,
            "system_prompt": chat_req.system_prompt,
            "history": [],
            "request_type": "unknown",
            "needs_retrieval": False,
            "classification_reason": None,
            "retrieved_chunks": [],
            "citations": [],
            "response_content": "",
            "error": None,
        }

        classification = await classify_request(state)  # type: ignore
        state.update(classification)

        if state["needs_retrieval"]:
            retrieval_res = await retrieve_context(state, session=session)  # type: ignore
            state.update(retrieval_res)

        citations = [
            Citation(
                document_id=c["document_id"],
                filename=c["filename"],
                chunk_index=c["chunk_index"],
                score=c["score"],
                snippet=c["snippet"],
            )
            for c in state.get("citations", [])
        ]

        # Emit initial event containing conversation_id and citations
        init_chunk = StreamChunk(
            delta="",
            citations=citations,
            conversation_id=conv.id,
            done=False,
        )
        yield f"data: {init_chunk.model_dump_json()}\n\n"

        # 4. Format messages for streaming from Groq
        system_base = chat_req.system_prompt or (
            "You are Eve, an intelligent, helpful, and concise AI assistant. "
            "When provided with context excerpts from uploaded documents, "
            "ground your response strictly in the context and cite relevant sources."
        )

        messages: List[dict] = []
        chunks = state.get("retrieved_chunks", [])
        if chunks:
            context_blocks = [
                f"--- Source: {c['filename']} (Chunk #{c['chunk_index']}) ---\n{c['content']}"
                for c in chunks
            ]
            rag_system_prompt = (
                f"{system_base}\n\n"
                f"RELEVANT CONTEXT FROM USER DOCUMENTS:\n"
                f"{chr(10).join(context_blocks)}\n\n"
                f"Instructions: Use the above context to answer the user's question accurately."
            )
            messages.append({"role": "system", "content": rag_system_prompt})
        else:
            messages.append({"role": "system", "content": system_base})

        messages.append({"role": "user", "content": chat_req.message})

        # 5. Stream tokens from Groq
        full_response_text = ""
        async for token in groq_client.stream_response(messages):
            full_response_text += token
            token_chunk = StreamChunk(
                delta=token,
                citations=None,
                conversation_id=conv.id,
                done=False,
            )
            yield f"data: {token_chunk.model_dump_json()}\n\n"

        # 6. Finalize and persist assistant message
        asst_msg = Message(
            conversation_id=conv.id,
            role="assistant",
            content=full_response_text,
            citations=[c.model_dump() for c in citations] if citations else None,
        )
        session.add(asst_msg)

        latency = (time.time() - start_time) * 1000
        agent_run = AgentRun(
            conversation_id=conv.id,
            request_type=state.get("request_type", "chat"),
            needs_retrieval=state.get("needs_retrieval", False),
            retrieved_chunk_count=len(chunks),
            latency_ms=round(latency, 2),
            execution_metadata={
                "classification_reason": state.get("classification_reason"),
            },
        )
        session.add(agent_run)
        await session.commit()

        # Emit completion event
        final_chunk = StreamChunk(
            delta="",
            citations=citations,
            conversation_id=conv.id,
            done=True,
        )
        yield f"data: {final_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"


chat_service = ChatService()
