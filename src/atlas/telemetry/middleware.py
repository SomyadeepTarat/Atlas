from time import monotonic
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.types import (
    ASGIApp,
    Message,
    Receive,
    Scope,
    Send,
)

from atlas.telemetry.logging import (
    bind_log_context,
    get_logger,
    reset_log_context,
)

logger = get_logger(__name__)


class RequestContextMiddleware:
    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        self._app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self._app(
                scope,
                receive,
                send,
            )
            return

        headers = MutableHeaders(scope=scope)

        request_id = headers.get("X-Request-ID") or str(uuid4())

        tokens = bind_log_context(request_id=request_id)

        started_at = monotonic()

        status_code = 500

        async def send_wrapper(
            message: Message,
        ) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]

                response_headers = MutableHeaders(scope=message)

                response_headers["X-Request-ID"] = request_id

            await send(message)

        try:
            await self._app(
                scope,
                receive,
                send_wrapper,
            )

            logger.info(
                "http.request.completed",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status_code": (status_code),
                    "duration_seconds": (monotonic() - started_at),
                },
            )

        except Exception:
            logger.exception(
                "http.request.failed",
                extra={
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "duration_seconds": (monotonic() - started_at),
                },
            )

            raise

        finally:
            reset_log_context(tokens)
