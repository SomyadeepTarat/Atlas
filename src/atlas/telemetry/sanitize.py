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
