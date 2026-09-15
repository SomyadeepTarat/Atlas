from collections.abc import (
    Awaitable,
    Callable,
)
from time import monotonic

from atlas.health.types import (
    DependencyStatus,
    HealthReport,
    HealthStatus,
)

HealthCheck = Callable[
    [],
    Awaitable[None],
]


class HealthService:
    def __init__(
        self,
        *,
        postgres_check: HealthCheck,
        qdrant_check: HealthCheck,
        model_check: HealthCheck,
    ) -> None:
        self._postgres_check = postgres_check

        self._qdrant_check = qdrant_check

        self._model_check = model_check

    async def _run_check(
        self,
        *,
        name: str,
        check: HealthCheck,
    ) -> DependencyStatus:
        started_at = monotonic()

        try:
            await check()

        except Exception as exc:
            return DependencyStatus(
                name=name,
                status=(HealthStatus.UNHEALTHY),
                latency_seconds=(monotonic() - started_at),
                message=str(exc),
            )

        return DependencyStatus(
            name=name,
            status=HealthStatus.HEALTHY,
            latency_seconds=(monotonic() - started_at),
        )

    async def check(self) -> HealthReport:
        dependencies = [
            await self._run_check(
                name="postgres",
                check=(self._postgres_check),
            ),
            await self._run_check(
                name="qdrant",
                check=(self._qdrant_check),
            ),
            await self._run_check(
                name="ollama",
                check=(self._model_check),
            ),
        ]

        failed_count = sum(
            dependency.status == HealthStatus.UNHEALTHY for dependency in dependencies
        )

        if failed_count == 0:
            overall_status = HealthStatus.HEALTHY

        elif failed_count == len(dependencies):
            overall_status = HealthStatus.UNHEALTHY

        else:
            overall_status = HealthStatus.DEGRADED

        return HealthReport(
            status=overall_status,
            dependencies=dependencies,
        )
