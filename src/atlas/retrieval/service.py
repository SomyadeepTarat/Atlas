from pathlib import Path

from atlas.retrieval.chunker import TextChunker
from atlas.retrieval.context import select_context_chunks
from atlas.retrieval.deduplication import deduplicate_adjacent_chunks
from atlas.retrieval.embeddings import EmbeddingService
from atlas.retrieval.loader import PDFLoader
from atlas.retrieval.reranker import Reranker
from atlas.retrieval.store import QdrantVectorStore
from atlas.retrieval.types import RetrievedChunk


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
        path: Path,
        *,
        filename: str,
    ) -> tuple[str, int]:
        pages = self._loader.load(
            path,
            filename=filename,
        )

        if not pages:
            raise ValueError("No extractable text was found in the PDF.")

        chunks = self._chunker.chunk_pages(pages)

        if not chunks:
            raise ValueError("No chunks could be created from the PDF.")

        texts = [chunk.text for chunk in chunks]

        dense_vectors = self._embeddings.embed_documents_dense(texts)

        sparse_vectors = self._embeddings.embed_documents_sparse(texts)

        self._vector_store.upsert(
            chunks=chunks,
            dense_vectors=dense_vectors,
            sparse_vectors=sparse_vectors,
        )

        return (
            pages[0].document_id,
            len(chunks),
        )

    def search_candidates(
        self,
        query: str,
        *,
        document_ids: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        dense_query = self._embeddings.embed_query_dense(query)

        sparse_query = self._embeddings.embed_query_sparse(query)

        return self._vector_store.hybrid_search(
            dense_query=dense_query,
            sparse_query=sparse_query,
            limit=self._candidate_k,
            document_ids=document_ids,
        )

    def retrieve_context(
        self,
        query: str,
    ) -> list[RetrievedChunk]:
        candidates = self.search_candidates(query)

        reranked = self._reranker.rerank(
            query=query,
            chunks=candidates,
            limit=self._rerank_top_k,
        )

        deduplicated = deduplicate_adjacent_chunks(reranked)

        return select_context_chunks(
            deduplicated,
            max_chunks=self._context_top_k,
            max_chars=self._max_context_chars,
        )
