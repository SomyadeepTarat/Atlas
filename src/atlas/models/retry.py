import asyncio
import random
from dataclasses import replace
from typing import TypeVar

from pydantic import BaseModel

from atlas.models.base import ModelClient
from atlas.models.errors import ModelError
from atlas.models.types import ModelResult

T = TypeVar("T", bound=BaseModel)


class RetryModelClient(ModelClient):
    def __init__(
        self,
        inner: ModelClient,
        *,
        max_attempts: int = 2,
        base_delay_seconds: float = 0.5,
        max_delay_seconds: float = 4.0,
        jitter_ratio: float = 0.2,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self._inner = inner
        self._max_attempts = max_attempts
        self._base_delay_seconds = base_delay_seconds
        self._max_delay_seconds = max_delay_seconds
        self._jitter_ratio = jitter_ratio

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        last_error: ModelError | None = None

        for attempt in range(
            1,
            self._max_attempts + 1,
        ):
            try:
                result = await self._inner.generate_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    output_schema=output_schema,
                )

                metadata = replace(
                    result.metadata,
                    attempts=attempt,
                )

                return replace(
                    result,
                    metadata=metadata,
                )

            except ModelError as exc:
                last_error = exc

                if not exc.retryable:
                    raise

                if attempt >= self._max_attempts:
                    raise

                delay = min(
                    self._base_delay_seconds * (2 ** (attempt - 1)),
                    self._max_delay_seconds,
                )

                jitter = delay * self._jitter_ratio

                delay += random.uniform(
                    -jitter,
                    jitter,
                )

                await asyncio.sleep(max(delay, 0.0))

        assert last_error is not None
        raise last_error

    async def is_ready(self) -> bool:
        return await self._inner.is_ready()
