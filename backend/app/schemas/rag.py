"""
RAG and Semantic Search Schemas.
"""

from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Query string to search for")
    top_k: int = Field(
        default=4, ge=1, le=20, description="Number of matching chunks to retrieve"
    )
    document_id: str | None = Field(
        default=None, description="Optional filter to specific document ID"
    )


class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    chunk_index: int
    content: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: list[SearchResultItem]
