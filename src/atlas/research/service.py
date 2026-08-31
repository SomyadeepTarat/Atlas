from atlas.models.service import (
    ResearchModelService,
)
from atlas.models.types import ModelResult
from atlas.research.errors import InvalidCitationError
from atlas.research.validation import (
    validate_citations,
)
from atlas.retrieval.context import (
    build_context,
)
from atlas.retrieval.service import (
    RetrievalService,
)
from atlas.schemas.model import (
    GroundedAnswer,
)


class ResearchService:
    def __init__(
        self,
        *,
        retrieval: RetrievalService,
        model: ResearchModelService,
    ) -> None:
        self._retrieval = retrieval
        self._model = model

    async def answer(
        self,
        question: str,
    ) -> ModelResult[GroundedAnswer]:
        chunks = self._retrieval.retrieve_context(question)

        context = build_context(chunks)

        result = await self._model.answer_from_context(
            question=question,
            context=context,
        )

        validation = validate_citations(
            answer=result.output,
            context_chunks=chunks,
        )

        if not validation.valid:
            raise InvalidCitationError(
                f"Model returned unsupported chunk IDs: {validation.invalid_chunk_ids}"
            )

        return result
