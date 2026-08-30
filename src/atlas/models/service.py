from atlas.models.base import ModelClient
from atlas.models.types import ModelResult
from atlas.schemas.model import (
    ResearchPreviewResponse,
)

SYSTEM_PROMPT = """
You are Atlas, an evidence-oriented AI research assistant.

Your task in this stage is only to produce a preliminary response.

Rules:
- Be concise.
- Do not fabricate citations.
- Do not claim that you searched external sources.
- If uncertain, lower the confidence score.
- Return only information matching the required output schema.
""".strip()


class ResearchModelService:
    def __init__(
        self,
        model_client: ModelClient,
    ) -> None:
        self._model_client = model_client

    async def create_preview(
        self,
        question: str,
    ) -> ModelResult[ResearchPreviewResponse]:
        return await self._model_client.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=question,
            output_schema=(ResearchPreviewResponse),
        )
