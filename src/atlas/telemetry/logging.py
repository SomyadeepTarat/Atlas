import json
import logging
import sys
from contextvars import (
    ContextVar,
    Token,
)
from dataclasses import dataclass
from datetime import (
    UTC,
    datetime,
)
from typing import Any

_request_id: ContextVar[str | None] = ContextVar(
    "atlas_request_id",
    default=None,
)

_thread_id: ContextVar[str | None] = ContextVar(
    "atlas_thread_id",
    default=None,
)


@dataclass(frozen=True)
class LogContextTokens:
    request_id: Token[str | None] | None
    thread_id: Token[str | None] | None


_STANDARD_RECORD_FIELDS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "taskName",
}


class JSONFormatter(logging.Formatter):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        payload: dict[
            str,
            Any,
        ] = {
            "timestamp": (datetime.now(UTC).isoformat()),
            "level": (record.levelname),
            "logger": (record.name),
            "message": (record.getMessage()),
        }

        request_id = _request_id.get()
        thread_id = _thread_id.get()

        if request_id is not None:
            payload["request_id"] = request_id

        if thread_id is not None:
            payload["thread_id"] = thread_id

        for key, value in record.__dict__.items():
            if key not in _STANDARD_RECORD_FIELDS and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            default=str,
        )


def configure_logging(
    *,
    level: str = "INFO",
) -> None:
    root_logger = logging.getLogger()

    root_logger.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(JSONFormatter())

    root_logger.handlers.clear()

    root_logger.addHandler(handler)


def get_logger(
    name: str,
) -> logging.Logger:
    return logging.getLogger(name)


def bind_log_context(
    *,
    request_id: str | None = None,
    thread_id: str | None = None,
) -> LogContextTokens:
    request_token = None
    thread_token = None

    if request_id is not None:
        request_token = _request_id.set(request_id)

    if thread_id is not None:
        thread_token = _thread_id.set(thread_id)

    return LogContextTokens(
        request_id=request_token,
        thread_id=thread_token,
    )


def reset_log_context(
    tokens: LogContextTokens,
) -> None:
    if tokens.request_id is not None:
        _request_id.reset(tokens.request_id)

    if tokens.thread_id is not None:
        _thread_id.reset(tokens.thread_id)
