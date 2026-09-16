"""
Document Ingestion & Management Service.

Handles document upload, file validation, text extraction, chunking,
embedding generation via Jina AI, and database persistence into PostgreSQL with pgvector.
"""

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.rag.chunking import recursive_split_text
from app.ai.rag.embeddings import jina_client
from app.ai.rag.extractors import DocumentExtractionError, extract_document_text
from app.core.config import settings
from app.core.logging import logger
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentResponse, DocumentUploadResponse


class DocumentService:
    """Orchestrates document lifecycle from ingestion to indexing."""

    async def ingest_document(
        self,
        session: AsyncSession,
        file: UploadFile,
        user_id: str | None = None,
    ) -> DocumentUploadResponse:
        """Processes an uploaded file into indexed vector chunks."""
        filename = file.filename or "unknown_document.txt"

        # 1. Read file bytes and validate size
        content_bytes = await file.read()
        if len(content_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024):.1f}MB.",
            )
        if len(content_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # 2. Extract and clean text
        try:
            text_content, file_type = extract_document_text(filename, content_bytes)
        except DocumentExtractionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract any readable text from document. Ensure file is not empty or scanned.",
            )

        # 3. Create Document record
        doc_record = Document(
            filename=filename,
            file_type=file_type,
            file_size_bytes=len(content_bytes),
            status="processing",
            user_id=user_id,
        )
        session.add(doc_record)
        await session.flush()  # Populates doc_record.id

        try:
            # 4. Chunk text recursively
            raw_chunks = recursive_split_text(
                text=text_content,
                chunk_size=settings.RAG_CHUNK_SIZE,
                chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            )

            if not raw_chunks:
                raise ValueError("Text chunking produced zero segments.")

            # 5. Compute vector embeddings in batch
            chunk_texts = [c.content for c in raw_chunks]
            embeddings = await jina_client.embed_texts(
                chunk_texts, task="retrieval.passage"
            )

            # 6. Save chunks with embeddings into PostgreSQL
            for idx, (c, emb) in enumerate(zip(raw_chunks, embeddings, strict=True)):
                chunk_record = DocumentChunk(
                    document_id=doc_record.id,
                    chunk_index=idx,
                    content=c.content,
                    embedding=emb,
                    metadata_json={
                        "filename": filename,
                        "start_char": c.start_char,
                        "end_char": c.end_char,
                    },
                )
                session.add(chunk_record)

            doc_record.status = "indexed"
            doc_record.chunk_count = len(raw_chunks)
            await session.commit()
            logger.info(
                f"Successfully indexed document '{filename}' with {len(raw_chunks)} chunks."
            )

            return DocumentUploadResponse(
                document_id=doc_record.id,
                filename=filename,
                status="indexed",
                message=f"Successfully indexed into {len(raw_chunks)} chunks.",
            )

        except Exception as exc:
            await session.rollback()
            doc_record.status = "failed"
            doc_record.error_message = str(exc)
            session.add(doc_record)
            await session.commit()
            logger.error(f"Failed to process and index document '{filename}': {exc}")
            raise HTTPException(
                status_code=500, detail=f"Document indexing failed: {exc}"
            ) from exc

    async def list_documents(
        self,
        session: AsyncSession,
        user_id: str | None = None,
    ) -> list[DocumentResponse]:
        """Lists all uploaded documents with indexing status."""
        query = select(Document).order_by(Document.created_at.desc())
        if user_id:
            query = query.where(Document.user_id == user_id)

        result = await session.execute(query)
        docs = result.scalars().all()
        return [DocumentResponse.model_validate(d) for d in docs]

    async def delete_document(
        self,
        session: AsyncSession,
        document_id: str,
    ) -> bool:
        """Deletes a document and all associated chunks via cascading foreign keys."""
        query = select(Document).where(Document.id == document_id)
        result = await session.execute(query)
        doc = result.scalar_one_or_none()
        if not doc:
            return False

        await session.delete(doc)
        await session.commit()
        logger.info(f"Deleted document {document_id} and its associated chunks.")
        return True


document_service = DocumentService()
