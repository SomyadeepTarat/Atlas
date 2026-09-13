from typing import Any, cast
from uuid import NAMESPACE_URL, uuid5

from opentelemetry import trace
from qdrant_client import (
    QdrantClient,
    models,
)
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

tracer = trace.get_tracer(__name__)


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

    def ensure_collection(
        self,
    ) -> None:
        with tracer.start_as_current_span("qdrant.ensure_collection") as span:
            span.set_attribute(
                "atlas.qdrant.collection",
                self._collection_name,
            )

            exists = self._client.collection_exists(self._collection_name)

            span.set_attribute(
                ("atlas.qdrant.collection_exists"),
                exists,
            )

            if exists:
                return

            self._client.create_collection(
                collection_name=(self._collection_name),
                vectors_config={
                    "dense": VectorParams(
                        size=(self._vector_size),
                        distance=(Distance.COSINE),
                    ),
                },
                sparse_vectors_config={
                    "sparse": (SparseVectorParams()),
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

        with tracer.start_as_current_span("qdrant.upsert") as span:
            span.set_attribute(
                "atlas.qdrant.collection",
                self._collection_name,
            )

            span.set_attribute(
                "atlas.qdrant.point_count",
                len(chunks),
            )

            points = [
                PointStruct(
                    id=str(
                        uuid5(
                            NAMESPACE_URL,
                            chunk.chunk_id,
                        )
                    ),
                    vector={
                        "dense": (dense_vector),
                        "sparse": (sparse_vector),
                    },
                    payload={
                        "chunk_id": (chunk.chunk_id),
                        "document_id": (chunk.document_id),
                        "filename": (chunk.filename),
                        "page_number": (chunk.page_number),
                        "chunk_index": (chunk.chunk_index),
                        "text": (chunk.text),
                    },
                )
                for (
                    chunk,
                    dense_vector,
                    sparse_vector,
                ) in zip(
                    chunks,
                    dense_vectors,
                    sparse_vectors,
                    strict=True,
                )
            ]

            try:
                self._client.upsert(
                    collection_name=(self._collection_name),
                    points=points,
                )

                span.set_attribute(
                    ("atlas.qdrant.success"),
                    True,
                )

            except Exception as exc:
                span.record_exception(exc)

                span.set_attribute(
                    ("atlas.qdrant.success"),
                    False,
                )

                raise

    def hybrid_search(
        self,
        *,
        dense_query: list[float],
        sparse_query: SparseVector,
        limit: int,
        document_ids: (list[str] | None) = None,
    ) -> list[RetrievedChunk]:
        with tracer.start_as_current_span("retrieval.hybrid_search") as span:
            span.set_attribute(
                "atlas.retrieval.mode",
                "hybrid",
            )

            span.set_attribute(
                "atlas.retrieval.limit",
                limit,
            )

            span.set_attribute(
                ("atlas.retrieval.collection"),
                self._collection_name,
            )

            span.set_attribute(
                ("atlas.retrieval.dense_dimensions"),
                len(dense_query),
            )

            span.set_attribute(
                ("atlas.retrieval.sparse_terms"),
                len(sparse_query.indices),
            )

            span.set_attribute(
                ("atlas.retrieval.filtered"),
                bool(document_ids),
            )

            query_filter: Filter | None = None

            if document_ids:
                span.set_attribute(
                    ("atlas.retrieval.document_filter_count"),
                    len(document_ids),
                )

                query_filter = Filter(
                    must=[
                        FieldCondition(
                            key=("document_id"),
                            match=MatchAny(any=(document_ids)),
                        )
                    ]
                )

            try:
                response = self._client.query_points(
                    collection_name=(self._collection_name),
                    prefetch=[
                        models.Prefetch(
                            query=(dense_query),
                            using=("dense"),
                            limit=limit,
                            filter=(query_filter),
                        ),
                        models.Prefetch(
                            query=(sparse_query),
                            using=("sparse"),
                            limit=limit,
                            filter=(query_filter),
                        ),
                    ],
                    query=(models.FusionQuery(fusion=(models.Fusion.RRF))),
                    limit=limit,
                    with_payload=True,
                )

            except Exception as exc:
                span.record_exception(exc)

                span.set_attribute(
                    ("atlas.retrieval.success"),
                    False,
                )

                raise

            retrieved = self._to_chunks(response.points)

            span.set_attribute(
                ("atlas.retrieval.result_count"),
                len(retrieved),
            )

            span.set_attribute(
                ("atlas.retrieval.success"),
                True,
            )

            return retrieved

    def dense_search(
        self,
        *,
        query_vector: list[float],
        limit: int,
    ) -> list[RetrievedChunk]:
        with tracer.start_as_current_span("retrieval.dense_search") as span:
            span.set_attribute(
                "atlas.retrieval.mode",
                "dense",
            )

            span.set_attribute(
                "atlas.retrieval.limit",
                limit,
            )

            try:
                response = self._client.query_points(
                    collection_name=(self._collection_name),
                    query=(query_vector),
                    using="dense",
                    limit=limit,
                    with_payload=True,
                )

            except Exception as exc:
                span.record_exception(exc)

                span.set_attribute(
                    ("atlas.retrieval.success"),
                    False,
                )

                raise

            chunks = self._to_chunks(response.points)

            span.set_attribute(
                ("atlas.retrieval.result_count"),
                len(chunks),
            )

            span.set_attribute(
                ("atlas.retrieval.success"),
                True,
            )

            return chunks

    def sparse_search(
        self,
        *,
        query_vector: SparseVector,
        limit: int,
    ) -> list[RetrievedChunk]:
        with tracer.start_as_current_span("retrieval.sparse_search") as span:
            span.set_attribute(
                "atlas.retrieval.mode",
                "sparse",
            )

            span.set_attribute(
                "atlas.retrieval.limit",
                limit,
            )

            try:
                response = self._client.query_points(
                    collection_name=(self._collection_name),
                    query=(query_vector),
                    using="sparse",
                    limit=limit,
                    with_payload=True,
                )

            except Exception as exc:
                span.record_exception(exc)

                span.set_attribute(
                    ("atlas.retrieval.success"),
                    False,
                )

                raise

            chunks = self._to_chunks(response.points)

            span.set_attribute(
                ("atlas.retrieval.result_count"),
                len(chunks),
            )

            span.set_attribute(
                ("atlas.retrieval.success"),
                True,
            )

            return chunks

    def _to_chunks(
        self,
        points: list[Any],
    ) -> list[RetrievedChunk]:
        chunks: list[RetrievedChunk] = []

        for point in points:
            payload = point.payload or {}

            chunks.append(
                RetrievedChunk(
                    chunk_id=cast(
                        str,
                        payload["chunk_id"],
                    ),
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
                    retrieval_score=(float(point.score)),
                    rerank_score=None,
                )
            )

        return chunks
