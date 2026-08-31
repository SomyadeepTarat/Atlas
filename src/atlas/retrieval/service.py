from pathlib import Path

from atlas.retrieval.chunker import (
    TextChunker,
)
from atlas.retrieval.embeddings import (
    EmbeddingService,
)
from atlas.retrieval.loader import PDFLoader
from atlas.retrieval.store import (
    QdrantVectorStore,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)


class RetrievalService:
    def __init__(
        self,
        *,
        loader: PDFLoader,
        chunker: TextChunker,
        embeddings: EmbeddingService,
        vector_store: QdrantVectorStore,
        top_k: int,
    ) -> None:
        self._loader = loader
        self._chunker = chunker
        self._embeddings = embeddings
        self._vector_store = vector_store
        self._top_k = top_k

    def ingest_pdf(
        self,
        path: Path,
        *,
        filename: str | None = None,
    ) -> tuple[str, int]:
        pages = self._loader.load(
        path,
        filename=filename,
    )

        if not pages:
            raise ValueError(
                "No extractable text "
                "was found in the PDF."
            )

        chunks = (
            self._chunker.chunk_pages(
                pages
            )
        )

        vectors = (
            self._embeddings.embed_documents(
                [
                    chunk.text
                    for chunk in chunks
                ]
            )
        )

        self._vector_store.ensure_collection()

        self._vector_store.upsert(
            chunks=chunks,
            vectors=vectors,
        )

        return (
            pages[0].document_id,
            len(chunks),
        )

    def search(
        self,
        query: str,
    ) -> list[RetrievedChunk]:
        vector = (
            self._embeddings.embed_query(
                query
            )
        )

        self._vector_store.ensure_collection()

        return self._vector_store.search(
            query_vector=vector,
            limit=self._top_k,
        )
    