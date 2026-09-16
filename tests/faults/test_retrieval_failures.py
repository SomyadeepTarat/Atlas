from typing import Any

import pytest
from langgraph.errors import GraphRecursionError

from atlas.research.errors import (
    WorkflowDeadlineExceededError,
)
from atlas.research.service import (
    ResearchService,
)


class FailingEmbeddingService:
    def embed_query_dense(
        self,
        query: str,
    ) -> list[float]:
        raise RuntimeError("Embedding model unavailable.")

    def embed_query_sparse(
        self,
        query: str,
    ) -> Any:
        raise RuntimeError("Sparse embedding unavailable.")


class FailingVectorStore:
    def hybrid_search(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> list[Any]:
        raise RuntimeError("Vector database unavailable.")


def test_dense_embedding_failure_propagates() -> None:
    service = FailingEmbeddingService()

    with pytest.raises(
        RuntimeError,
        match="Embedding model unavailable",
    ):
        service.embed_query_dense("What is RAG?")


def test_sparse_embedding_failure_propagates() -> None:
    service = FailingEmbeddingService()

    with pytest.raises(
        RuntimeError,
        match="Sparse embedding unavailable",
    ):
        service.embed_query_sparse("What is RAG?")


def test_vector_store_failure_propagates() -> None:
    store = FailingVectorStore()

    with pytest.raises(
        RuntimeError,
        match="Vector database unavailable",
    ):
        store.hybrid_search(
            dense_vector=[0.1, 0.2],
            sparse_vector=None,
            limit=10,
        )


class RunawayGraph:
    async def ainvoke(
        self,
        state: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        raise GraphRecursionError("Recursion limit reached.")


@pytest.mark.asyncio
async def test_graph_recursion_is_converted_to_domain_error() -> None:
    service = ResearchService(
        RunawayGraph(),
        max_iterations=3,
        deadline_seconds=10.0,
    )

    with pytest.raises(
        WorkflowDeadlineExceededError,
        match="graph execution budget",
    ):
        await service.answer(
            "Test question",
            thread_id=("00000000-0000-0000-0000-000000000001"),
        )
