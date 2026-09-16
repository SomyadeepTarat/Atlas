from dataclasses import dataclass


@dataclass(frozen=True)
class MCPServerSecurityPolicy:
    server_name: str

    allowed_tools: frozenset[str]

    allow_resources: bool = False


ATLAS_LOCAL_MCP_POLICY = MCPServerSecurityPolicy(
    server_name="atlas-local",
    allowed_tools=frozenset(
        {
            "calculate",
            "search_documents",
        }
    ),
    allow_resources=True,
)
