from contextlib import (
    asynccontextmanager,
)

from fastapi import FastAPI
from langgraph.checkpoint.postgres.aio import (
    AsyncPostgresSaver,
)
from opentelemetry.instrumentation.fastapi import (
    FastAPIInstrumentor,
)
from opentelemetry.instrumentation.httpx import (
    HTTPXClientInstrumentor,
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
from atlas.telemetry.logging import (
    configure_logging,
)
from atlas.telemetry.middleware import (
    RequestContextMiddleware,
)
from atlas.telemetry.setup import (
    configure_telemetry,
)
from atlas.telemetry.tracing import (
    get_langfuse,
    shutdown_tracing,
)

settings = get_settings()
configure_telemetry(settings)
configure_logging(level=settings.log_level)

HTTPXClientInstrumentor().instrument()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    get_langfuse()

    settings = get_settings()

    async with AsyncPostgresSaver.from_conn_string(
        settings.langgraph_database_url
    ) as checkpointer:
        await checkpointer.setup()

        app.state.langgraph_checkpointer = checkpointer

        yield

    shutdown_tracing()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=("Evidence-driven AI research agent."),
    lifespan=lifespan,
)

FastAPIInstrumentor.instrument_app(app)


app.add_middleware(RequestContextMiddleware)


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
