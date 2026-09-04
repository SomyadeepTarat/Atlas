from pydantic.dataclasses import dataclass


def abstention_correct(
    *,
    expected_abstain: bool,
    actual_abstain: bool,
) -> bool:
    return expected_abstain == actual_abstain


@dataclass(frozen=True)
class GenerationCaseResult:
    case_id: str

    abstention_correct: bool
    citation_valid: bool

    model_input_tokens: int
    model_output_tokens: int
    model_latency_seconds: float

    answer: str
