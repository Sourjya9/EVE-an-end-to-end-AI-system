"""
Unit Tests for Document Chunking.
"""

from app.ai.rag.chunking import recursive_split_text


def test_empty_text_returns_empty_chunks():
    assert recursive_split_text("") == []
    assert recursive_split_text("   \n\t  ") == []


def test_short_text_single_chunk():
    text = "Eve is a production AI assistant built with FastAPI and LangGraph."
    chunks = recursive_split_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) == 1
    assert chunks[0].content == text
    assert chunks[0].index == 0


def test_long_text_splits_at_natural_boundaries():
    para1 = "This is the first paragraph describing the architecture of Eve."
    para2 = "This is the second paragraph covering pgvector and semantic retrieval."
    para3 = "This is the third paragraph detailing the Next.js frontend."
    full_text = f"{para1}\n\n{para2}\n\n{para3}"

    chunks = recursive_split_text(full_text, chunk_size=80, chunk_overlap=15)
    assert len(chunks) >= 3
    # Verify chunks contain meaningful text
    for chunk in chunks:
        assert len(chunk.content) > 0
        assert chunk.end_char > chunk.start_char


def test_chunk_overlap_present():
    text = "WordOne WordTwo WordThree WordFour WordFive WordSix WordSeven WordEight WordNine WordTen"
    chunks = recursive_split_text(text, chunk_size=40, chunk_overlap=15)
    assert len(chunks) > 1
    # Check that adjacent chunks have character overlap
    assert chunks[1].start_char < chunks[0].end_char
