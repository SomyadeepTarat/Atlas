from atlas.tools.base import Tool
from atlas.tools.errors import (
    ToolApprovalRequiredError,
    ToolPermissionDeniedError,
)
from atlas.tools.types import (
    ToolExecutionContext,
)


class ToolPolicyEngine:
    def authorize(
        self,
        *,
        tool: Tool,
        context: ToolExecutionContext,
    ) -> None:
        missing_permissions = tool.policy.required_permissions - context.permissions

        if missing_permissions:
            raise ToolPermissionDeniedError(
                "Missing permissions: "
                + ", ".join(
                    sorted(permission.value for permission in missing_permissions)
                )
            )

        if tool.policy.requires_approval and tool.name not in context.approved_tools:
            raise ToolApprovalRequiredError(f"Tool '{tool.name}' requires approval.")
