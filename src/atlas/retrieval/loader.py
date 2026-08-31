from pathlib import Path
from uuid import uuid4

import pymupdf

from atlas.retrieval.types import DocumentPage


class PDFLoader:
    def load(
        self,
        path: Path,
        *,
        filename: str | None = None,
    ) -> list[DocumentPage]:
        document_id = str(uuid4())

        display_filename = filename or path.name

        pages: list[DocumentPage] = []

        with pymupdf.open(path) as document:
            for index in range(len(document)):
                page = document[index]
                text = page.get_text("text")

                text = self._normalize_text(text if isinstance(text, str) else "")

                if not text:
                    continue

                pages.append(
                    DocumentPage(
                        document_id=document_id,
                        filename=(display_filename),
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
