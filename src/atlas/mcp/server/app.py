from mcp.server import MCPServer

mcp = MCPServer(
    "atlas-research",
    instructions=("Provides research-related tools and resources for Atlas."),
)


def register_capabilities() -> None:
    from atlas.mcp.server import (
        resources,
        tools,
    )

    _ = resources
    _ = tools
