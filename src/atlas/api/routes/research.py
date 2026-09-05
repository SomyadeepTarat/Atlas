from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from atlas.models.errors import (
    AllModelsFailedError,
)
from atlas.research.dependencies import (
    get_research_service,
)
from atlas.research.service import (
    ResearchService,
)
from atlas.schemas.model import (
    GroundedAnswerAPIResponse,
    ResearchAnswerRequest,
)

router = APIRouter(
    prefix="/research",
    tags=["research"],
)


@router.post(
    "/answer",
    response_model=GroundedAnswerAPIResponse,
)
async def answer_research_question(
    payload: ResearchAnswerRequest,
    request: Request,
    service: ResearchService = Depends(get_research_service),
) -> GroundedAnswerAPIResponse:
    thread_id = request.headers.get("X-Thread-ID") or str(uuid4())

    try:
        result = await service.answer(
            payload.question,
            thread_id=thread_id,
        )

    except AllModelsFailedError as exc:
        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail=("No configured model is currently available."),
        ) from exc

    return GroundedAnswerAPIResponse(
        data=result.answer,
        thread_id=thread_id,
        iterations=result.iterations,
        verification_passed=(result.verification_passed),
        verification_reason=(result.verification_reason),
    )
