import pytest

from atlas.tools.builtin.mock_write import (
    MockWriteTool,
)
from atlas.tools.errors import (
    ToolApprovalRequiredError,
    ToolPermissionDeniedError,
)
from atlas.tools.policy import (
    ToolPolicyEngine,
)
from atlas.tools.types import (
    ToolExecutionContext,
    ToolPermission,
)


def test_model_cannot_self_grant_write_permission():
    engine = ToolPolicyEngine()

    context = ToolExecutionContext(permissions=frozenset())

    with pytest.raises(ToolPermissionDeniedError):
        engine.authorize(
            tool=MockWriteTool(),
            context=context,
        )


def test_high_risk_write_cannot_bypass_approval():
    engine = ToolPolicyEngine()

    context = ToolExecutionContext(
        permissions=frozenset({ToolPermission.EXTERNAL_WRITE}),
        approved_tools=frozenset(),
    )

    with pytest.raises(ToolApprovalRequiredError):
        engine.authorize(
            tool=MockWriteTool(),
            context=context,
        )
