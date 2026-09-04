from dataclasses import dataclass
from enum import StrEnum


class RetrievalMode(StrEnum):
    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class RetrievalExperiment:
    name: str

    mode: RetrievalMode

    use_reranker: bool

    use_deduplication: bool

    candidate_k: int

    final_k: int


EXPERIMENTS = [
    RetrievalExperiment(
        name="dense",
        mode=RetrievalMode.DENSE,
        use_reranker=False,
        use_deduplication=False,
        candidate_k=5,
        final_k=5,
    ),
    RetrievalExperiment(
        name="sparse",
        mode=RetrievalMode.SPARSE,
        use_reranker=False,
        use_deduplication=False,
        candidate_k=5,
        final_k=5,
    ),
    RetrievalExperiment(
        name="hybrid",
        mode=RetrievalMode.HYBRID,
        use_reranker=False,
        use_deduplication=False,
        candidate_k=5,
        final_k=5,
    ),
    RetrievalExperiment(
        name="hybrid-rerank",
        mode=RetrievalMode.HYBRID,
        use_reranker=True,
        use_deduplication=False,
        candidate_k=20,
        final_k=5,
    ),
    RetrievalExperiment(
        name="hybrid-rerank-dedupe",
        mode=RetrievalMode.HYBRID,
        use_reranker=True,
        use_deduplication=True,
        candidate_k=20,
        final_k=5,
    ),
]
