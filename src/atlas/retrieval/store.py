from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
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
        client: QdrantClient | None = None,
        url: str | None = None,
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
            collection_name=(self._collection_name),
            vectors_config=VectorParams(
                size=self._vector_size,
                distance=Distance.COSINE,
            ),
        )

    def upsert(
        self,
        *,
        chunks: list[DocumentChunk],
        vectors: list[list[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Chunks and vectors must have the same length.")

        points = [
            PointStruct(
                id=chunk.chunk_id,
                vector=vector,
                payload={
                    "document_id": (chunk.document_id),
                    "filename": (chunk.filename),
                    "page_number": (chunk.page_number),
                    "chunk_index": (chunk.chunk_index),
                    "text": chunk.text,
                },
            )
            for chunk, vector in zip(
                chunks,
                vectors,
                strict=True,
            )
        ]

        self._client.upsert(
            collection_name=(self._collection_name),
            points=points,
            wait=True,
        )

    def search(
        self,
        *,
        query_vector: list[float],
        limit: int,
    ) -> list[RetrievedChunk]:
        results = self._client.query_points(
            collection_name=(self._collection_name),
            query=query_vector,
            limit=limit,
            with_payload=True,
        ).points

        retrieved: list[RetrievedChunk] = []

        for result in results:
            payload = result.payload or {}

            retrieved.append(
                RetrievedChunk(
                    chunk_id=str(result.id),
                    document_id=str(payload["document_id"]),
                    filename=str(payload["filename"]),
                    page_number=int(payload["page_number"]),
                    chunk_index=int(payload["chunk_index"]),
                    text=str(payload["text"]),
                    score=float(result.score),
                )
            )

        return retrieved
