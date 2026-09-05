class ToolError(Exception):
    """Base tool-layer error."""

    retryable: bool = False


class ToolNotFoundError(ToolError):
    """Unknown tool requested."""


class ToolInputValidationError(ToolError):
    """Tool input violated schema."""


class ToolOutputValidationError(ToolError):
    """Tool returned invalid output."""


class ToolPermissionDeniedError(ToolError):
    """Caller lacks permission."""


class ToolApprovalRequiredError(ToolError):
    """Execution requires approval."""


class ToolTimeoutError(ToolError):
    """Tool exceeded timeout."""

    retryable = True


class ToolExecutionError(ToolError):
    """Tool implementation failed."""

    retryable = True
