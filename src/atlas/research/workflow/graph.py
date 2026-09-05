from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from atlas.research.workflow.nodes import (
    ResearchWorkflowNodes,
)
from atlas.research.workflow.routing import (
    route_after_evidence,
    route_after_verification,
)
from atlas.research.workflow.state import (
    ResearchWorkflowState,
)


def build_research_graph(
    *,
    nodes: ResearchWorkflowNodes,
):
    builder = StateGraph(ResearchWorkflowState)

    builder.add_node(
        "plan",
        nodes.plan,
    )

    builder.add_node(
        "retrieve",
        nodes.retrieve,
    )

    builder.add_node(
        "assess_evidence",
        nodes.assess_evidence,
    )

    builder.add_node(
        "expand_retrieval",
        nodes.expand_retrieval,
    )

    builder.add_node(
        "synthesize",
        nodes.synthesize,
    )

    builder.add_node(
        "verify",
        nodes.verify,
    )

    builder.add_node(
        "repair",
        nodes.repair,
    )

    builder.add_edge(
        START,
        "plan",
    )

    builder.add_edge(
        "plan",
        "retrieve",
    )

    builder.add_edge(
        "retrieve",
        "assess_evidence",
    )

    builder.add_conditional_edges(
        "assess_evidence",
        route_after_evidence,
        {
            "synthesize": "synthesize",
            "advance_query": "expand_retrieval",
        },
    )

    builder.add_edge(
        "expand_retrieval",
        "retrieve",
    )

    builder.add_edge(
        "synthesize",
        "verify",
    )

    builder.add_conditional_edges(
        "verify",
        route_after_verification,
        {
            "finish": END,
            "repair": "repair",
        },
    )

    builder.add_edge(
        "repair",
        "verify",
    )

    checkpointer = MemorySaver()

    return builder.compile(
        checkpointer=checkpointer,
    )
