from enum import StrEnum


class MemoryType(StrEnum):
    PREFERENCE = "preference"

    FACT = "fact"

    DECISION = "decision"

    EPISODE = "episode"
