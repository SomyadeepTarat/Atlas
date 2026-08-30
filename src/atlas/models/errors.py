class ModelError(Exception):
    """Base exception for model-layer failures."""


class ModelUnavailableError(ModelError):
    """Raised when the model service cannot be reached."""


class ModelTimeoutError(ModelError):
    """Raised when model inference exceeds the configured timeout."""


class ModelInvalidOutputError(ModelError):
    """Raised when model output violates the expected schema."""