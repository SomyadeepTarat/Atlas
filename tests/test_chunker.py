import pytest

from atlas.retrieval.chunker import (
    TextChunker,
)
from atlas.retrieval.types import (
    DocumentPage,
)


def test_chunker_creates_multiple_chunks():
    page = DocumentPage(
        document_id="doc-1",
        filename="test.pdf",
        page_number=1,
        text="A" * 2500,
    )

    chunker = TextChunker(
        chunk_size=1000,
        overlap=100,
    )

    chunks = chunker.chunk_pages([page])

    assert len(chunks) >= 2

    assert all(chunk.document_id == "doc-1" for chunk in chunks)


def test_chunker_preserves_page_number():
    page = DocumentPage(
        document_id="doc",
        filename="test.pdf",
        page_number=7,
        text="hello world " * 100,
    )

    chunker = TextChunker(
        chunk_size=300,
        overlap=50,
    )

    chunks = chunker.chunk_pages([page])

    assert all(chunk.page_number == 7 for chunk in chunks)


def test_overlap_must_be_smaller_than_chunk():
    with pytest.raises(ValueError):
        TextChunker(
            chunk_size=100,
            overlap=100,
        )
