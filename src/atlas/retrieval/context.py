from atlas.retrieval.types import (
    RetrievedChunk,
)


def build_context(
    chunks: list[RetrievedChunk],
) -> str:
    blocks: list[str] = []

    for chunk in chunks:
        blocks.append(
            "\n".join(
                [
                    (
                        f"[CHUNK_ID: "
                        f"{chunk.chunk_id}]"
                    ),
                    (
                        f"[SOURCE: "
                        f"{chunk.filename}, "
                        f"page "
                        f"{chunk.page_number}]"
                    ),
                    chunk.text,
                ]
            )
        )

    return "\n\n---\n\n".join(blocks)