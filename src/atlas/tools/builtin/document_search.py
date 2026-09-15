import asyncio

from pydantic import BaseModel, Field

from atlas.retrieval.service import (
    RetrievalService,
)
from atlas.tools.base import Tool
from atlas.tools.types import (
    ToolPermission,
    ToolPolicy,
    ToolRisk,
)


class DocumentSearchInput(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=2000,
    )

    document_ids: list[str] | None = None


class DocumentSearchResult(BaseModel):
    chunk_id: str

    document_id: str

    filename: str

    page_number: int

    text: str

    retrieval_score: float

    rerank_score: float | None = None


class DocumentSearchOutput(BaseModel):
    results: list[DocumentSearchResult]


class DocumentSearchTool(
    Tool[
        DocumentSearchInput,
        DocumentSearchOutput,
    ]
):
    name = "search_documents"

    description = (
        "Search indexed research documents for passages relevant to a question."
    )

    input_schema = DocumentSearchInput

    output_schema = DocumentSearchOutput

    policy = ToolPolicy(
        risk=ToolRisk.READ_ONLY,
        required_permissions=frozenset(
            {
                ToolPermission.DOCUMENT_READ,
            }
        ),
        requires_approval=False,
        timeout_seconds=10.0,
        max_attempts=1,
        idempotent=True,
    )

    def __init__(
        self,
        retrieval: RetrievalService,
    ) -> None:
        self._retrieval = retrieval

    async def execute(
        self,
        input_data: DocumentSearchInput,
    ) -> DocumentSearchOutput:
        retrieval_result = await asyncio.to_thread(
            self._retrieval.retrieve_context,
            input_data.query,
        )
        chunks = retrieval_result.chunks

        return DocumentSearchOutput(
            results=[
                DocumentSearchResult(
                    chunk_id=chunk.chunk_id,
                    document_id=(chunk.document_id),
                    filename=(chunk.filename),
                    page_number=(chunk.page_number),
                    text=chunk.text,
                    retrieval_score=(chunk.retrieval_score),
                    rerank_score=(chunk.rerank_score),
                )
                for chunk in chunks
            ]
        )
