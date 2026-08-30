from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

from atlas.models.types import ModelResult

T = TypeVar("T", bound=BaseModel)


class ModelClient(ABC):
    @abstractmethod
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[T],
    ) -> ModelResult[T]:
        """Generate and validate structured model output."""

    @abstractmethod
    async def is_ready(self) -> bool:
        """Return whether this model provider is ready for inference."""
