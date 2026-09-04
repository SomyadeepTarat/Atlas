from hashlib import sha256
from pathlib import Path


def create_document_id(
    path: Path,
) -> str:
    digest = sha256()

    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


def create_chunk_id(
    *,
    document_id: str,
    page_number: int,
    chunk_index: int,
    text: str,
) -> str:
    raw = f"{document_id}:{page_number}:{chunk_index}:{text}"

    return sha256(raw.encode("utf-8")).hexdigest()
