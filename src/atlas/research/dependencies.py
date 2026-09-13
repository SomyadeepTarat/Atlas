from fastapi import Request

from atlas.core.config import get_settings
from atlas.models.dependencies import (
    get_research_model_service,
)
from atlas.research.service import ResearchService
from atlas.research.workflow.graph import (
    build_research_graph,
)
from atlas.research.workflow.nodes import (
    ResearchWorkflowNodes,
)
from atlas.retrieval.dependencies import (
    get_retrieval_service,
)
from atlas.tools.dependencies import (
    get_tool_executor,
    get_tool_registry,
)


def get_research_service(
    request: Request,
) -> ResearchService:
    settings = get_settings()

    nodes = ResearchWorkflowNodes(
        retrieval=get_retrieval_service(),
        model=get_research_model_service(),
        tool_registry=get_tool_registry(),
        tool_executor=get_tool_executor(),
    )

    checkpointer = request.app.state.langgraph_checkpointer

    graph = build_research_graph(
        nodes=nodes,
        checkpointer=checkpointer,
    )

    return ResearchService(
        graph=graph,
        max_iterations=(settings.research_max_iterations),
    )
