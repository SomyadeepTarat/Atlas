from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = "Atlas"
    app_environment: str = "development"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"
    ollama_timeout_seconds: float = 180.0

    model_max_attempts: int = 2
    model_retry_base_delay_seconds: float = 0.5
    model_retry_max_delay_seconds: float = 4.0
    model_retry_jitter_ratio: float = 0.2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "atlas_documents"

    embedding_model: str = "BAAI/bge-small-en-v1.5"

    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 200

    retrieval_top_k: int = 5

    sparse_embedding_model: str = "Qdrant/bm25"

    retrieval_candidate_k: int = 20
    rerank_top_k: int = 8
    context_top_k: int = 5

    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    max_context_chars: int = 7000
    minimum_rerank_score: float | None = None

    research_max_iterations: int = 3
    max_tool_calls: int = 5

    atlas_mcp_url: str = "http://localhost:8001/mcp"

    telemetry_enabled: bool = True

    telemetry_console_export: bool = False

    langfuse_enabled: bool = False

    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_base_url: str = "https://cloud.langfuse.com"

    telemetry_capture_content: bool = False
    langfuse_tracing_environment: str = "development"

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
