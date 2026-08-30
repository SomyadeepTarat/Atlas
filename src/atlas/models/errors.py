class ModelError(Exception):
    """Base exception for model-layer failures."""

    retryable: bool = False


class ModelUnavailableError(ModelError):
    """Raised when the model provider cannot be reached."""

    retryable = True


class ModelTimeoutError(ModelError):
    """Raised when generation exceeds its allowed timeout."""

    retryable = True


class ModelInvalidOutputError(ModelError):
    """Raised when output violates the expected schema."""

    retryable = True


class AllModelsFailedError(ModelError):
    """Raised when every configured model provider fails."""

    retryable = False
