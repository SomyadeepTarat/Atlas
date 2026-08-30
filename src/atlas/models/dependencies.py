from functools import lru_cache

from atlas.core.config import get_settings
from atlas.models.base import ModelClient
from atlas.models.fallback import FallbackModelClient
from atlas.models.ollama import OllamaModelClient
from atlas.models.retry import RetryModelClient
from atlas.models.service import ResearchModelService


@lru_cache
def get_model_client() -> ModelClient:
    settings = get_settings()

    ollama = OllamaModelClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=(settings.ollama_timeout_seconds),
    )

    retrying_ollama = RetryModelClient(
        ollama,
        max_attempts=settings.model_max_attempts,
        base_delay_seconds=(settings.model_retry_base_delay_seconds),
        max_delay_seconds=(settings.model_retry_max_delay_seconds),
        jitter_ratio=(settings.model_retry_jitter_ratio),
    )

    return FallbackModelClient(
        clients=[
            retrying_ollama,
        ]
    )


@lru_cache
def get_research_model_service() -> ResearchModelService:
    return ResearchModelService(get_model_client())
