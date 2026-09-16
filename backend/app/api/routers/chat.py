"""
Chat & Conversations Router.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.conversation import ConversationDetailResponse, ConversationResponse
from app.services.chat_service import chat_service

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse | None)
async def chat_endpoint(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Main chat endpoint. Supports standard JSON responses or Server-Sent Events (SSE) streaming.
    """
    if request.stream:
        return StreamingResponse(
            chat_service.stream_chat(session=db, chat_req=request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        return await chat_service.process_chat(session=db, chat_req=request)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations_endpoint(
    db: AsyncSession = Depends(get_db),
):
    """Lists recent conversation threads with message counts."""
    return await chat_service.list_conversations(session=db)


@router.get(
    "/conversations/{conversation_id}", response_model=ConversationDetailResponse
)
async def get_conversation_endpoint(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full conversation history and citations by conversation ID."""
    return await chat_service.get_conversation(
        session=db, conversation_id=conversation_id
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Deletes a conversation and its messages."""
    success = await chat_service.delete_conversation(
        session=db, conversation_id=conversation_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully", "id": conversation_id}
