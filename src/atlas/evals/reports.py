import csv
from pathlib import Path

from atlas.evals.types import (
    RetrievalExperimentResult,
)


def write_retrieval_csv(
    results: list[RetrievalExperimentResult],
    path: Path,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "experiment",
        "mean_recall",
        "mean_precision",
        "mean_mrr",
        "mean_ndcg",
        "mean_latency_seconds",
    ]

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "experiment": (result.experiment_name),
                    "mean_recall": (result.mean_recall),
                    "mean_precision": (result.mean_precision),
                    "mean_mrr": (result.mean_reciprocal_rank),
                    "mean_ndcg": (result.mean_ndcg),
                    "mean_latency_seconds": (result.mean_latency_seconds),
                }
            )
