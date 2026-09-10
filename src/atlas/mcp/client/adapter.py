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
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.input_schema,
                )
                for tool in result.tools
            ]

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
