from fastembed import SparseTextEmbedding, TextEmbedding
from qdrant_client.models import SparseVector


class EmbeddingService:
    def __init__(
        self,
        *,
        dense_model_name: str,
        sparse_model_name: str,
    ) -> None:
        self._dense_model = TextEmbedding(model_name=dense_model_name)

        self._sparse_model = SparseTextEmbedding(model_name=sparse_model_name)

    @property
    def dimension(self) -> int:
        test_vector = next(iter(self._dense_model.embed(["dimension check"])))

        return len(test_vector)

    def embed_documents_dense(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        embeddings = self._dense_model.embed(texts)

        return [embedding.tolist() for embedding in embeddings]

    def embed_query_dense(
        self,
        query: str,
    ) -> list[float]:
        embedding = next(iter(self._dense_model.query_embed(query)))

        return embedding.tolist()

    def embed_documents_sparse(
        self,
        texts: list[str],
    ) -> list[SparseVector]:
        embeddings = self._sparse_model.embed(texts)

        return [
            SparseVector(
                indices=embedding.indices.tolist(),
                values=embedding.values.tolist(),
            )
            for embedding in embeddings
        ]

    def embed_query_sparse(
        self,
        query: str,
    ) -> SparseVector:
        embedding = next(iter(self._sparse_model.query_embed(query)))

        return SparseVector(
            indices=embedding.indices.tolist(),
            values=embedding.values.tolist(),
        )
