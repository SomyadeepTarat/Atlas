from pathlib import Path

from atlas.security.errors import (
    InvalidFileError,
    ResourceLimitError,
)

PDF_MAGIC = b"%PDF-"


def validate_pdf_upload(
    *,
    filename: str,
    content: bytes,
    max_bytes: int,
    max_filename_chars: int,
) -> None:
    if not filename:
        raise InvalidFileError("Filename is required.")

    if len(filename) > max_filename_chars:
        raise InvalidFileError("Filename is too long.")

    if not filename.lower().endswith(".pdf"):
        raise InvalidFileError("Only PDF files are supported.")

    if len(content) > max_bytes:
        raise ResourceLimitError("Uploaded PDF exceeds size limit.")

    if not content.startswith(PDF_MAGIC):
        raise InvalidFileError("Uploaded file is not a valid PDF.")


def safe_display_filename(
    filename: str,
) -> str:
    name = Path(filename).name

    if not name:
        return "document.pdf"

    return name
