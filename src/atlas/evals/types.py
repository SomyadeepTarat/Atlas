from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidenceLabel:
    document_id: str
    page_number: int | None = None
    text_contains: str | None = None
    chunk_id: str | None = None


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    question: str

    relevant_evidence: list[EvidenceLabel]

    expected_answer: str | None = None

    should_abstain: bool = False

    tags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RetrievalCaseResult:
    case_id: str

    recall_at_k: float
    precision_at_k: float
    reciprocal_rank: float
    ndcg_at_k: float

    latency_seconds: float

    retrieved_chunk_ids: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalExperimentResult:
    experiment_name: str

    case_results: tuple[RetrievalCaseResult, ...]

    mean_recall: float
    mean_precision: float
    mean_reciprocal_rank: float
    mean_ndcg: float

    mean_latency_seconds: float
