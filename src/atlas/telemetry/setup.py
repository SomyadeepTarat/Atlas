from opentelemetry import trace
from opentelemetry.sdk.resources import (
    Resource,
)
from opentelemetry.sdk.trace import (
    TracerProvider,
)
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)

from atlas.core.config import (
    Settings,
)

_configured = False


def configure_telemetry(
    settings: Settings,
) -> None:
    global _configured

    if _configured:
        return

    if not settings.telemetry_enabled:
        _configured = True
        return

    resource = Resource.create(
        {
            "service.name": "atlas-api",
            "service.version": "0.1.0",
            "deployment.environment": (settings.app_environment),
        }
    )

    provider = TracerProvider(resource=resource)

    if settings.telemetry_console_export:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    _configured = True
