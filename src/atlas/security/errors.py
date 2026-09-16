class SecurityError(Exception):
    """Base security-layer exception."""


class UnsafeContentError(SecurityError):
    """Input violated a security policy."""


class ResourceLimitError(SecurityError):
    """Input exceeded an allowed resource limit."""


class InvalidFileError(SecurityError):
    """Uploaded file failed security validation."""


class SecurityPolicyViolationError(SecurityError):
    """Requested operation violates security policy."""
