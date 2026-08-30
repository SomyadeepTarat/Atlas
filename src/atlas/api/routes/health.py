from fastapi import (
    APIRouter,
    Depends,
    Response,
    status,
)

from atlas.models.base import ModelClient
from atlas.models.dependencies import (
    get_model_client,
)

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "atlas-api",
    }


@router.get("/ready")
async def readiness(
    response: Response,
    model_client: ModelClient = Depends(get_model_client),
) -> dict[str, str]:
    ready = await model_client.is_ready()

    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return {
            "status": "not_ready",
            "model": "unavailable",
        }

    return {
        "status": "ready",
        "model": "available",
    }
