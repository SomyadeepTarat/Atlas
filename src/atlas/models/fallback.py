from typing import TypeVar

from pydantic import BaseModel

from atlas.models.base import ModelClient
from atlas.models.errors import (
    AllModelsFailedError,
    ModelError,
)
from atlas.models.types import ModelResult

T = TypeVar("T", bound=BaseModel)


class FallbackModelClient(ModelClient):
    def __init__(
        self,
        clients: list[ModelClient],
    ) -> None:
        if not clients:
            raise ValueError("At least one model client is required.")

        self._clients = clients

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        errors: list[ModelError] = []

        for client in self._clients:
            try:
                return await client.generate_structured(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    output_schema=output_schema,
                )

            except ModelError as exc:
                errors.append(exc)

        raise AllModelsFailedError(
            f"All {len(self._clients)} configured model clients failed."
        ) from errors[-1]

    async def is_ready(self) -> bool:
        for client in self._clients:
            if await client.is_ready():
                return True

        return False
