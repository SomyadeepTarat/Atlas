import pytest

from atlas.models.service import (
    ResearchModelService,
)
from atlas.schemas.model import (
    ResearchPreviewResponse,
)
from tests.fakes.model import FakeModelClient


@pytest.mark.asyncio
async def test_research_service_returns_preview():
    expected = ResearchPreviewResponse(
        answer="RAG retrieves external context.",
        key_points=[
            "Retrieval happens before generation.",
            "Retrieved context grounds the model.",
        ],
        confidence=0.9,
    )

    fake_model = FakeModelClient(expected)

    service = ResearchModelService(fake_model)

    result = await service.create_preview("What is RAG?")

    assert result.output == expected
    assert result.metadata.provider == "fake"
