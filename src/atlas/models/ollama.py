import json
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from atlas.models.base import ModelClient
from atlas.models.errors import (
    ModelInvalidOutputError,
    ModelTimeoutError,
    ModelUnavailableError,
)


T = TypeVar("T", bound=BaseModel)


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
    ) -> T:
        payload = {
            "model": self._model,
            "stream": False,
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

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds
            ) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )

                response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise ModelTimeoutError(
                "Model generation timed out."
            ) from exc

        except httpx.HTTPError as exc:
            raise ModelUnavailableError(
                "Unable to communicate with model service."
            ) from exc

        try:
            response_data = response.json()
            raw_content = response_data["message"]["content"]

            parsed_json = json.loads(raw_content)

            return output_schema.model_validate(parsed_json)

        except (
            KeyError,
            json.JSONDecodeError,
            ValidationError,
            TypeError,
        ) as exc:
            raise ModelInvalidOutputError(
                "Model returned output that violated the expected schema."
            ) from exc