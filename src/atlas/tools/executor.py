import asyncio
from time import monotonic
from typing import Any

from pydantic import ValidationError

from atlas.tools.errors import (
    ToolExecutionError,
    ToolInputValidationError,
    ToolOutputValidationError,
    ToolTimeoutError,
)
from atlas.tools.policy import ToolPolicyEngine
from atlas.tools.registry import ToolRegistry
from atlas.tools.types import (
    ToolExecutionContext,
    ToolMetadata,
    ToolResult,
)


class ToolExecutor:
    def __init__(
        self,
        *,
        registry: ToolRegistry,
        policy_engine: ToolPolicyEngine,
    ) -> None:
        self._registry = registry
        self._policy = policy_engine

    def _validate_input(
        self,
        tool: Any,
        raw_input: dict[str, Any],
    ) -> Any:
        try:
            return tool.input_schema.model_validate(raw_input)
        except ValidationError as exc:
            raise ToolInputValidationError("Tool input failed validation.") from exc

    async def _execute_once(
        self,
        *,
        tool: Any,
        input_data: Any,
    ) -> Any:
        try:
            async with asyncio.timeout(tool.policy.timeout_seconds):
                return await tool.execute(input_data)

        except TimeoutError as exc:
            raise ToolTimeoutError(f"Tool '{tool.name}' timed out.") from exc

        except ToolTimeoutError:
            raise

        except Exception as exc:
            raise ToolExecutionError(f"Tool '{tool.name}' failed.") from exc

    def _validate_output(
        self,
        tool: Any,
        output_data: Any,
    ) -> Any:
        try:
            return tool.output_schema.model_validate(output_data)
        except ValidationError as exc:
            raise ToolOutputValidationError("Tool output failed validation.") from exc

    async def execute(
        self,
        *,
        tool_name: str,
        raw_input: dict[str, Any],
        context: ToolExecutionContext,
    ) -> ToolResult:
        tool = self._registry.get(tool_name)

        if tool is None:
            raise ToolExecutionError(f"Unknown tool: '{tool_name}'.")

        self._policy.authorize(
            tool=tool,
            context=context,
        )

        validated_input = self._validate_input(
            tool,
            raw_input,
        )

        started_at = monotonic()

        output = await self._execute_once(
            tool=tool,
            input_data=validated_input,
        )

        duration_seconds = monotonic() - started_at

        validated_output = self._validate_output(
            tool,
            output,
        )

        metadata = ToolMetadata(
            tool_name=tool.name,
            duration_seconds=duration_seconds,
            attempts=1,
        )

        return ToolResult(
            output=validated_output,
            metadata=metadata,
        )
