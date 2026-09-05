from functools import lru_cache

from atlas.retrieval.dependencies import (
    get_retrieval_service,
)
from atlas.tools.builtin.calculator import (
    CalculatorTool,
)
from atlas.tools.builtin.document_search import (
    DocumentSearchTool,
)
from atlas.tools.builtin.mock_write import (
    MockWriteTool,
)
from atlas.tools.executor import (
    ToolExecutor,
)
from atlas.tools.policy import (
    ToolPolicyEngine,
)
from atlas.tools.registry import (
    ToolRegistry,
)


@lru_cache
def get_tool_registry() -> ToolRegistry:
    return ToolRegistry(
        tools=[
            CalculatorTool(),
            DocumentSearchTool(get_retrieval_service()),
            MockWriteTool(),
        ]
    )


@lru_cache
def get_tool_executor() -> ToolExecutor:
    return ToolExecutor(
        registry=get_tool_registry(),
        policy_engine=ToolPolicyEngine(),
    )
