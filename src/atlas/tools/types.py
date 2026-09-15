from dataclasses import dataclass
from enum import StrEnum


class ToolRisk(StrEnum):
    READ_ONLY = "read_only"
    LOW_RISK_WRITE = "low_risk_write"
    HIGH_RISK_WRITE = "high_risk_write"


class ToolPermission(StrEnum):
    DOCUMENT_READ = "document_read"
    WEB_READ = "web_read"
    CALCULATE = "calculate"
    EXTERNAL_WRITE = "external_write"


class GroundingPolicy(StrEnum):
    NONE = "none"
    OPTIONAL = "optional"
    REQUIRED = "required"


@dataclass(frozen=True)
class ToolPolicy:
    risk: ToolRisk
    required_permissions: frozenset[ToolPermission]
    requires_approval: bool
    timeout_seconds: float
    max_attempts: int
    idempotent: bool


class ToolOutcome(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ToolMetadata:
    tool_name: str
    attempts: int
    duration_seconds: float


@dataclass(frozen=True)
class ToolResult[OutputT]:
    output: OutputT
    metadata: ToolMetadata
    outcome: ToolOutcome


@dataclass(frozen=True)
class ToolExecutionContext:
    permissions: frozenset[ToolPermission]
    approved_tools: frozenset[str] = frozenset()
    grounding_policy: GroundingPolicy = GroundingPolicy.NONE
