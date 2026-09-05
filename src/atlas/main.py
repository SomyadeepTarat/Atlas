from fastapi import FastAPI

from atlas.api.middleware import (
    RequestIDMiddleware,
)
from atlas.api.routes.documents import (
    router as documents_router,
)
from atlas.api.routes.health import (
    router as health_router,
)
from atlas.api.routes.research import (
    router as research_router,
)
from atlas.api.routes.retrieval import (
    router as retrieval_router,
)
from atlas.api.routes.tools import (
    router as tools_router,
)
from atlas.core.config import get_settings

settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=("Evidence-driven AI research agent."),
)


app.add_middleware(RequestIDMiddleware)


app.include_router(
    health_router,
    prefix="/api/v1",
)

app.include_router(
    research_router,
    prefix="/api/v1",
)

app.include_router(
    documents_router,
    prefix="/api/v1",
)

app.include_router(
    retrieval_router,
    prefix="/api/v1",
)

app.include_router(
    tools_router,
    prefix="/api/v1",
)
