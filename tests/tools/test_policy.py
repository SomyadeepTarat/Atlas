import pytest

from atlas.tools.builtin.calculator import CalculatorTool
from atlas.tools.builtin.mock_write import MockWriteTool
from atlas.tools.errors import (
    ToolApprovalRequiredError,
    ToolPermissionDeniedError,
)
from atlas.tools.policy import ToolPolicyEngine
from atlas.tools.types import (
    ToolExecutionContext,
    ToolPermission,
)


def test_missing_permission_denied():
    engine = ToolPolicyEngine()

    tool = CalculatorTool()

    with pytest.raises(ToolPermissionDeniedError):
        engine.authorize(
            tool=tool,
            context=(ToolExecutionContext(permissions=frozenset())),
        )


def test_high_risk_tool_requires_approval():
    engine = ToolPolicyEngine()

    with pytest.raises(ToolApprovalRequiredError):
        engine.authorize(
            tool=MockWriteTool(),
            context=ToolExecutionContext(
                permissions=frozenset({ToolPermission.EXTERNAL_WRITE})
            ),
        )


def test_approved_tool_is_allowed():
    engine = ToolPolicyEngine()

    engine.authorize(
        tool=MockWriteTool(),
        context=ToolExecutionContext(
            permissions=frozenset({ToolPermission.EXTERNAL_WRITE}),
            approved_tools=frozenset({"mock_external_write"}),
        ),
    )
