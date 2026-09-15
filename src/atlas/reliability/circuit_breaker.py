import asyncio
from collections.abc import (
    Awaitable,
    Callable,
)
from enum import StrEnum
from time import monotonic
from typing import TypeVar

from atlas.models.errors import (
    ModelTimeoutError,
    ModelUnavailableError,
)
from atlas.reliability.errors import (
    CircuitOpenError,
)

FailurePredicate = Callable[
    [Exception],
    bool,
]


class CircuitState(StrEnum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


T = TypeVar("T")


class CircuitBreaker:
    def __init__(
        self,
        *,
        name: str,
        failure_threshold: int,
        recovery_seconds: float,
        counts_as_failure: FailurePredicate,
    ) -> None:
        ...
        self._counts_as_failure = counts_as_failure

        if failure_threshold < 1:
            raise ValueError("failure_threshold must be >= 1")

        self._name = name
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds

        self._state = CircuitState.CLOSED

        self._failures = 0

        self._opened_at: float | None = None

        self._lock = asyncio.Lock()

    async def call(
        self,
        operation: Callable[..., Awaitable[T]],
        *args: object,
        **kwargs: object,
    ) -> T:
        await self._before_call()

        try:
            result = await operation(*args, **kwargs)
        except Exception as exc:
            if self._counts_as_failure(exc):
                await self._record_failure()
            raise
        else:
            await self._record_success()
            return result

    async def _before_call(
        self,
    ) -> None:
        async with self._lock:
            if self._state == CircuitState.CLOSED:
                return

        if self._state == CircuitState.OPEN:
            assert self._opened_at is not None

            elapsed = monotonic() - self._opened_at

            if elapsed >= self._recovery_seconds:
                self._state = CircuitState.HALF_OPEN

                return

            raise CircuitOpenError(f"Circuit '{self._name}' is open.")

        if self._state == CircuitState.HALF_OPEN:
            return

    async def _record_success(
        self,
    ) -> None:
        async with self._lock:
            self._failures = 0

        self._opened_at = None

        self._state = CircuitState.CLOSED

    async def _record_failure(
        self,
    ) -> None:
        async with self._lock:
            self._failures += 1

        if self._failures >= self._failure_threshold:
            self._state = CircuitState.OPEN

            self._opened_at = monotonic()

    @staticmethod
    def model_dependency_failure(
        exc: Exception,
    ) -> bool:
        return isinstance(
            exc,
            (
                ModelTimeoutError,
                ModelUnavailableError,
            ),
        )
