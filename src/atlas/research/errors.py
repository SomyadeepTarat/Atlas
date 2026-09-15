class ResearchError(Exception):
    """Base research-layer error."""


class InvalidCitationError(ResearchError):
    """Model referenced evidence not supplied."""


class WorkflowDeadlineExceededError(RuntimeError):
    """Raised when the research graph exceeds its execution budget."""
