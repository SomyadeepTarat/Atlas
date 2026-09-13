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
