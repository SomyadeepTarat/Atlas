from atlas.retrieval.context import (
    build_context,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)


def test_context_contains_source_metadata():
    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        filename="paper.pdf",
        page_number=4,
        chunk_index=2,
        text="Important evidence.",
        retrieval_score=0.91,
    )

    context = build_context([chunk])

    assert "chunk-1" in context
    assert "paper.pdf" in context
    assert "page 4" in context
    assert "Important evidence." in context
