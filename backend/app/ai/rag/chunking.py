"""
Document Text Chunking Engine.

Recursively splits document text into semantic chunks while respecting
sentence boundaries, character limits, and overlap thresholds.
"""

from typing import Any

from app.core.config import settings


class TextChunk:
    """Represents a discrete chunk of text with position metadata."""

    def __init__(
        self,
        index: int,
        content: str,
        start_char: int,
        end_char: int,
        metadata: dict[str, Any] | None = None,
    ):
        self.index = index
        self.content = content
        self.start_char = start_char
        self.end_char = end_char
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "content": self.content,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "metadata": self.metadata,
        }


def recursive_split_text(
    text: str,
    chunk_size: int = settings.RAG_CHUNK_SIZE,
    chunk_overlap: int = settings.RAG_CHUNK_OVERLAP,
    separators: list[str] | None = None,
) -> list[TextChunk]:
    """
    Splits text into chunks of maximum length chunk_size with chunk_overlap.
    Tries splitting on paragraphs, then lines, then sentences, then spaces.
    """
    if separators is None:
        separators = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    if not text.strip():
        return []

    # If text is already smaller than chunk_size, return it directly
    if len(text) <= chunk_size:
        return [
            TextChunk(index=0, content=text.strip(), start_char=0, end_char=len(text))
        ]

    chunks: list[TextChunk] = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        # If we reached the end of text, add the final chunk and exit
        if end >= len(text):
            chunk_str = text[start:end].strip()
            if chunk_str:
                chunks.append(
                    TextChunk(
                        index=chunk_index,
                        content=chunk_str,
                        start_char=start,
                        end_char=end,
                    )
                )
            break

        # Look for the best separator within the target window
        split_idx = -1
        for sep in separators:
            if not sep:
                continue
            # Search backwards from the end window
            pos = text.rfind(sep, start, end)
            if pos != -1 and pos > start:
                split_idx = pos + len(sep)
                break

        # Fallback to hard slice if no separator found
        if split_idx == -1 or split_idx <= start:
            split_idx = end

        chunk_str = text[start:split_idx].strip()
        if chunk_str:
            chunks.append(
                TextChunk(
                    index=chunk_index,
                    content=chunk_str,
                    start_char=start,
                    end_char=split_idx,
                )
            )
            chunk_index += 1

        # Advance start position taking overlap into account
        start = max(split_idx - chunk_overlap, start + 1)

    return chunks
