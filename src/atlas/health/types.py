from enum import StrEnum

from pydantic import BaseModel


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyStatus(BaseModel):
    name: str
    status: HealthStatus

    latency_seconds: float | None = None

    message: str | None = None


class HealthReport(BaseModel):
    status: HealthStatus

    dependencies: list[DependencyStatus]
