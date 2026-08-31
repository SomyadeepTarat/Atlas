from pydantic import BaseModel


class DocumentIngestResponse(BaseModel):
    document_id: str
    filename: str
    chunks_created: int


class RetrievalRequest(BaseModel):
    query: str
    document_ids: list[str] | None = None


class RetrievedChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page_number: int
    chunk_index: int
    text: str
    retrieval_score: float
    rerank_score: float | None


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievedChunkResponse]
