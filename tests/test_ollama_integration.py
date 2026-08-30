import os

import pytest

from atlas.core.config import get_settings
from atlas.models.ollama import OllamaModelClient
from atlas.schemas.model import (
    ResearchPreviewResponse,
)

RUN_INTEGRATION = os.getenv("RUN_INTEGRATION_TESTS") == "1"


@pytest.mark.skipif(
    not RUN_INTEGRATION,
    reason=("Set RUN_INTEGRATION_TESTS=1 to run Ollama integration tests."),
)
@pytest.mark.asyncio
async def test_ollama_structured_generation():
    settings = get_settings()

    client = OllamaModelClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=(settings.ollama_timeout_seconds),
    )

    result = await client.generate_structured(
        system_prompt=("Return the required structure."),
        user_prompt=("Explain RAG very briefly."),
        output_schema=ResearchPreviewResponse,
    )

    assert result.output.answer
    assert result.output.key_points
    assert 0 <= result.output.confidence <= 1
    assert result.metadata.provider == "ollama"
