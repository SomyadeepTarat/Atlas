from statistics import mean
from time import perf_counter

from atlas.evals.experiments import (
    RetrievalExperiment,
)
from atlas.evals.matching import (
    relevance_flags_unique,
)
from atlas.evals.metrics.retrieval import (
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)
from atlas.evals.types import (
    EvaluationCase,
    RetrievalCaseResult,
    RetrievalExperimentResult,
)
from atlas.retrieval.service import (
    RetrievalService,
)


class RetrievalEvaluationRunner:
    def __init__(
        self,
        retrieval: RetrievalService,
    ) -> None:
        self._retrieval = retrieval

    def run(
        self,
        *,
        experiment: RetrievalExperiment,
        cases: list[EvaluationCase],
    ) -> RetrievalExperimentResult:
        results: list[RetrievalCaseResult] = []

        for case in cases:
            if case.should_abstain:
                continue

            started = perf_counter()

            chunks = self._retrieval.retrieve_for_experiment(
                query=case.question,
                mode=experiment.mode.value,
                candidate_k=experiment.candidate_k,
                final_k=experiment.final_k,
                use_reranker=(experiment.use_reranker),
                use_deduplication=(experiment.use_deduplication),
            )

            latency = perf_counter() - started

            flags = relevance_flags_unique(
                chunks=chunks,
                labels=case.relevant_evidence,
            )

            total_relevant = len(case.relevant_evidence)

            results.append(
                RetrievalCaseResult(
                    case_id=case.case_id,
                    recall_at_k=recall_at_k(
                        flags,
                        total_relevant=total_relevant,
                        k=experiment.final_k,
                    ),
                    precision_at_k=precision_at_k(
                        flags,
                        k=experiment.final_k,
                    ),
                    reciprocal_rank=(reciprocal_rank(flags)),
                    ndcg_at_k=ndcg_at_k(
                        flags,
                        k=experiment.final_k,
                    ),
                    latency_seconds=latency,
                    retrieved_chunk_ids=tuple(chunk.chunk_id for chunk in chunks),
                )
            )

        return RetrievalExperimentResult(
            experiment_name=experiment.name,
            case_results=tuple(results),
            mean_recall=mean(item.recall_at_k for item in results),
            mean_precision=mean(item.precision_at_k for item in results),
            mean_reciprocal_rank=mean(item.reciprocal_rank for item in results),
            mean_ndcg=mean(item.ndcg_at_k for item in results),
            mean_latency_seconds=mean(item.latency_seconds for item in results),
        )
