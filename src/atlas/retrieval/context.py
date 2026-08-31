from atlas.retrieval.types import (
    RetrievedChunk,
)


def select_context_chunks(
    chunks: list[RetrievedChunk],
    *,
    max_chunks: int,
    max_chars: int,
) -> list[RetrievedChunk]:
    selected: list[RetrievedChunk] = []

    used_chars = 0

    for chunk in chunks:
        if len(selected) >= max_chunks:
            break

        chunk_cost = len(chunk.text)

        if used_chars + chunk_cost > max_chars:
            continue

        selected.append(chunk)
        used_chars += chunk_cost

    return selected


def build_context(
    chunks: list[RetrievedChunk],
) -> str:
    blocks: list[str] = []

    for chunk in chunks:
        blocks.append(
            "\n".join(
                [
                    (f"[CHUNK_ID: {chunk.chunk_id}]"),
                    (f"[SOURCE: {chunk.filename}, page {chunk.page_number}]"),
                    chunk.text,
                ]
            )
        )

    return "\n\n---\n\n".join(blocks)
