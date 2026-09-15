"""
Semantic Search & Retrieval Router.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.rag.embeddings import jina_client
from app.ai.rag.retriever import retriever
from app.db.session import get_db
from app.schemas.rag import SearchRequest, SearchResponse

router = APIRouter(prefix="/api", tags=["RAG"])


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes semantic similarity search over pgvector chunk embeddings.
    Returns ranked chunk matches with similarity scores.
    """
    query_vector = await jina_client.embed_query(request.query)
    results = await retriever.search(
        session=db,
        query_embedding=query_vector,
        top_k=request.top_k,
        document_id=request.document_id,
    )
    return SearchResponse(
        query=request.query,
        total_results=len(results),
        results=results,
    )
