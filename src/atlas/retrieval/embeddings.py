from fastembed import (
    SparseTextEmbedding,
    TextEmbedding,
)
from qdrant_client.models import (
    SparseVector,
)

from atlas.telemetry.tracing import (
    tracer,
)


class EmbeddingService:
    def __init__(
        self,
        *,
        dense_model_name: str,
        sparse_model_name: str,
    ) -> None:
        self._dense_model_name = dense_model_name

        self._sparse_model_name = sparse_model_name

        self._dense_model = TextEmbedding(model_name=(dense_model_name))

        self._sparse_model = SparseTextEmbedding(model_name=(sparse_model_name))

    @property
    def dimension(
        self,
    ) -> int:
        vector = next(iter(self._dense_model.embed([("dimension check")])))

        return len(vector)

    def embed_documents_dense(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        with tracer.start_as_current_span("dense-embedding") as span:
            span.set_attribute(
                ("atlas.embedding.model"),
                self._dense_model_name,
            )

            span.set_attribute(
                ("atlas.embedding.document_count"),
                len(texts),
            )

            embeddings = self._dense_model.embed(texts)

            return [embedding.tolist() for embedding in embeddings]

    def embed_query_dense(
        self,
        query: str,
    ) -> list[float]:
        with tracer.start_as_current_span("dense-embedding") as span:
            span.set_attribute(
                ("atlas.embedding.model"),
                self._dense_model_name,
            )

            span.set_attribute(
                ("atlas.embedding.query_chars"),
                len(query),
            )

            embedding = next(iter(self._dense_model.query_embed(query)))

            return embedding.tolist()

    def embed_documents_sparse(
        self,
        texts: list[str],
    ) -> list[SparseVector]:
        with tracer.start_as_current_span("sparse-embedding") as span:
            span.set_attribute(
                ("atlas.embedding.model"),
                self._sparse_model_name,
            )

            span.set_attribute(
                ("atlas.embedding.document_count"),
                len(texts),
            )

            embeddings = self._sparse_model.embed(texts)

            return [
                SparseVector(
                    indices=(embedding.indices.tolist()),
                    values=(embedding.values.tolist()),
                )
                for embedding in embeddings
            ]

    def embed_query_sparse(
        self,
        query: str,
    ) -> SparseVector:
        with tracer.start_as_current_span("sparse-embedding") as span:
            span.set_attribute(
                ("atlas.embedding.model"),
                self._sparse_model_name,
            )

            span.set_attribute(
                ("atlas.embedding.query_chars"),
                len(query),
            )

            embedding = next(iter(self._sparse_model.query_embed(query)))

            return SparseVector(
                indices=(embedding.indices.tolist()),
                values=(embedding.values.tolist()),
            )
