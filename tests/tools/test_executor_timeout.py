import asyncio

import pytest
from pydantic import BaseModel

from atlas.tools.base import Tool
from atlas.tools.errors import ToolTimeoutError
from atlas.tools.executor import ToolExecutor
from atlas.tools.policy import ToolPolicyEngine
from atlas.tools.registry import ToolRegistry
from atlas.tools.types import (
    ToolExecutionContext,
    ToolPolicy,
    ToolRisk,
)


class EmptyInput(BaseModel):
    pass


class EmptyOutput(BaseModel):
    success: bool


class SlowTool(
    Tool[
        EmptyInput,
        EmptyOutput,
    ]
):
    name = "slow_tool"
    description = "Tool used to test execution timeout."

    input_schema = EmptyInput
    output_schema = EmptyOutput

    policy = ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        required_permissions=frozenset(),
        requires_approval=False,
        timeout_seconds=0.01,
        max_attempts=1,
        idempotent=True,
    )

    async def execute(
        self,
        input_data: EmptyInput,
    ) -> EmptyOutput:
        await asyncio.sleep(0.1)

        return EmptyOutput(success=True)


@pytest.mark.asyncio
async def test_tool_execution_timeout() -> None:
    registry = ToolRegistry(tools=[SlowTool()])

    executor = ToolExecutor(
        registry=registry,
        policy_engine=ToolPolicyEngine(),
    )

    context = ToolExecutionContext(
        permissions=frozenset(),
    )

    with pytest.raises(ToolTimeoutError):
        await executor.execute(
            tool_name="slow_tool",
            raw_input={},
            context=context,
        )
