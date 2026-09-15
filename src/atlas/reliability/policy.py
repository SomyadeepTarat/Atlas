from dataclasses import dataclass


@dataclass(frozen=True)
class ReliabilityPolicy:
    research_deadline_seconds: float

    model_concurrency: int

    reranker_concurrency: int

    circuit_failure_threshold: int

    circuit_recovery_seconds: float
