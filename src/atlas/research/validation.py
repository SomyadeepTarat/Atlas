from dataclasses import dataclass

from atlas.retrieval.types import (
    RetrievedChunk,
)
from atlas.schemas.model import (
    GroundedAnswer,
)


@dataclass(frozen=True)
class CitationValidationResult:
    valid: bool
    invalid_chunk_ids: list[str]


def validate_citations(
    *,
    answer: GroundedAnswer,
    context_chunks: list[RetrievedChunk],
) -> CitationValidationResult:
    allowed_ids = {chunk.chunk_id for chunk in context_chunks}

    invalid_ids = [
        chunk_id for chunk_id in answer.used_chunk_ids if chunk_id not in allowed_ids
    ]

    missing_required_citation = (
        not answer.insufficient_context
        and bool(answer.answer.strip())
        and not answer.used_chunk_ids
    )

    valid = not invalid_ids and not missing_required_citation

    return CitationValidationResult(
        valid=valid,
        invalid_chunk_ids=invalid_ids,
    )
