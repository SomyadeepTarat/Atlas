from atlas.retrieval.types import (
    RetrievedChunk,
)


def deduplicate_adjacent_chunks(
    chunks: list[RetrievedChunk],
) -> list[RetrievedChunk]:
    kept: list[RetrievedChunk] = []

    seen: set[tuple[str, int]] = set()

    for chunk in chunks:
        key = (
            chunk.document_id,
            chunk.chunk_index,
        )

        adjacent = {
            (
                chunk.document_id,
                chunk.chunk_index - 1,
            ),
            (
                chunk.document_id,
                chunk.chunk_index + 1,
            ),
        }

        if any(neighbor in seen for neighbor in adjacent):
            continue

        kept.append(chunk)
        seen.add(key)

    return kept
