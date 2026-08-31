from pydantic import BaseModel, Field


class DocumentIngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int


class RetrievalRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=2000,
    )


class RetrievedChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    chunk_index: int
    text: str
    score: float


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievedChunkResponse]
