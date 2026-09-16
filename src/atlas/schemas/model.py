from typing import Any

from pydantic import BaseModel, Field

from atlas.core.config import get_settings

settings = get_settings()


class ResearchPreviewRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
        description="Research question supplied by the user.",
    )


class ResearchPreviewResponse(BaseModel):
    answer: str = Field(
        description="A concise preliminary answer.",
    )

    key_points: list[str] = Field(
        min_length=1,
        max_length=5,
        description="Important relevant points.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )


class ModelUsageResponse(BaseModel):
    input_tokens: int
    output_tokens: int


class ModelTimingResponse(BaseModel):
    total_seconds: float
    load_seconds: float | None = None
    prompt_eval_seconds: float | None = None
    generation_seconds: float | None = None


class ModelMetadataResponse(BaseModel):
    provider: str
    model: str
    attempts: int
    usage: ModelUsageResponse
    timings: ModelTimingResponse


class ResearchPreviewAPIResponse(BaseModel):
    request_id: str
    data: ResearchPreviewResponse
    meta: ModelMetadataResponse


class GroundedAnswer(BaseModel):
    answer: str = Field(
        description=("Answer grounded only in the supplied context."),
    )

    used_chunk_ids: list[str] = Field(
        description=("IDs of context chunks used to support the answer."),
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    insufficient_context: bool = Field(
        description=(
            "Whether the supplied context is insufficient to answer reliably."
        ),
    )


class ResearchAnswerRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=(settings.max_user_question_chars),
    )


class GroundedAnswerAPIResponse(BaseModel):
    data: GroundedAnswer

    thread_id: str

    iterations: int = Field(
        ge=1,
    )

    verification_passed: bool

    verification_reason: str | None = None


class ResearchPlan(BaseModel):
    queries: list[str] = Field(
        min_length=1,
        max_length=4,
        description=(
            "Focused retrieval queries required to answer the research question."
        ),
    )

    reasoning_summary: str = Field(
        description=("Short explanation of the research strategy."),
    )


class EvidenceAssessment(BaseModel):
    sufficient: bool

    reason: str = Field(
        description=(
            "Brief explanation of whether the retrieved evidence is sufficient."
        ),
    )

    missing_information: list[str] = Field(
        default_factory=list,
        description=("Information still required to answer the research question."),
    )


class AnswerVerification(BaseModel):
    supported: bool

    reason: str

    unsupported_claims: list[str] = Field(
        default_factory=list,
    )


class ToolDecision(BaseModel):
    use_tool: bool

    tool_name: str | None = None

    arguments: dict = Field(default_factory=dict)

    reason: str


class ToolExecuteRequest(BaseModel):
    tool_name: str

    arguments: dict[str, Any]

    permissions: list[str]

    approved_tools: list[str] = Field(default_factory=list)


class MemoryCandidate(BaseModel):
    should_store: bool = Field(
        description=(
            "Whether this information is useful enough to persist as long-term memory."
        )
    )

    memory_type: str | None = Field(
        default=None,
        description=(
            "Category of memory, such as preference, fact, project, or instruction."
        ),
    )

    content: str | None = Field(
        default=None,
        description=("Concise normalized memory content."),
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description=("Confidence that this information should be stored."),
    )
