from atlas.research.validation import (
    validate_citations,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)
from atlas.schemas.model import (
    GroundedAnswer,
)


def make_chunk(
    chunk_id: str,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc",
        filename="paper.pdf",
        page_number=1,
        chunk_index=0,
        text="evidence",
        retrieval_score=0.95,
    )


def test_valid_citation():
    answer = GroundedAnswer(
        answer="Supported claim",
        used_chunk_ids=["chunk-1"],
        confidence=0.9,
        insufficient_context=False,
    )

    result = validate_citations(
        answer=answer,
        context_chunks=[make_chunk("chunk-1")],
    )

    assert result.valid


def test_invalid_citation():
    answer = GroundedAnswer(
        answer="Unsupported",
        used_chunk_ids=["fake"],
        confidence=0.8,
        insufficient_context=False,
    )

    result = validate_citations(
        answer=answer,
        context_chunks=[make_chunk("real")],
    )

    assert not result.valid
    assert result.invalid_chunk_ids == ["fake"]


def test_answer_requires_citation():
    answer = GroundedAnswer(
        answer="Claim.",
        used_chunk_ids=[],
        confidence=0.8,
        insufficient_context=False,
    )

    result = validate_citations(
        answer=answer,
        context_chunks=[make_chunk("chunk-1")],
    )

    assert not result.valid


def test_insufficient_context_can_have_no_citations():
    answer = GroundedAnswer(
        answer=("The supplied context does not answer this question."),
        used_chunk_ids=[],
        confidence=0.2,
        insufficient_context=True,
    )

    result = validate_citations(
        answer=answer,
        context_chunks=[],
    )

    assert result.valid
