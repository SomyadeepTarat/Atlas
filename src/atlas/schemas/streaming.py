from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from atlas.schemas.model import GroundedAnswer


class ResearchEventType(StrEnum):
    STARTED = "started"
    STATUS = "status"
    RETRIEVAL = "retrieval"
    ANSWER = "answer"
    COMPLETE = "complete"
    ERROR = "error"


class ResearchStage(StrEnum):
    STARTING = "starting"
    PLANNING = "planning"
    RETRIEVING = "retrieving"
    ASSESSING = "assessing"
    SYNTHESIZING = "synthesizing"
    VERIFYING = "verifying"
    REPAIRING = "repairing"
    COMPLETE = "complete"


class ResearchStreamEvent(BaseModel):
    type: ResearchEventType

    stage: ResearchStage

    message: str

    sequence: int = Field(ge=0)

    data: dict[str, Any] = Field(default_factory=dict)


class ResearchCompleteData(BaseModel):
    answer: GroundedAnswer

    iterations: int

    verification_passed: bool

    verification_reason: str | None = None


class ResearchStreamRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=10_000,
    )


class ResearchSource(BaseModel):
    chunk_id: str

    filename: str

    page_number: int

    text_preview: str
