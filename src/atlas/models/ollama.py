from typing import TypeVar

import httpx
from opentelemetry.trace import (
    Status,
    StatusCode,
)
from pydantic import BaseModel

from atlas.models.base import ModelClient
from atlas.models.types import (
    ModelResult,
)
from atlas.telemetry.tracing import tracer

T = TypeVar("T", bound=BaseModel)


def nanoseconds_to_seconds(
    value: int | None,
) -> float | None:
    if value is None:
        return None

    return value / 1_000_000_000


class OllamaModelClient(ModelClient):
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    async def _generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        raise NotImplementedError

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        with tracer.start_as_current_span("model.generate") as span:
            span.set_attribute(
                "gen_ai.provider.name",
                "ollama",
            )

        span.set_attribute(
            "gen_ai.request.model",
            self._model,
        )

        span.set_attribute(
            "atlas.model.output_schema",
            output_schema.__name__,
        )

        try:
            result = await self._generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                output_schema=output_schema,
            )

        except Exception as exc:
            span.record_exception(exc)

            span.set_status(
                Status(
                    StatusCode.ERROR,
                    str(exc),
                )
            )

            raise

        span.set_attribute(
            "atlas.llm.input_tokens",
            result.metadata.usage.input_tokens,
        )

        span.set_attribute(
            "atlas.llm.output_tokens",
            result.metadata.usage.output_tokens,
        )

        span.set_attribute(
            "atlas.llm.total_seconds",
            result.metadata.timings.total_seconds,
        )

        return result

    async def is_ready(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self._base_url}/api/tags")

                response.raise_for_status()

                data = response.json()

        except (
            httpx.HTTPError,
            ValueError,
        ):
            return False

        models = data.get("models", [])

        return any(
            item.get("name") == self._model or item.get("model") == self._model
            for item in models
        )
