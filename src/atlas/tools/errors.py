class ToolError(Exception):
    """Base exception for all tool-related failures."""


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not registered."""


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""


class ToolAuthorizationError(ToolError):
    """Raised when a tool call is blocked by policy."""


class ToolPermissionDeniedError(ToolAuthorizationError):
    """Raised when required permissions are missing."""


class ToolApprovalRequiredError(ToolAuthorizationError):
    """Raised when explicit approval is required."""


class ToolInputValidationError(ToolExecutionError):
    """Raised when tool input validation fails."""


class ToolOutputValidationError(ToolExecutionError):
    """Raised when tool output validation fails."""


class ToolTimeoutError(ToolExecutionError):
    """Raised when tool execution times out."""


class ToolExecutionUnknownError(ToolExecutionError):
    """Raised when execution may have succeeded but cannot be confirmed."""

    retryable = False
