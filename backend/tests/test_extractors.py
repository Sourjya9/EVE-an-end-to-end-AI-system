"""
Unit Tests for Document Text Extractors.
"""

import pytest

from app.ai.rag.extractors import (
    DocumentExtractionError,
    clean_text,
    extract_document_text,
)


def test_clean_text_whitespace_and_newlines():
    raw = "Hello   world!\r\n\r\n\n\nThis is    a test.\xa0"
    cleaned = clean_text(raw)
    assert cleaned == "Hello world!\n\nThis is a test."


def test_extract_txt_file():
    sample_content = b"Architecture: FastAPI + Next.js + PostgreSQL"
    text, file_type = extract_document_text("architecture.txt", sample_content)
    assert file_type == "txt"
    assert "FastAPI" in text


def test_extract_markdown_file():
    sample_md = b"# Title\n\n- Point 1\n- Point 2"
    text, file_type = extract_document_text("guide.md", sample_md)
    assert file_type == "md"
    assert "Point 1" in text


def test_unsupported_extension():
    with pytest.raises(DocumentExtractionError):
        # Even if attempted as txt, non-decodable invalid binary will raise
        extract_document_text("unsupported.bin_data", b"\x80\x81\xfe\xff" * 100)
