from uuid import UUID

from sqlalchemy import select

from atlas.db.models import MemoryRecord
from atlas.db.repositories.memories import (
    MemoryRepository,
)
from atlas.memory.policy import (
    MemoryPolicy,
)
from atlas.models.service import (
    ResearchModelService,
)


class MemoryService:
    def __init__(
        self,
        *,
        repository: MemoryRepository,
        model: ResearchModelService,
        policy: MemoryPolicy,
    ) -> None:
        self._repository = repository
        self._model = model
        self._policy = policy

    async def consider_message(
        self,
        *,
        user_message: str,
        thread_id: UUID,
    ) -> None:
        extract_memory_candidate = self._model.extract_memory_candidate
        result = await extract_memory_candidate(
            user_message=user_message,
            assistant_message="",
        )

        candidate = result.output

        if not self._policy.should_store(candidate):
            return

        if candidate.content is None:
            return

        existing = await self.find_by_content(candidate.content)

        if existing is not None:
            return

        await self._repository.create(
            memory_type=(candidate.memory_type or "fact"),
            content=(candidate.content or ""),
            source_thread_id=thread_id,
            confidence=candidate.confidence,
        )

    async def find_by_content(
        self,
        content: str,
    ) -> MemoryRecord | None:
        statement = select(MemoryRecord).where(MemoryRecord.content == content).limit(1)

        result = await self._repository._session.execute(statement)

        return result.scalar_one_or_none()
