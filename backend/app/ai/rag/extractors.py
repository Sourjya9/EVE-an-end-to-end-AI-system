"""
Document Text Extraction Utilities.

Extracts text from PDF, TXT, and Markdown formats with robust cleaning.
"""

import io
import re
from typing import Tuple
from app.core.logging import logger

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class DocumentExtractionError(Exception):
    """Raised when document parsing fails."""
    pass


def clean_text(text: str) -> str:
    """Normalizes whitespace, line endings, and cleans control characters."""
    if not text:
        return ""
    # Replace carriage returns
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-breaking spaces
    text = text.replace("\xa0", " ")
    # Replace multiple spaces with a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Collapse 3 or more newlines to two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_txt(content_bytes: bytes) -> str:
    """Decodes plain text or markdown files with fallback encodings."""
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return clean_text(content_bytes.decode(enc))
        except UnicodeDecodeError:
            continue
    raise DocumentExtractionError("Unable to decode text file with standard encodings.")


def extract_text_from_pdf(content_bytes: bytes) -> str:
    """Extracts text page-by-page from PDF files using pypdf."""
    if not PYPDF_AVAILABLE:
        raise DocumentExtractionError("pypdf library is not installed. PDF extraction unavailable.")

    try:
        reader = pypdf.PdfReader(io.BytesIO(content_bytes))
        extracted_pages = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(f"[Page {idx + 1}]\n" + page_text)

        full_text = "\n\n".join(extracted_pages)
        if not full_text.strip():
            logger.warning("PDF extraction yielded zero text characters (may be scanned image).")
            return ""
        return clean_text(full_text)
    except Exception as exc:
        raise DocumentExtractionError(f"Failed to extract PDF contents: {exc}") from exc


def extract_document_text(filename: str, content_bytes: bytes) -> Tuple[str, str]:
    """
    Infers file type from filename extension and extracts cleaned plain text.
    Returns tuple of (cleaned_text, file_type).
    """
    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(content_bytes), "pdf"
    elif lower_name.endswith((".md", ".markdown")):
        return extract_text_from_txt(content_bytes), "md"
    elif lower_name.endswith((".txt", ".text", ".log", ".csv")):
        return extract_text_from_txt(content_bytes), "txt"
    else:
        # Default attempt as plain text
        try:
            return extract_text_from_txt(content_bytes), "txt"
        except Exception:
            raise DocumentExtractionError(f"Unsupported file format for '{filename}'. Supported: PDF, TXT, MD.")
