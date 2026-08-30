from fastapi import APIRouter, Depends, HTTPException, status

from atlas.models.dependencies import get_research_model_service
from atlas.models.errors import (
    ModelInvalidOutputError,
    ModelTimeoutError,
    ModelUnavailableError,
)
from atlas.models.service import ResearchModelService
from atlas.schemas.model import (
    ResearchPreviewRequest,
    ResearchPreviewResponse,
)


router = APIRouter(
    prefix="/research",
    tags=["research"],
)


@router.post(
    "/preview",
    response_model=ResearchPreviewResponse,
)
async def research_preview(
    request: ResearchPreviewRequest,
    service: ResearchModelService = Depends(
        get_research_model_service
    ),
) -> ResearchPreviewResponse:
    try:
        return await service.create_preview(request.question)

    except ModelTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The model took too long to respond.",
        ) from exc

    except ModelUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The model service is unavailable.",
        ) from exc

    except ModelInvalidOutputError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The model produced an invalid response.",
        ) from exc