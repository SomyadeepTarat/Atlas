import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from atlas.reliability.errors import (
    WorkflowDeadlineExceededError,
)


@asynccontextmanager
async def workflow_deadline(
    seconds: float,
) -> AsyncIterator[None]:
    try:
        async with asyncio.timeout(seconds):
            yield

    except TimeoutError as exc:
        raise WorkflowDeadlineExceededError(
            f"Research workflow exceeded {seconds:.1f} seconds."
        ) from exc
