from time import monotonic
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from atlas.telemetry.logging import (
    bind_log_context,
    get_logger,
    reset_log_context,
)

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())

        tokens = bind_log_context(request_id=request_id)

        started_at = monotonic()

        try:
            response = await call_next(request)

            response.headers["X-Request-ID"] = request_id

            logger.info(
                "http.request.completed",
                extra={
                    "method": (request.method),
                    "path": (request.url.path),
                    "status_code": (response.status_code),
                    "duration_seconds": (monotonic() - started_at),
                },
            )

            return response

        except Exception:
            logger.exception(
                "http.request.failed",
                extra={
                    "method": (request.method),
                    "path": (request.url.path),
                    "duration_seconds": (monotonic() - started_at),
                },
            )

            raise

        finally:
            reset_log_context(tokens)
