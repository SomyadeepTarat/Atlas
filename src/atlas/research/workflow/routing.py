from atlas.research.workflow.state import (
    ResearchWorkflowState,
)


def route_after_evidence(
    state: ResearchWorkflowState,
) -> str:
    evidence_sufficient = state.get(
        "evidence_sufficient",
        False,
    )

    if evidence_sufficient:
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
) -> str:
    verification_passed = state.get(
        "verification_passed",
        False,
    )

    if verification_passed:
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
