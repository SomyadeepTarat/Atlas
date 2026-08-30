from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class ModelUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True)
class ModelTimings:
    total_seconds: float
    load_seconds: float | None = None
    prompt_eval_seconds: float | None = None
    generation_seconds: float | None = None


@dataclass(frozen=True)
class ModelMetadata:
    provider: str
    model: str
    attempts: int
    usage: ModelUsage
    timings: ModelTimings


@dataclass(frozen=True)
class ModelResult[T: BaseModel]:
    output: T
    metadata: ModelMetadata
