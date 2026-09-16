from pathlib import Path
from typing import cast

import pymupdf

from atlas.retrieval.identity import (
    create_document_id,
)
from atlas.retrieval.types import DocumentPage


class PDFLoader:
    def __init__(
        self,
        *,
        max_pages: int,
        max_extracted_chars: int,
    ) -> None:
        self._max_pages = max_pages
        self._max_extracted_chars = max_extracted_chars

    def load(
        self,
        path: Path,
        *,
        filename: str | None = None,
    ) -> list[DocumentPage]:
        document_id = create_document_id(path)

        display_filename = filename or path.name

        pages: list[DocumentPage] = []
        extracted_chars = 0

        with pymupdf.open(path) as document:
            if len(document) > self._max_pages:
                raise ValueError("PDF exceeds maximum page limit.")

            for index in range(len(document)):
                page = document[index]
                text = self._normalize_text(cast(str, page.get_text("text")))

                extracted_chars += len(text)
                if extracted_chars > self._max_extracted_chars:
                    raise ValueError("Extracted document text exceeds allowed limit.")

                if not text:
                    continue

                pages.append(
                    DocumentPage(
                        document_id=document_id,
                        filename=display_filename,
                        page_number=index + 1,
                        text=text,
                    )
                )

        return pages

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:
        lines = [line.strip() for line in text.splitlines()]

        non_empty = [line for line in lines if line]

        return "\n".join(non_empty)
