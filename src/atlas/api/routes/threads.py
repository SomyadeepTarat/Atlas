from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from atlas.db.repositories.threads import (
    ThreadRepository,
)
from atlas.db.session import get_db_session
from atlas.schemas.threads import (
    CreateThreadRequest,
    ThreadResponse,
)

router = APIRouter(
    prefix="/threads",
    tags=["threads"],
)


@router.post("")
async def create_thread(
    payload: CreateThreadRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ThreadResponse:
    repository = ThreadRepository(session)

    thread = await repository.create_thread(title=payload.title)

    return ThreadResponse(
        id=thread.id,
        title=thread.title,
    )


@router.get("")
async def list_threads(
    session: AsyncSession = Depends(get_db_session),
) -> list[ThreadResponse]:
    repository = ThreadRepository(session)

    threads = await repository.list_threads()

    return [
        ThreadResponse(
            id=thread.id,
            title=thread.title,
        )
        for thread in threads
    ]
