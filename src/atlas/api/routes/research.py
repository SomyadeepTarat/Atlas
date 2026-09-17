import logging
from collections.abc import (
    AsyncIterator,
)
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.sse import (
    EventSourceResponse,
    ServerSentEvent,
)

from atlas.models.errors import (
    AllModelsFailedError,
)
from atlas.research.dependencies import (
    get_research_service,
    get_research_stream_adapter,
)
from atlas.research.service import (
    ResearchService,
)
from atlas.research.streaming import (
    ResearchStreamAdapter,
)
from atlas.schemas.model import (
    GroundedAnswerAPIResponse,
    ResearchAnswerRequest,
)
from atlas.schemas.streaming import (
    ResearchEventType,
    ResearchStage,
    ResearchStreamEvent,
    ResearchStreamRequest,
)

router = APIRouter(
    prefix="/research",
    tags=["research"],
)
logger = logging.getLogger(__name__)


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


@router.post(
    "/threads/{thread_id}/stream",
    response_class=EventSourceResponse,
)
async def stream_research(
    thread_id: str,
    payload: ResearchStreamRequest,
    adapter: ResearchStreamAdapter = Depends(get_research_stream_adapter),
) -> AsyncIterator[ServerSentEvent]:
    sequence = 0

    try:
        async for event in adapter.stream(
            question=payload.question,
            thread_id=thread_id,
        ):
            sequence = event.sequence

            yield ServerSentEvent(
                event=event.type.value,
                id=str(event.sequence),
                data=event.model_dump(mode="json"),
            )

    except Exception:
        logger.exception(
            "research.stream.failed",
            extra={
                "thread_id": thread_id,
                "sequence": sequence,
            },
        )

        error = ResearchStreamEvent(
            type=ResearchEventType.ERROR,
            stage=ResearchStage.COMPLETE,
            message=("Research could not be completed."),
            sequence=sequence + 1,
        )

        yield ServerSentEvent(
            event="error",
            id=str(error.sequence),
            data=error.model_dump(mode="json"),
        )
