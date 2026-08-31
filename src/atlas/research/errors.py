class ResearchError(Exception):
    """Base research-layer error."""


class InvalidCitationError(ResearchError):
    """Model referenced evidence not supplied."""
