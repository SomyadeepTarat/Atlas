import re
from hashlib import sha256


def hash_text(
    value: str,
) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def text_metadata(
    value: str,
) -> dict[str, str | int]:
    return {
        "text.length": len(value),
        "text.sha256": hash_text(value),
    }


_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(authorization)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(password)\s*[:=]\s*\S+"),
]


def redact_secrets(
    value: str,
) -> str:
    sanitized = value

    for pattern in _SECRET_PATTERNS:
        sanitized = pattern.sub(
            r"\1=[REDACTED]",
            sanitized,
        )

    return sanitized
