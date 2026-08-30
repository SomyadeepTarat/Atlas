from typing import TypeVar

from pydantic import BaseModel

from atlas.models.base import ModelClient
from atlas.models.types import (
    ModelMetadata,
    ModelResult,
    ModelTimings,
    ModelUsage,
)

T = TypeVar("T", bound=BaseModel)


class FakeModelClient(ModelClient):
    def __init__(
        self,
        output: BaseModel,
        *,
        ready: bool = True,
    ) -> None:
        self._output = output
        self._ready = ready

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        output = output_schema.model_validate(self._output.model_dump())

        return ModelResult(
            output=output,
            metadata=ModelMetadata(
                provider="fake",
                model="fake-model",
                attempts=1,
                usage=ModelUsage(
                    input_tokens=10,
                    output_tokens=20,
                ),
                timings=ModelTimings(
                    total_seconds=0.01,
                ),
            ),
        )

    async def is_ready(self) -> bool:
        return self._ready
