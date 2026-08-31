from functools import lru_cache

from atlas.core.config import get_settings
from atlas.retrieval.chunker import TextChunker
from atlas.retrieval.embeddings import EmbeddingService
from atlas.retrieval.loader import PDFLoader
from atlas.retrieval.reranker import Reranker
from atlas.retrieval.service import RetrievalService
from atlas.retrieval.store import QdrantVectorStore


@lru_cache
def get_embedding_service() -> EmbeddingService:
    settings = get_settings()

    return EmbeddingService(
        dense_model_name=settings.embedding_model,
        sparse_model_name=settings.sparse_embedding_model,
    )


@lru_cache
def get_reranker() -> Reranker:
    settings = get_settings()

    return Reranker(
        model_name=settings.reranker_model,
    )


@lru_cache
def get_retrieval_service() -> RetrievalService:
    settings = get_settings()

    embeddings = get_embedding_service()
    reranker = get_reranker()

    store = QdrantVectorStore(
        url=settings.qdrant_url,
        collection_name=settings.qdrant_collection,
        vector_size=embeddings.dimension,
    )

    store.ensure_collection()

    return RetrievalService(
        loader=PDFLoader(),
        chunker=TextChunker(
            chunk_size=settings.chunk_size_chars,
            overlap=settings.chunk_overlap_chars,
        ),
        embeddings=embeddings,
        vector_store=store,
        reranker=reranker,
        candidate_k=settings.retrieval_candidate_k,
        rerank_top_k=settings.rerank_top_k,
        context_top_k=settings.context_top_k,
        max_context_chars=settings.max_context_chars,
    )
