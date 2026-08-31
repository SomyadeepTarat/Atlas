from pydantic import BaseModel, Field


class ResearchPreviewRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
        description=("Research question supplied by the user."),
    )


class ResearchPreviewResponse(BaseModel):
    answer: str = Field(description=("A concise preliminary answer."))

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
    load_seconds: float | None
    prompt_eval_seconds: float | None
    generation_seconds: float | None


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
        description=(
            "Answer grounded only in "
            "the supplied context."
        )
    )

    used_chunk_ids: list[str] = Field(
        description=(
            "IDs of context chunks "
            "used to support the answer."
        )
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    insufficient_context: bool = Field(
        description=(
            "Whether the supplied "
            "context is insufficient "
            "to answer reliably."
        )
    )