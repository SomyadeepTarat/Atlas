import asyncio
import secrets
from dataclasses import replace
from typing import TypeVar

from pydantic import BaseModel

from atlas.models.base import (
    ModelClient,
)
from atlas.models.errors import (
    ModelError,
)
from atlas.models.types import (
    ModelResult,
)
from atlas.telemetry.tracing import (
    get_langfuse,
    tracer,
)

_jitter_random = secrets.SystemRandom()

T = TypeVar(
    "T",
    bound=BaseModel,
)


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
        langfuse = get_langfuse()

        last_error: ModelError | None = None

        with langfuse.start_as_current_observation(
            name="model-generation",
            as_type="generation",
            input={
                "system_prompt": (system_prompt),
                "user_prompt": (user_prompt),
                "output_schema": (output_schema.__name__),
            },
        ) as generation:
            for attempt in range(
                1,
                self._max_attempts + 1,
            ):
                delay = 0.0

                with tracer.start_as_current_span("model.attempt") as span:
                    span.set_attribute(
                        ("atlas.retry.attempt"),
                        attempt,
                    )

                    span.set_attribute(
                        ("atlas.retry.max_attempts"),
                        self._max_attempts,
                    )

                    try:
                        result = await self._inner.generate_structured(
                            system_prompt=(system_prompt),
                            user_prompt=(user_prompt),
                            output_schema=(output_schema),
                        )

                        metadata = replace(
                            result.metadata,
                            attempts=(attempt),
                        )

                        final_result = replace(
                            result,
                            metadata=(metadata),
                        )

                        generation.update(
                            model=(final_result.metadata.model),
                            output=(final_result.output.model_dump()),
                            usage_details={
                                ("input_tokens"): (
                                    final_result.metadata.usage.input_tokens
                                ),
                                ("output_tokens"): (
                                    final_result.metadata.usage.output_tokens
                                ),
                            },
                            metadata={
                                "provider": (final_result.metadata.provider),
                                "attempts": (attempt),
                            },
                        )

                        span.set_attribute(
                            ("atlas.retry.success"),
                            True,
                        )

                        return final_result

                    except ModelError as exc:
                        last_error = exc

                        span.record_exception(exc)

                        span.set_attribute(
                            ("atlas.retry.success"),
                            False,
                        )

                        span.set_attribute(
                            ("atlas.retry.error_type"),
                            type(exc).__name__,
                        )

                        if not exc.retryable:
                            generation.update(
                                level="ERROR",
                                status_message=(str(exc)),
                            )

                            raise

                        if attempt >= self._max_attempts:
                            generation.update(
                                level="ERROR",
                                status_message=(str(exc)),
                            )

                            raise

                        delay = min(
                            (self._base_delay_seconds * (2 ** (attempt - 1))),
                            self._max_delay_seconds,
                        )

                        jitter = delay * self._jitter_ratio

                        if jitter > 0:
                            delay += _jitter_random.uniform(
                                -jitter,
                                jitter,
                            )

                        delay = max(
                            delay,
                            0.0,
                        )

                        span.set_attribute(
                            ("atlas.retry.delay_seconds"),
                            delay,
                        )

                await asyncio.sleep(delay)

        if last_error is None:
            raise RuntimeError("Retry loop exhausted without recording an error.")

        raise last_error

    async def is_ready(
        self,
    ) -> bool:
        return await self._inner.is_ready()
