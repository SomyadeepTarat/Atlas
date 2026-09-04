import json
from dataclasses import asdict
from pathlib import Path

from atlas.evals.types import (
    RetrievalExperimentResult,
)


def write_result_json(
    result: RetrievalExperimentResult,
    *,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = output_dir / (f"{result.experiment_name}.json")

    path.write_text(
        json.dumps(
            asdict(result),
            indent=2,
        ),
        encoding="utf-8",
    )

    return path
