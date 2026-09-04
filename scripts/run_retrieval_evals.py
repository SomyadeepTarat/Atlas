from pathlib import Path

from atlas.evals.dataset import (
    load_dataset,
)
from atlas.evals.experiments import (
    EXPERIMENTS,
)
from atlas.evals.runner import (
    RetrievalEvaluationRunner,
)
from atlas.retrieval.dependencies import (
    get_retrieval_service,
)


def main() -> None:
    dataset = load_dataset(Path("evals/datasets/retrieval_v1.json"))

    retrieval = get_retrieval_service()

    runner = RetrievalEvaluationRunner(retrieval)

    for experiment in EXPERIMENTS:
        result = runner.run(
            experiment=experiment,
            cases=dataset,
        )

        print()
        print(f"=== {result.experiment_name} ===")

        print(
            "Recall:",
            round(
                result.mean_recall,
                4,
            ),
        )

        print(
            "Precision:",
            round(
                result.mean_precision,
                4,
            ),
        )

        print(
            "MRR:",
            round(
                result.mean_reciprocal_rank,
                4,
            ),
        )

        print(
            "nDCG:",
            round(
                result.mean_ndcg,
                4,
            ),
        )

        print(
            "Latency:",
            round(
                result.mean_latency_seconds,
                4,
            ),
            "s",
        )


if __name__ == "__main__":
    main()
