from dataclasses import dataclass
from typing import Any

from atlas.mcp.client.manager import MCPClientManager
from atlas.tools.types import ToolPermission


@dataclass(frozen=True)
class MCPToolSpecification:
    name: str
    description: str | None
    input_schema: dict[str, Any]


class MCPToolAdapter:
    MAX_MCP_TOOL_DESCRIPTION_CHARS = 2_000
    MAX_MCP_TOOL_NAME_CHARS = 128

    def __init__(
        self,
        client_manager: MCPClientManager,
    ) -> None:
        self._client_manager = client_manager

    async def list_tools(
        self,
    ) -> list[MCPToolSpecification]:
        async with self._client_manager.create_client() as client:
            result = await client.list_tools()

            return [
                MCPToolSpecification(
                    name=sanitize_tool_name(tool.name),
                    description=sanitize_tool_description(tool.description),
                    input_schema=tool.input_schema,
                )
                for tool in result.tools
            ]


def sanitize_tool_name(
    name: str,
) -> str:
    if not name:
        raise ValueError("MCP tool name is empty.")

    if len(name) > MCPToolAdapter.MAX_MCP_TOOL_NAME_CHARS:
        raise ValueError("MCP tool name is too long.")

    return name


def sanitize_tool_description(
    description: str | None,
) -> str:
    if description is None:
        return ""

    return description[: MCPToolAdapter.MAX_MCP_TOOL_DESCRIPTION_CHARS]


async def call_tool(
    self,
    *,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    async with self._client_manager.create_client() as client:
        result = await client.call_tool(
            tool_name,
            arguments,
        )

        if result.is_error:
            raise RuntimeError(f"MCP tool '{tool_name}' failed.")

        if result.structured_content is None:
            return {}

        return dict(result.structured_content)


@dataclass(frozen=True)
class MCPServerConfig:
    name: str
    url: str

    allowed_tools: frozenset[str]

    required_permission: ToolPermission
