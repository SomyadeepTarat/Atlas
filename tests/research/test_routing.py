from atlas.research.workflow.routing import (
    route_after_evidence,
)


def test_sufficient_evidence_routes_to_synthesis():
    result = route_after_evidence(
        {
            "evidence_sufficient": True,
            "iteration": 0,
            "max_iterations": 3,
        }
    )

    assert result == "synthesize"


def test_insufficient_evidence_retries():
    result = route_after_evidence(
        {
            "evidence_sufficient": False,
            "iteration": 0,
            "max_iterations": 3,
        }
    )

    assert result == "advance_query"


def test_iteration_limit_stops_search():
    result = route_after_evidence(
        {
            "evidence_sufficient": False,
            "iteration": 2,
            "max_iterations": 3,
        }
    )

    assert result == "synthesize"
