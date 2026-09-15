from typing import TypeVar

from pydantic import BaseModel

from atlas.models.base import ModelClient
from atlas.models.types import ModelResult
from atlas.reliability.circuit_breaker import (
    CircuitBreaker,
)

T = TypeVar(
    "T",
    bound=BaseModel,
)


class CircuitBreakerModelClient(ModelClient):
    def __init__(
        self,
        inner: ModelClient,
        breaker: CircuitBreaker,
    ) -> None:
        self._inner = inner
        self._breaker = breaker

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        async def operation() -> ModelResult[T]:
            return await self._inner.generate_structured(
                system_prompt=(system_prompt),
                user_prompt=user_prompt,
                output_schema=(output_schema),
            )

        return await self._breaker.call(operation)

    async def is_ready(self) -> bool:
        return await self._inner.is_ready()
