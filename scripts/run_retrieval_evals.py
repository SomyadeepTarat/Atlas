from pathlib import Path

from atlas.evals.dataset import (
    load_dataset,
)
from atlas.evals.experiments import (
    EXPERIMENTS,
)
from atlas.evals.reports import (
    write_retrieval_csv,
)
from atlas.evals.runner import (
    RetrievalEvaluationRunner,
)
from atlas.evals.types import (
    RetrievalExperimentResult,
)
from atlas.retrieval.dependencies import (
    get_retrieval_service,
)


def main() -> None:
    dataset_path = Path("evals/datasets/retrieval_v1.json")

    output_dir = Path("benchmarks/atlas-v1")

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset = load_dataset(dataset_path)

    retrieval = get_retrieval_service()

    runner = RetrievalEvaluationRunner(retrieval)

    results: list[RetrievalExperimentResult] = []

    for experiment in EXPERIMENTS:
        result = runner.run(
            experiment=experiment,
            cases=dataset,
        )

        results.append(result)

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

    write_retrieval_csv(
        results,
        output_dir / "retrieval-results.csv",
    )

    print()
    print(
        "Results written to:",
        output_dir / "retrieval-results.csv",
    )


if __name__ == "__main__":
    main()
