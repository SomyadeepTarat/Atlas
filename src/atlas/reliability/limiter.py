import asyncio
from collections.abc import (
    AsyncIterator,
)
from contextlib import (
    asynccontextmanager,
)
from typing import (
    TypeVar,
)

from pydantic import BaseModel

from atlas.models.base import ModelClient
from atlas.models.types import ModelResult

T = TypeVar("T", bound=BaseModel)


class ConcurrencyLimiter:
    def __init__(
        self,
        limit: int,
    ) -> None:
        if limit < 1:
            raise ValueError("limit must be at least 1")

        self._semaphore = asyncio.Semaphore(limit)

    @asynccontextmanager
    async def slot(
        self,
    ) -> AsyncIterator[None]:
        async with self._semaphore:
            yield


class LimitedModelClient(ModelClient):
    def __init__(
        self,
        inner: ModelClient,
        limiter: ConcurrencyLimiter,
    ) -> None:
        self._inner = inner
        self._limiter = limiter

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        async with self._limiter.slot():
            return await self._inner.generate_structured(
                system_prompt=(system_prompt),
                user_prompt=user_prompt,
                output_schema=(output_schema),
            )

    async def is_ready(self) -> bool:
        return await self._inner.is_ready()
