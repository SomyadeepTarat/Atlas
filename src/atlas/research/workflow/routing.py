from typing import Literal

from atlas.research.workflow.state import ResearchWorkflowState


def route_after_evidence(
    state: ResearchWorkflowState,
) -> Literal[
    "synthesize",
    "advance_query",
]:
    if state.get(
        "evidence_sufficient",
        False,
    ):
        return "synthesize"

    iteration = state.get(
        "iteration",
        0,
    )

    max_iterations = state.get(
        "max_iterations",
        1,
    )

    if iteration + 1 < max_iterations:
        return "advance_query"

    return "synthesize"


def route_after_verification(
    state: ResearchWorkflowState,
) -> Literal[
    "finish",
    "repair",
]:
    if state.get(
        "verification_passed",
        False,
    ):
        return "finish"

    repair_attempts = state.get(
        "repair_attempts",
        0,
    )

    max_repair_attempts = state.get(
        "max_repair_attempts",
        1,
    )

    if repair_attempts < max_repair_attempts:
        return "repair"

    return "finish"


def route_after_tool_decision(
    state: ResearchWorkflowState,
) -> Literal[
    "execute_tool",
    "plan",
]:
    if state.get("tool_required") and state.get("tool_name") == "calculate":
        return "execute_tool"

    return "plan"
