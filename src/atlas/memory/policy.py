from typing import Any

from atlas.memory.types import (
    MemoryType,
)


class MemoryPolicy:
    def should_store(
        self,
        candidate: Any,
    ) -> bool:
        if not candidate.should_store:
            return False

        if not candidate.content:
            return False

        if candidate.confidence < 0.75:
            return False

        if candidate.memory_type not in {item.value for item in MemoryType}:
            return False

        return True
