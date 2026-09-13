from langgraph.checkpoint.postgres.aio import (
    AsyncPostgresSaver,
)

from atlas.core.config import (
    get_settings,
)


async def create_checkpointer():
    settings = get_settings()

    context_manager = AsyncPostgresSaver.from_conn_string(
        settings.langgraph_database_url
    )

    checkpointer = await context_manager.__aenter__()

    return (
        checkpointer,
        context_manager,
    )
