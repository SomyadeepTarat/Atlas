from fastapi import FastAPI

from atlas.api.routes.health import router as health_router
from atlas.api.routes.research import router as research_router
from atlas.core.config import get_settings


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Evidence-driven AI research agent.",
)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    research_router,
    prefix="/api/v1",
)