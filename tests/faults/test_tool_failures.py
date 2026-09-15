import asyncio

import pytest
from pydantic import BaseModel

from atlas.tools.errors import (
    ToolExecutionUnknownError,
    ToolTimeoutError,
)
from atlas.tools.executor import ToolExecutor
from atlas.tools.types import (
    ToolExecutionContext,
    ToolRisk,
)


class SlowInput(BaseModel):
    value: str


class SlowOutput(BaseModel):
    value: str


class DummyPolicy:
    def __init__(
        self,
        *,
        risk: ToolRisk,
    ) -> None:
        self.risk = risk
        self.timeout_seconds = 0.01


class SlowTool:
    name = "slow_tool"
    input_schema = SlowInput
    output_schema = SlowOutput

    def __init__(
        self,
        *,
        risk: ToolRisk,
    ) -> None:
        self.policy = DummyPolicy(risk=risk)

    async def execute(
        self,
        input_data: SlowInput,
    ) -> SlowOutput:
        await asyncio.sleep(0.1)

        return SlowOutput(value=input_data.value)


class FakeRegistry:
    def __init__(
        self,
        tool: SlowTool,
    ) -> None:
        self._tool = tool

    def get(
        self,
        tool_name: str,
    ) -> SlowTool | None:
        if tool_name == self._tool.name:
            return self._tool

        return None


class AllowAllPolicyEngine:
    def authorize(
        self,
        *,
        tool: SlowTool,
        context: ToolExecutionContext,
    ) -> None:
        del tool
        del context


def make_context() -> ToolExecutionContext:
    return ToolExecutionContext(
        permissions=frozenset(),
    )


@pytest.mark.asyncio
async def test_read_only_timeout_is_timeout_failure() -> None:
    tool = SlowTool(risk=ToolRisk.READ_ONLY)

    executor = ToolExecutor(
        registry=FakeRegistry(tool),  # type: ignore[arg-type]
        policy_engine=AllowAllPolicyEngine(),  # type: ignore[arg-type]
    )

    with pytest.raises(ToolTimeoutError):
        await executor.execute(
            tool_name="slow_tool",
            raw_input={"value": "test"},
            context=make_context(),
        )


@pytest.mark.asyncio
async def test_side_effect_timeout_becomes_unknown() -> None:
    tool = SlowTool(risk=ToolRisk.LOW_RISK_WRITE)

    executor = ToolExecutor(
        registry=FakeRegistry(tool),  # type: ignore[arg-type]
        policy_engine=AllowAllPolicyEngine(),  # type: ignore[arg-type]
    )

    with pytest.raises(ToolExecutionUnknownError):
        await executor.execute(
            tool_name="slow_tool",
            raw_input={"value": "test"},
            context=make_context(),
        )
