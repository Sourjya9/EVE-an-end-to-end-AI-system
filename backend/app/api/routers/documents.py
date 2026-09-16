"""
Document Ingestion & Management Router.
"""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import document_service

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Uploads a document (PDF, TXT, MD), extracts text, chunks it,
    computes Jina AI embeddings, and saves into PostgreSQL with pgvector.
    """
    return await document_service.ingest_document(session=db, file=file)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
):
    """Lists all uploaded documents with chunk counts and status."""
    return await document_service.list_documents(session=db)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Deletes a document and all its vector chunks."""
    success = await document_service.delete_document(
        session=db, document_id=document_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully", "id": document_id}
