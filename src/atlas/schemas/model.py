from pydantic import BaseModel, Field


class ResearchPreviewRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
        description="Research question supplied by the user.",
    )


class ResearchPreviewResponse(BaseModel):
    answer: str = Field(
        description="A concise preliminary answer to the research question."
    )

    key_points: list[str] = Field(
        min_length=1,
        max_length=5,
        description="Important points relevant to the question.",
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Model-estimated confidence in the answer.",
    )