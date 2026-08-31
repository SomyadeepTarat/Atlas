from atlas.retrieval.context import (
    select_context_chunks,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)


def chunk(
    idx: int,
    text: str,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=str(idx),
        document_id="doc",
        filename="paper.pdf",
        page_number=1,
        chunk_index=idx,
        text=text,
        retrieval_score=1.0,
    )


def test_context_respects_max_chunks():
    chunks = [
        chunk(1, "a"),
        chunk(2, "b"),
        chunk(3, "c"),
    ]

    selected = select_context_chunks(
        chunks,
        max_chunks=2,
        max_chars=100,
    )

    assert len(selected) == 2


def test_context_respects_character_budget():
    chunks = [
        chunk(1, "a" * 50),
        chunk(2, "b" * 50),
    ]

    selected = select_context_chunks(
        chunks,
        max_chunks=5,
        max_chars=60,
    )

    assert len(selected) == 1
