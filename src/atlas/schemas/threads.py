from uuid import UUID

from pydantic import BaseModel, Field


class CreateThreadRequest(BaseModel):
    title: str | None = Field(
        default=None,
        max_length=300,
    )


class ThreadResponse(BaseModel):
    id: UUID
    title: str | None


class MessageResponse(BaseModel):
    role: str
    content: str
