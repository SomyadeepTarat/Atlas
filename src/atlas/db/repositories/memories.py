from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from qdrant_client.models import BaseModel, Field
from sqlalchemy import (
    or_,
    select,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from atlas.db.models import (
    MemoryRecord,
)
from atlas.models.types import ModelResult


class MemoryRepository:
    def __init__(
        self,
        session: AsyncSession,
        model_client,
    ) -> None:
        self._session = session
        self._model_client = model_client

    async def create(
        self,
        *,
        memory_type: str,
        content: str,
        source_thread_id: UUID | None,
        confidence: float,
        expires_at: datetime | None = None,
        metadata: dict | None = None,
    ) -> MemoryRecord:
        memory = MemoryRecord(
            memory_type=memory_type,
            content=content,
            source_thread_id=(source_thread_id),
            confidence=confidence,
            expires_at=expires_at,
            metadata_json=metadata or {},
        )

        self._session.add(memory)

        await self._session.commit()

        await self._session.refresh(memory)

        return memory

    async def list_active(
        self,
        *,
        limit: int = 100,
    ) -> list[MemoryRecord]:
        now = datetime.now(UTC)

        statement = (
            select(MemoryRecord)
            .where(
                or_(
                    MemoryRecord.expires_at.is_(None),
                    MemoryRecord.expires_at > now,
                )
            )
            .order_by(MemoryRecord.updated_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def delete(
        self,
        memory_id: UUID,
    ) -> bool:
        memory = await self._session.get(
            MemoryRecord,
            memory_id,
        )

        if memory is None:
            return False

        await self._session.delete(memory)

        await self._session.commit()

        return True

    async def extract_memory_candidate(
        self,
        *,
        user_message: str,
    ) -> ModelResult[MemoryCandidate]:
        system_prompt = """
You identify whether a user message contains
information useful for future interactions.

Store only information that is likely to remain
useful beyond the current conversation.

Good candidates include:
- durable preferences
- persistent project context
- explicit decisions
- stable recurring requirements

Do NOT store:
- temporary requests
- arbitrary conversation details
- passwords or credentials
- sensitive personal information
- content that only matters for the current answer

If nothing should be stored, set should_store=false.
""".strip()

        return await self._model_client.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_message,
            output_schema=MemoryCandidate,
        )


class MemoryCandidate(BaseModel):
    should_store: bool

    memory_type: str | None = None

    content: str | None = None

    confidence: float = Field(
        ge=0,
        le=1,
    )

    reason: str
