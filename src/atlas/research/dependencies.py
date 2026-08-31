from functools import lru_cache

from atlas.models.dependencies import (
    get_research_model_service,
)
from atlas.research.service import (
    ResearchService,
)
from atlas.retrieval.dependencies import (
    get_retrieval_service,
)


@lru_cache
def get_research_service() -> ResearchService:
    return ResearchService(
        retrieval=get_retrieval_service(),
        model=(get_research_model_service()),
    )
