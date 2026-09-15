from pydantic import BaseModel


class APIError(BaseModel):
    code: str
    message: str
    request_id: str
    trace_id: str | None = None
    retryable: bool
