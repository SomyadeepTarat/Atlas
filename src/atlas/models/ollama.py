from __future__ import annotations

import json
from time import monotonic
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from atlas.models.errors import (
    ModelInvalidOutputError,
    ModelTimeoutError,
    ModelUnavailableError,
)
from atlas.models.types import (
    ModelMetadata,
    ModelResult,
    ModelTimings,
    ModelUsage,
)


OutputT = TypeVar(
    "OutputT",
    bound=BaseModel,
)


def nanoseconds_to_seconds(
    value: int | None,
) -> float | None:
    if value is None:
        return None

    return value / 1_000_000_000


class OllamaModelClient:
    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = (
            timeout_seconds
        )

    async def _generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        format_schema: dict[str, Any],
    ) -> dict[str, Any]:
        payload = {
            "model": self._model,
            "stream": False,
            "format": format_schema,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        }

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds,
            ) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )

                response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise ModelTimeoutError(
                "Ollama request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise ModelUnavailableError(
                "Ollama returned an "
                f"HTTP {exc.response.status_code} "
                "response."
            ) from exc

        except httpx.RequestError as exc:
            raise ModelUnavailableError(
                "Could not connect to Ollama."
            ) from exc

        return response.json()

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[OutputT],
    ) -> ModelResult[OutputT]:
        started_at = monotonic()

        response = await self._generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            format_schema=(
                output_schema.model_json_schema()
            ),
        )

        message = response.get(
            "message"
        )

        if not isinstance(
            message,
            dict,
        ):
            raise ModelInvalidOutputError(
                "Ollama response did not "
                "contain a message object."
            )

        content = message.get(
            "content"
        )

        if not isinstance(
            content,
            str,
        ):
            raise ModelInvalidOutputError(
                "Ollama response did not "
                "contain textual content."
            )

        try:
            raw_output = json.loads(
                content
            )

        except json.JSONDecodeError as exc:
            raise ModelInvalidOutputError(
                "Ollama returned invalid JSON."
            ) from exc

        try:
            output = (
                output_schema.model_validate(
                    raw_output
                )
            )

        except ValidationError as exc:
            raise ModelInvalidOutputError(
                "Ollama output did not "
                "match the requested schema."
            ) from exc

        total_duration = (
            monotonic() - started_at
        )

        prompt_tokens = response.get(
            "prompt_eval_count",
            0,
        )

        output_tokens = response.get(
            "eval_count",
            0,
        )

        usage = ModelUsage(
            input_tokens=(
                prompt_tokens
                if isinstance(
                    prompt_tokens,
                    int,
                )
                else 0
            ),
            output_tokens=(
                output_tokens
                if isinstance(
                    output_tokens,
                    int,
                )
                else 0
            ),
        )

        timings = ModelTimings(
            total_seconds=total_duration,
            load_seconds=(
                nanoseconds_to_seconds(
                    response.get(
                        "load_duration"
                    )
                )
            ),
            prompt_eval_seconds=(
                nanoseconds_to_seconds(
                    response.get(
                        "prompt_eval_duration"
                    )
                )
            ),
            generation_seconds=(
                nanoseconds_to_seconds(
                    response.get(
                        "eval_duration"
                    )
                )
            ),
        )

        metadata = ModelMetadata(
            provider="ollama",
            model=self._model,
            attempts=1,
            usage=usage,
            timings=timings,
        )

        return ModelResult(
            output=output,
            metadata=metadata,
        )