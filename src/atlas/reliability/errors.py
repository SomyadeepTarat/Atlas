class ReliabilityError(Exception):
    """Base reliability-layer error."""


class CircuitOpenError(ReliabilityError):
    """Dependency calls are temporarily blocked."""


class WorkflowDeadlineExceededError(ReliabilityError):
    """Research workflow exceeded its total deadline."""


class ConcurrencyLimitExceededError(ReliabilityError):
    """Too many concurrent operations."""


class DependencyUnavailableError(ReliabilityError):
    """Required dependency unavailable."""
