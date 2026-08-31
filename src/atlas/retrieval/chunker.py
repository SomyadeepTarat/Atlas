from uuid import uuid4

from atlas.retrieval.types import (
    DocumentChunk,
    DocumentPage,
)


class TextChunker:
    def __init__(
        self,
        *,
        chunk_size: int,
        overlap: int,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive.")

        if overlap < 0:
            raise ValueError("overlap cannot be negative.")

        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size.")

        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk_pages(
        self,
        pages: list[DocumentPage],
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        chunk_index = 0

        for page in pages:
            page_chunks = self._chunk_text(page.text)

            for text in page_chunks:
                chunks.append(
                    DocumentChunk(
                        chunk_id=str(uuid4()),
                        document_id=(page.document_id),
                        filename=page.filename,
                        page_number=(page.page_number),
                        chunk_index=chunk_index,
                        text=text,
                    )
                )

                chunk_index += 1

        return chunks

    def _chunk_text(
        self,
        text: str,
    ) -> list[str]:
        chunks: list[str] = []

        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(
                start + self._chunk_size,
                text_length,
            )

            candidate = text[start:end]

            if end < text_length:
                candidate = self._move_to_boundary(candidate)

            candidate = candidate.strip()

            if candidate:
                chunks.append(candidate)

            consumed = len(candidate)

            if consumed == 0:
                break

            next_start = start + consumed - self._overlap

            if next_start <= start:
                next_start = end

            start = next_start

        return chunks

    @staticmethod
    def _move_to_boundary(
        text: str,
    ) -> str:
        boundaries = [
            text.rfind("\n\n"),
            text.rfind(". "),
            text.rfind("\n"),
            text.rfind(" "),
        ]

        best = max(boundaries)

        minimum_boundary = int(len(text) * 0.6)

        if best >= minimum_boundary:
            return text[: best + 1]

        return text
