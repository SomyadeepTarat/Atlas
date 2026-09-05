from dataclasses import dataclass

from atlas.schemas.model import (
    GroundedAnswer,
)


@dataclass(frozen=True)
class ResearchWorkflowResult:
    answer: GroundedAnswer

    iterations: int

    verification_passed: bool

    verification_reason: str | None
