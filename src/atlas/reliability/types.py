from enum import StrEnum


class DependencyName(StrEnum):
    MODEL = "model"
    QDRANT = "qdrant"
    POSTGRES = "postgres"
    RERANKER = "reranker"
    EMBEDDING = "embedding"
    MCP = "mcp"


class FailureAction(StrEnum):
    RETRY = "retry"
    FALLBACK = "fallback"
    DEGRADE = "degrade"
    ABSTAIN = "abstain"
    FAIL = "fail"
