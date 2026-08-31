from atlas.models.base import ModelClient
from atlas.models.types import ModelResult
from atlas.schemas.model import (
    GroundedAnswer,
    ResearchPreviewResponse,
)

async def answer_from_context(
    self,
    *,
    question: str,
    context: str,
) -> ModelResult[GroundedAnswer]:
    system_prompt = """
You are Atlas, an evidence-grounded research assistant.

Answer using ONLY the supplied context.

Rules:
- Never use unsupported factual claims.
- Never invent information.
- If context is insufficient, say so.
- Return the IDs of chunks used.
- Chunk IDs appear before each context block.
- Do not cite chunk IDs that were not supplied.
""".strip()

    user_prompt = f"""
QUESTION:
{question}

CONTEXT:
{context}
""".strip()

    return await (
        self._model_client.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            output_schema=GroundedAnswer,
        )
    )
