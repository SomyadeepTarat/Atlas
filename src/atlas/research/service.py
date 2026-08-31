from atlas.models.service import (
    ResearchModelService,
)
from atlas.models.types import ModelResult
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
        chunks = self._retrieval.search(question)

        context = build_context(chunks)

        return await self._model.answer_from_context(
            question=question,
            context=context,
        )
