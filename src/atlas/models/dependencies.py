from functools import lru_cache

from atlas.core.config import get_settings
from atlas.models.ollama import OllamaModelClient
from atlas.models.service import ResearchModelService


@lru_cache
def get_research_model_service() -> ResearchModelService:
    settings = get_settings()

    client = OllamaModelClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )

    return ResearchModelService(client)