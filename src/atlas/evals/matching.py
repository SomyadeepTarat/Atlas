from atlas.evals.types import (
    EvidenceLabel,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)


def chunk_matches_label(
    chunk: RetrievedChunk,
    label: EvidenceLabel,
) -> bool:
    if chunk.document_id != label.document_id:
        return False

    if label.chunk_id is not None and chunk.chunk_id != label.chunk_id:
        return False

    if label.page_number is not None and chunk.page_number != label.page_number:
        return False

    if label.text_contains is not None:
        expected = label.text_contains.casefold()
        actual = chunk.text.casefold()

        if expected not in actual:
            return False

    return True


def relevance_flags(
    *,
    chunks: list[RetrievedChunk],
    labels: list[EvidenceLabel],
) -> list[int]:
    return [
        int(
            any(
                chunk_matches_label(
                    chunk,
                    label,
                )
                for label in labels
            )
        )
        for chunk in chunks
    ]


def relevance_flags_unique(
    *,
    chunks: list[RetrievedChunk],
    labels: list[EvidenceLabel],
) -> list[int]:
    matched_labels: set[int] = set()
    flags: list[int] = []

    for chunk in chunks:
        matched_index: int | None = None

        for index, label in enumerate(labels):
            if index in matched_labels:
                continue

            if chunk_matches_label(
                chunk,
                label,
            ):
                matched_index = index
                break

        if matched_index is None:
            flags.append(0)
        else:
            flags.append(1)
            matched_labels.add(matched_index)

    return flags
