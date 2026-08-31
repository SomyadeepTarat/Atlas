from fastapi import (
    APIRouter,
    Depends,
)

from atlas.retrieval.dependencies import (
    get_retrieval_service,
)
from atlas.retrieval.service import (
    RetrievalService,
)
from atlas.schemas.retrieval import (
    RetrievalRequest,
    RetrievalResponse,
    RetrievedChunkResponse,
)

router = APIRouter(
    prefix="/retrieval",
    tags=["retrieval"],
)


@router.post(
    "/search",
    response_model=RetrievalResponse,
)
async def search_documents(
    payload: RetrievalRequest,
    retrieval: RetrievalService = Depends(get_retrieval_service),
) -> RetrievalResponse:
    results = retrieval.search_candidates(
        payload.query,
        document_ids=payload.document_ids,
    )

    return RetrievalResponse(
        query=payload.query,
        results=[
            RetrievedChunkResponse(
                chunk_id=item.chunk_id,
                document_id=item.document_id,
                filename=item.filename,
                page_number=item.page_number,
                chunk_index=item.chunk_index,
                text=item.text,
                retrieval_score=item.retrieval_score,
                rerank_score=item.rerank_score,
            )
            for item in results
        ],
    )
