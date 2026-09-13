from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from atlas.db.models import (
    Message,
    ResearchThread,
)


class ThreadRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create_thread(
        self,
        *,
        title: str | None = None,
    ) -> ResearchThread:
        thread = ResearchThread(title=title)

        self._session.add(thread)

        await self._session.commit()

        await self._session.refresh(thread)

        return thread

    async def add_message(
        self,
        *,
        thread_id: UUID,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> Message:
        message = Message(
            thread_id=thread_id,
            role=role,
            content=content,
            metadata_json=(metadata or {}),
        )

        self._session.add(message)

        await self._session.commit()

        await self._session.refresh(message)

        return message

    async def get_messages(
        self,
        *,
        thread_id: UUID,
        limit: int = 50,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.thread_id == thread_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())
