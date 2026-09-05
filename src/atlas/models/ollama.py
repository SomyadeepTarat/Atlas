import json
from time import monotonic
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from atlas.models.base import ModelClient
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

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        payload = {
            "model": self._model,
            "stream": False,
            "think": False,
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
            "format": output_schema.model_json_schema(),
            "options": {
                "temperature": 0,
            },
        }

        started_at = monotonic()

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )

                response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise ModelTimeoutError("Model generation timed out.") from exc

        except httpx.HTTPError as exc:
            raise ModelUnavailableError("Unable to communicate with Ollama.") from exc

        total_seconds = monotonic() - started_at

        try:
            response_data = response.json()

            raw_content = response_data["message"]["content"]

            parsed_json = json.loads(raw_content)

            output = output_schema.model_validate(parsed_json)

        except (
            KeyError,
            json.JSONDecodeError,
            ValidationError,
            TypeError,
        ) as exc:
            raise ModelInvalidOutputError(
                "Model returned output that violated the expected schema."
            ) from exc

        input_tokens = response_data.get(
            "prompt_eval_count",
            0,
        )

        output_tokens = response_data.get(
            "eval_count",
            0,
        )

        usage = ModelUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )

        timings = ModelTimings(
            total_seconds=total_seconds,
            load_seconds=nanoseconds_to_seconds(response_data.get("load_duration")),
            prompt_eval_seconds=nanoseconds_to_seconds(
                response_data.get("prompt_eval_duration")
            ),
            generation_seconds=nanoseconds_to_seconds(
                response_data.get("eval_duration")
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
