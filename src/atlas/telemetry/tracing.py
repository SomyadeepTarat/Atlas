from functools import lru_cache

from langfuse import Langfuse
from opentelemetry import trace

from atlas.core.config import get_settings

tracer = trace.get_tracer("atlas")


@lru_cache
def get_langfuse() -> Langfuse:
    settings = get_settings()

    if not settings.langfuse_enabled:
        return Langfuse(tracing_enabled=False)

    if not settings.langfuse_public_key:
        raise RuntimeError("LANGFUSE_PUBLIC_KEY is required when Langfuse is enabled.")

    if not settings.langfuse_secret_key:
        raise RuntimeError("LANGFUSE_SECRET_KEY is required when Langfuse is enabled.")

    return Langfuse(
        public_key=(settings.langfuse_public_key),
        secret_key=(settings.langfuse_secret_key),
        base_url=(settings.langfuse_base_url),
        environment=(settings.langfuse_tracing_environment),
        # Export our own OpenTelemetry spans too:
        #
        # research-plan
        # retrieval
        # dense-embedding
        # qdrant-search
        # reranker
        # verification
        # etc.
        should_export_span=lambda span: True,
    )


def flush_tracing() -> None:
    get_langfuse().flush()


def shutdown_tracing() -> None:
    get_langfuse().shutdown()
