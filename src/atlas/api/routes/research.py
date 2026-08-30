from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from atlas.models.dependencies import (
    get_research_model_service,
)
from atlas.models.errors import (
    AllModelsFailedError,
    ModelInvalidOutputError,
    ModelTimeoutError,
    ModelUnavailableError,
)
from atlas.models.service import (
    ResearchModelService,
)
from atlas.schemas.model import (
    ModelMetadataResponse,
    ModelTimingResponse,
    ModelUsageResponse,
    ResearchPreviewAPIResponse,
    ResearchPreviewRequest,
)

router = APIRouter(
    prefix="/research",
    tags=["research"],
)


@router.post(
    "/preview",
    response_model=ResearchPreviewAPIResponse,
)
async def research_preview(
    payload: ResearchPreviewRequest,
    request: Request,
    service: ResearchModelService = Depends(get_research_model_service),
) -> ResearchPreviewAPIResponse:
    try:
        result = await service.create_preview(payload.question)

    except ModelTimeoutError as exc:
        raise HTTPException(
            status_code=(status.HTTP_504_GATEWAY_TIMEOUT),
            detail=("The model took too long to respond."),
        ) from exc

    except ModelUnavailableError as exc:
        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail=("The model service is unavailable."),
        ) from exc

    except ModelInvalidOutputError as exc:
        raise HTTPException(
            status_code=(status.HTTP_502_BAD_GATEWAY),
            detail=("The model produced an invalid response."),
        ) from exc

    except AllModelsFailedError as exc:
        raise HTTPException(
            status_code=(status.HTTP_503_SERVICE_UNAVAILABLE),
            detail=("No configured model is currently available."),
        ) from exc

    metadata = result.metadata

    return ResearchPreviewAPIResponse(
        request_id=request.state.request_id,
        data=result.output,
        meta=ModelMetadataResponse(
            provider=metadata.provider,
            model=metadata.model,
            attempts=metadata.attempts,
            usage=ModelUsageResponse(
                input_tokens=(metadata.usage.input_tokens),
                output_tokens=(metadata.usage.output_tokens),
            ),
            timings=ModelTimingResponse(
                total_seconds=(metadata.timings.total_seconds),
                load_seconds=(metadata.timings.load_seconds),
                prompt_eval_seconds=(metadata.timings.prompt_eval_seconds),
                generation_seconds=(metadata.timings.generation_seconds),
            ),
        ),
    )
