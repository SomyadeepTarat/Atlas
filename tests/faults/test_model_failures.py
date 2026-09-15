from typing import Any

import pytest
from pydantic import BaseModel

from atlas.models.errors import (
    ModelInvalidOutputError,
    ModelTimeoutError,
    ModelUnavailableError,
)


class DummyOutput(BaseModel):
    value: str


class TimeoutModelClient:
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[BaseModel],
    ) -> Any:
        raise ModelTimeoutError("Model request timed out.")


class UnavailableModelClient:
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[BaseModel],
    ) -> Any:
        raise ModelUnavailableError("Model is unavailable.")


class InvalidOutputModelClient:
    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        output_schema: type[BaseModel],
    ) -> Any:
        raise ModelInvalidOutputError("Model returned invalid output.")


@pytest.mark.asyncio
async def test_model_timeout_is_preserved() -> None:
    client = TimeoutModelClient()

    with pytest.raises(ModelTimeoutError):
        await client.generate_structured(
            system_prompt="system",
            user_prompt="user",
            output_schema=DummyOutput,
        )


@pytest.mark.asyncio
async def test_model_unavailable_is_preserved() -> None:
    client = UnavailableModelClient()

    with pytest.raises(ModelUnavailableError):
        await client.generate_structured(
            system_prompt="system",
            user_prompt="user",
            output_schema=DummyOutput,
        )


@pytest.mark.asyncio
async def test_invalid_model_output_is_preserved() -> None:
    client = InvalidOutputModelClient()

    with pytest.raises(ModelInvalidOutputError):
        await client.generate_structured(
            system_prompt="system",
            user_prompt="user",
            output_schema=DummyOutput,
        )
