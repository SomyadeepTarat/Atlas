from atlas.models.base import ModelClient
from atlas.models.types import ModelResult
from atlas.schemas.model import (
    GroundedAnswer,
    ResearchPreviewResponse,
)

PREVIEW_SYSTEM_PROMPT = """
You are Atlas, a careful AI research assistant.

Your task is to answer the user's research question clearly and concisely.

You must:
- Provide a direct answer.
- Extract the most important key points.
- Avoid inventing facts.
- Express confidence honestly.
- Return output strictly matching the requested schema.
""".strip()


GROUNDED_SYSTEM_PROMPT = """
You are Atlas, a grounded AI research assistant.

You will receive:
1. A user question.
2. Retrieved context chunks.

You must answer using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not invent facts that are not supported by the context.
- Cite supporting chunks using their chunk IDs.
- Include only chunk IDs that directly support the answer.
- If the context is insufficient to answer the question reliably,
  set insufficient_context to true.
- If context is insufficient, clearly state that the provided evidence
  is not enough.
- Confidence must reflect how strongly the provided context supports
  the answer.
- Return output strictly matching the requested schema.
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
        """
        Generate a lightweight research preview directly from the model.

        This method does not use retrieval. It is primarily useful for
        testing the model runtime and for simple model-only responses.
        """

        user_prompt = f"""
Research question:

{question}

Provide a concise research preview.
""".strip()

        return await self._model_client.generate_structured(
            system_prompt=PREVIEW_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=ResearchPreviewResponse,
        )

    async def answer_from_context(
        self,
        *,
        question: str,
        context: str,
    ) -> ModelResult[GroundedAnswer]:
        """
        Generate an answer grounded exclusively in retrieved context.

        Retrieval itself is intentionally handled elsewhere. This service
        only receives already-prepared context and asks the model to reason
        over it.
        """

        user_prompt = f"""
Research question:

{question}

Retrieved context:

{context}

Answer the research question using only the retrieved context.

Return the IDs of every chunk that directly supports your answer.
""".strip()

        return await self._model_client.generate_structured(
            system_prompt=GROUNDED_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_schema=GroundedAnswer,
        )
