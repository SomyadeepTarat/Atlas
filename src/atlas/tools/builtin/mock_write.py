from pydantic import BaseModel

from atlas.tools.base import Tool
from atlas.tools.types import (
    ToolPermission,
    ToolPolicy,
    ToolRisk,
)


class MockWriteInput(BaseModel):
    message: str


class MockWriteOutput(BaseModel):
    stored: bool


class MockWriteTool(
    Tool[
        MockWriteInput,
        MockWriteOutput,
    ]
):
    name = "mock_external_write"

    description = "Development-only tool used to test high-risk approval enforcement."

    input_schema = MockWriteInput
    output_schema = MockWriteOutput

    policy = ToolPolicy(
        risk=ToolRisk.HIGH_RISK_WRITE,
        required_permissions=frozenset(
            {
                ToolPermission.EXTERNAL_WRITE,
            }
        ),
        requires_approval=True,
        timeout_seconds=2.0,
        max_attempts=1,
    )

    async def execute(
        self,
        input_data: MockWriteInput,
    ) -> MockWriteOutput:
        return MockWriteOutput(stored=True)
