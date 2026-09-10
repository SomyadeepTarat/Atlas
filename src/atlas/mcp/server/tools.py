from atlas.mcp.server.app import mcp
from atlas.tools.builtin.calculator import (
    CalculatorTool,
)
from atlas.tools.dependencies import (
    get_tool_executor,
)
from atlas.tools.types import (
    ToolExecutionContext,
    ToolPermission,
)

calculator = CalculatorTool()


@mcp.tool(title="Calculate expression")
async def calculate(
    expression: str,
) -> dict[str, float]:
    """Safely evaluate a mathematical expression."""

    executor = get_tool_executor()

    result = await executor.execute(
        tool_name="calculate",
        raw_input={"expression": expression},
        context=ToolExecutionContext(permissions=frozenset({ToolPermission.CALCULATE})),
    )

    return result.output.model_dump()


@mcp.tool(title="Search indexed documents")
async def search_documents(
    query: str,
    document_ids: list[str] | None = None,
) -> dict:
    """
    Search indexed Atlas documents for
    passages relevant to a research query.
    """

    executor = get_tool_executor()

    result = await executor.execute(
        tool_name="search_documents",
        raw_input={
            "query": query,
            "document_ids": document_ids,
        },
        context=ToolExecutionContext(
            permissions=frozenset({ToolPermission.DOCUMENT_READ})
        ),
    )

    return result.output.model_dump()
