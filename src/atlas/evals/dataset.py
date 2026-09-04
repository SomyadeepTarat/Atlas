import json
from pathlib import Path

from atlas.evals.types import (
    EvaluationCase,
    EvidenceLabel,
)


def load_dataset(
    path: Path,
) -> list[EvaluationCase]:
    raw = json.loads(path.read_text(encoding="utf-8"))

    cases: list[EvaluationCase] = []

    for item in raw:
        evidence = [
            EvidenceLabel(
                document_id=label["document_id"],
                page_number=label.get("page_number"),
                text_contains=label.get("text_contains"),
                chunk_id=label.get("chunk_id"),
            )
            for label in item["relevant_evidence"]
        ]

        cases.append(
            EvaluationCase(
                case_id=item["case_id"],
                question=item["question"],
                relevant_evidence=evidence,
                expected_answer=item.get("expected_answer"),
                should_abstain=item.get(
                    "should_abstain",
                    False,
                ),
                tags=tuple(item.get("tags", [])),
            )
        )

    return cases
