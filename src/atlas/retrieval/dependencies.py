from functools import lru_cache

from atlas.core.config import get_settings
from atlas.retrieval.chunker import (
    TextChunker,
)
from atlas.retrieval.embeddings import (
    EmbeddingService,
)
from atlas.retrieval.loader import PDFLoader
from atlas.retrieval.service import (
    RetrievalService,
)
from atlas.retrieval.store import (
    QdrantVectorStore,
)


@lru_cache
def get_embedding_service(
) -> EmbeddingService:
    settings = get_settings()

    return EmbeddingService(
        model_name=settings.embedding_model
    )


@lru_cache
def get_retrieval_service(
) -> RetrievalService:
    settings = get_settings()

    embeddings = get_embedding_service()

    store = QdrantVectorStore(
        url=settings.qdrant_url,
        collection_name=(
            settings.qdrant_collection
        ),
        vector_size=embeddings.dimension,
    )

    return RetrievalService(
        loader=PDFLoader(),
        chunker=TextChunker(
            chunk_size=(
                settings.chunk_size_chars
            ),
            overlap=(
                settings.chunk_overlap_chars
            ),
        ),
        embeddings=embeddings,
        vector_store=store,
        top_k=settings.retrieval_top_k,
    )