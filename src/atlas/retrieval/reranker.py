from sentence_transformers import (
    CrossEncoder,
)

from atlas.retrieval.types import (
    RetrievedChunk,
)


class Reranker:
    def __init__(
        self,
        *,
        model_name: str,
    ) -> None:
        self._model = CrossEncoder(model_name)

    def rerank(
        self,
        *,
        query: str,
        chunks: list[RetrievedChunk],
        limit: int,
    ) -> list[RetrievedChunk]:
        if not chunks:
            return []

        pairs = [
            (
                query,
                chunk.text,
            )
            for chunk in chunks
        ]

        scores = self._model.predict(pairs)

        reranked = [
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=(chunk.document_id),
                filename=chunk.filename,
                page_number=(chunk.page_number),
                chunk_index=(chunk.chunk_index),
                text=chunk.text,
                retrieval_score=float(score),
            )
            for chunk, score in zip(
                chunks,
                scores,
                strict=True,
            )
        ]

        reranked.sort(
            key=lambda item: (
                item.retrieval_score
                if item.retrieval_score is not None
                else float("-inf")
            ),
            reverse=True,
        )

        return reranked[:limit]
