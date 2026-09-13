from atlas.db.models import (
    MemoryRecord,
)


def build_memory_context(
    memories: list[MemoryRecord],
) -> str:
    if not memories:
        return ""

    lines = ["Relevant persistent context:"]

    for memory in memories:
        lines.append(f"- [{memory.memory_type}] {memory.content}")

    return "\n".join(lines)
