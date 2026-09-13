from sentence_transformers import (
    CrossEncoder,
)

from atlas.retrieval.types import (
    RetrievedChunk,
)
from atlas.telemetry.tracing import (
    tracer,
)


class Reranker:
    def __init__(
        self,
        *,
        model_name: str,
    ) -> None:
        self._model_name = model_name

        self._model: CrossEncoder | None = None

    def _get_model(
        self,
    ) -> CrossEncoder:
        if self._model is not None:
            return self._model

        with tracer.start_as_current_span("reranker-model-load"):
            self._model = CrossEncoder(self._model_name)

        return self._model

    def rerank(
        self,
        *,
        query: str,
        chunks: list[RetrievedChunk],
        limit: int,
    ) -> list[RetrievedChunk]:
        with tracer.start_as_current_span("reranker") as span:
            span.set_attribute(
                "atlas.reranker.model",
                self._model_name,
            )

            span.set_attribute(
                ("atlas.reranker.input_count"),
                len(chunks),
            )

            if not chunks:
                return []

            pairs = [
                (
                    query,
                    chunk.text,
                )
                for chunk in chunks
            ]

            model = self._get_model()

            try:
                scores = model.predict(pairs)

            except Exception as exc:
                span.record_exception(exc)

                raise

            reranked = [
                RetrievedChunk(
                    chunk_id=(chunk.chunk_id),
                    document_id=(chunk.document_id),
                    filename=(chunk.filename),
                    page_number=(chunk.page_number),
                    chunk_index=(chunk.chunk_index),
                    text=chunk.text,
                    retrieval_score=(chunk.retrieval_score),
                    rerank_score=(float(score)),
                )
                for chunk, score in zip(
                    chunks,
                    scores,
                    strict=True,
                )
            ]

            reranked.sort(
                key=lambda item: (
                    item.rerank_score
                    if (item.rerank_score is not None)
                    else float("-inf")
                ),
                reverse=True,
            )

            result = reranked[:limit]

            span.set_attribute(
                ("atlas.reranker.output_count"),
                len(result),
            )

            return result
