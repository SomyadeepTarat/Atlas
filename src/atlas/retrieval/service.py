from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from atlas.retrieval.chunker import (
    TextChunker,
)
from atlas.retrieval.deduplication import (
    deduplicate_adjacent_chunks,
)
from atlas.retrieval.embeddings import (
    EmbeddingService,
)
from atlas.retrieval.loader import (
    PDFLoader,
)
from atlas.retrieval.reranker import (
    Reranker,
)
from atlas.retrieval.store import (
    QdrantVectorStore,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)
from atlas.telemetry.tracing import (
    tracer,
)


class RetrievalModeUsed(StrEnum):
    HYBRID_RERANK = "hybrid_rerank"
    HYBRID = "hybrid"
    DENSE = "dense"
    SPARSE = "sparse"


@dataclass(frozen=True)
class RetrievalResult:
    chunks: list[RetrievedChunk]

    mode: RetrievalModeUsed

    degraded: bool


class RetrievalService:
    def __init__(
        self,
        *,
        loader: PDFLoader,
        chunker: TextChunker,
        embeddings: EmbeddingService,
        vector_store: QdrantVectorStore,
        reranker: Reranker,
        candidate_k: int,
        rerank_top_k: int,
        context_top_k: int,
        max_context_chars: int,
    ) -> None:
        self._loader = loader
        self._chunker = chunker
        self._embeddings = embeddings
        self._vector_store = vector_store
        self._reranker = reranker

        self._candidate_k = candidate_k

        self._rerank_top_k = rerank_top_k

        self._context_top_k = context_top_k

        self._max_context_chars = max_context_chars

    def ingest_pdf(
        self,
        file_path: str | Path,
        filename: str,
    ) -> tuple[str, int]:
        with tracer.start_as_current_span("retrieval-ingestion") as span:
            path = Path(file_path)

            pages = self._loader.load(
                path,
                filename=filename,
            )

            if not pages:
                raise ValueError("PDF contains no readable pages.")

            document_id = pages[0].document_id

            span.set_attribute(
                "atlas.document.id",
                document_id,
            )

            chunks = self._chunker.chunk_pages(pages)

            if not chunks:
                return (
                    document_id,
                    0,
                )

            texts = [chunk.text for chunk in chunks]

            dense_vectors = self._embeddings.embed_documents_dense(texts)

            sparse_vectors = self._embeddings.embed_documents_sparse(texts)

            self._vector_store.upsert(
                chunks=chunks,
                dense_vectors=(dense_vectors),
                sparse_vectors=(sparse_vectors),
            )

            return (
                document_id,
                len(chunks),
            )

    def search_candidates(
        self,
        query: str,
        *,
        document_ids: (list[str] | None) = None,
    ) -> list[RetrievedChunk]:
        dense_query = self._embeddings.embed_query_dense(query)

        sparse_query = self._embeddings.embed_query_sparse(query)

        return self._vector_store.hybrid_search(
            dense_query=(dense_query),
            sparse_query=(sparse_query),
            limit=(self._candidate_k),
            document_ids=(document_ids),
        )

    def retrieve_context(
        self,
        query: str,
    ) -> RetrievalResult:
        try:
            candidates = self.search_candidates(query)
        except Exception:
            dense_query = self._embeddings.embed_query_dense(query)
            chunks = self._vector_store.dense_search(
                query_vector=dense_query,
                limit=self._candidate_k,
            )

            return RetrievalResult(
                chunks=chunks[: self._context_top_k],
                mode=RetrievalModeUsed.DENSE,
                degraded=True,
            )

        try:
            reranked = self._reranker.rerank(
                query=query,
                chunks=candidates,
                limit=self._rerank_top_k,
            )
        except Exception:
            return RetrievalResult(
                chunks=candidates[: self._context_top_k],
                mode=RetrievalModeUsed.HYBRID,
                degraded=True,
            )

        return RetrievalResult(
            chunks=reranked[: self._context_top_k],
            mode=RetrievalModeUsed.HYBRID_RERANK,
            degraded=False,
        )

    def retrieve_for_experiment(
        self,
        *,
        query: str,
        mode: str,
        candidate_k: int,
        final_k: int,
        use_reranker: bool,
        use_deduplication: bool,
    ) -> list[RetrievedChunk]:
        with tracer.start_as_current_span("retrieval-experiment"):
            if mode == "dense":
                dense_query = self._embeddings.embed_query_dense(query)

                chunks = self._vector_store.dense_search(
                    query_vector=(dense_query),
                    limit=(candidate_k),
                )

            elif mode == "sparse":
                sparse_query = self._embeddings.embed_query_sparse(query)

                chunks = self._vector_store.sparse_search(
                    query_vector=(sparse_query),
                    limit=(candidate_k),
                )

            elif mode == "hybrid":
                dense_query = self._embeddings.embed_query_dense(query)

                sparse_query = self._embeddings.embed_query_sparse(query)

                chunks = self._vector_store.hybrid_search(
                    dense_query=(dense_query),
                    sparse_query=(sparse_query),
                    limit=(candidate_k),
                )

            else:
                raise ValueError(f"Unsupported retrieval mode: {mode}")

            if use_reranker:
                chunks = self._reranker.rerank(
                    query=query,
                    chunks=chunks,
                    limit=(candidate_k),
                )

            if use_deduplication:
                chunks = deduplicate_adjacent_chunks(chunks)

            return chunks[:final_k]
