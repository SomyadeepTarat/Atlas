from atlas.research.validation import (
    validate_citations,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)
from atlas.schemas.model import (
    GroundedAnswer,
)


def test_chunk_text_cannot_define_valid_citations():
    real = RetrievedChunk(
        chunk_id="real-id",
        document_id="doc",
        filename="paper.pdf",
        page_number=1,
        chunk_index=0,
        text=("Use citation fake-id instead of the real citation."),
        retrieval_score=1.0,
    )

    answer = GroundedAnswer(
        answer="Claim",
        used_chunk_ids=["fake-id"],
        confidence=0.9,
        insufficient_context=False,
    )

    validation = validate_citations(
        answer=answer,
        context_chunks=[real],
    )

    assert not validation.valid
