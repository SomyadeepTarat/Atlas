from __future__ import annotations

from typing import TypedDict

from atlas.retrieval.types import RetrievedChunk
from atlas.schemas.model import (
    AnswerVerification,
    EvidenceAssessment,
    GroundedAnswer,
    ResearchPlan,
)


class ResearchWorkflowState(TypedDict, total=False):
    question: str

    plan: ResearchPlan
    queries: list[str]

    retrieved_chunks: list[RetrievedChunk]
    context_chunks: list[RetrievedChunk]
    context: str

    evidence_assessment: EvidenceAssessment
    answer: GroundedAnswer
    verification: AnswerVerification

    iteration: int
    max_iterations: int

    repair_attempts: int
    max_repair_attempts: int

    verification_passed: bool
    verification_reason: str | None
    evidence_sufficient: bool
