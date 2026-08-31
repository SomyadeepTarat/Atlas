from typing import cast

from qdrant_client import QdrantClient, models
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from atlas.retrieval.types import (
    DocumentChunk,
    RetrievedChunk,
)


class QdrantVectorStore:
    def __init__(
        self,
        *,
        collection_name: str,
        vector_size: int,
        url: str | None = None,
        client: QdrantClient | None = None,
    ) -> None:
        if client is None:
            if url is None:
                raise ValueError("Either client or URL must be provided.")

            client = QdrantClient(url=url)

        self._client = client
        self._collection_name = collection_name
        self._vector_size = vector_size

    def ensure_collection(self) -> None:
        if self._client.collection_exists(self._collection_name):
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=self._vector_size,
                    distance=Distance.COSINE,
                ),
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(),
            },
        )

    def upsert(
        self,
        *,
        chunks: list[DocumentChunk],
        dense_vectors: list[list[float]],
        sparse_vectors: list[SparseVector],
    ) -> None:
        if len(chunks) != len(dense_vectors):
            raise ValueError("Chunks and dense vectors must have the same length.")

        if len(chunks) != len(sparse_vectors):
            raise ValueError("Chunks and sparse vectors must have the same length.")

        points = [
            PointStruct(
                id=chunk.chunk_id,
                vector={
                    "dense": dense_vector,
                    "sparse": sparse_vector,
                },
                payload={
                    "document_id": chunk.document_id,
                    "filename": chunk.filename,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "text": chunk.text,
                },
            )
            for chunk, dense_vector, sparse_vector in zip(
                chunks,
                dense_vectors,
                sparse_vectors,
                strict=True,
            )
        ]

        self._client.upsert(
            collection_name=self._collection_name,
            points=points,
        )

    def hybrid_search(
        self,
        *,
        dense_query: list[float],
        sparse_query: SparseVector,
        limit: int,
        document_ids: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        query_filter: Filter | None = None

        if document_ids:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchAny(
                            any=document_ids,
                        ),
                    )
                ]
            )

        response = self._client.query_points(
            collection_name=self._collection_name,
            prefetch=[
                models.Prefetch(
                    query=dense_query,
                    using="dense",
                    limit=limit,
                    filter=query_filter,
                ),
                models.Prefetch(
                    query=sparse_query,
                    using="sparse",
                    limit=limit,
                    filter=query_filter,
                ),
            ],
            query=models.FusionQuery(
                fusion=models.Fusion.RRF,
            ),
            limit=limit,
            with_payload=True,
        )

        retrieved: list[RetrievedChunk] = []

        for result in response.points:
            payload = result.payload or {}

            retrieved.append(
                RetrievedChunk(
                    chunk_id=str(result.id),
                    document_id=cast(
                        str,
                        payload["document_id"],
                    ),
                    filename=cast(
                        str,
                        payload["filename"],
                    ),
                    page_number=cast(
                        int,
                        payload["page_number"],
                    ),
                    chunk_index=cast(
                        int,
                        payload["chunk_index"],
                    ),
                    text=cast(
                        str,
                        payload["text"],
                    ),
                    retrieval_score=float(result.score),
                    rerank_score=None,
                )
            )

        return retrieved
