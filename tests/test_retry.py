from typing import TypeVar

import pytest
from pydantic import BaseModel

from atlas.models.base import ModelClient
from atlas.models.errors import (
    ModelError,
    ModelTimeoutError,
)
from atlas.models.retry import RetryModelClient
from atlas.models.types import (
    ModelMetadata,
    ModelResult,
    ModelTimings,
    ModelUsage,
)

T = TypeVar("T", bound=BaseModel)


class EventuallySuccessfulClient(ModelClient):
    def __init__(self) -> None:
        self.calls = 0

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        self.calls += 1

        if self.calls == 1:
            raise ModelTimeoutError("Temporary timeout")

        output = output_schema.model_validate(
            {
                "answer": "Success",
                "key_points": ["Recovered"],
                "confidence": 0.9,
            }
        )

        return ModelResult(
            output=output,
            metadata=ModelMetadata(
                provider="test",
                model="test-model",
                attempts=1,
                usage=ModelUsage(
                    input_tokens=1,
                    output_tokens=1,
                ),
                timings=ModelTimings(total_seconds=0.01),
            ),
        )

    async def is_ready(self) -> bool:
        return True


class PermanentModelError(ModelError):
    retryable = False


class PermanentlyFailingClient(ModelClient):
    def __init__(self) -> None:
        self.calls = 0

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        self.calls += 1

        raise PermanentModelError("Permanent failure")

    async def is_ready(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_retry_recovers_from_timeout():
    inner = EventuallySuccessfulClient()

    client = RetryModelClient(
        inner,
        max_attempts=2,
        base_delay_seconds=0,
        jitter_ratio=0,
    )

    from atlas.schemas.model import ResearchPreviewResponse

    result = await client.generate_structured(
        system_prompt="test",
        user_prompt="test",
        output_schema=ResearchPreviewResponse,
    )

    assert inner.calls == 2
    assert result.metadata.attempts == 2
    assert result.output.answer == "Success"


@pytest.mark.asyncio
async def test_retry_does_not_retry_permanent_error():
    inner = PermanentlyFailingClient()

    client = RetryModelClient(
        inner,
        max_attempts=5,
        base_delay_seconds=0,
        jitter_ratio=0,
    )

    from atlas.schemas.model import ResearchPreviewResponse

    with pytest.raises(PermanentModelError):
        await client.generate_structured(
            system_prompt="test",
            user_prompt="test",
            output_schema=ResearchPreviewResponse,
        )

    assert inner.calls == 1
