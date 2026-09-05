from atlas.tools.base import Tool
from atlas.tools.errors import (
    ToolNotFoundError,
)


class ToolRegistry:
    def __init__(
        self,
        tools: list[Tool],
    ) -> None:
        self._tools = {tool.name: tool for tool in tools}

        if len(self._tools) != len(tools):
            raise ValueError("Tool names must be unique.")

    def get(
        self,
        name: str,
    ) -> Tool:
        try:
            return self._tools[name]

        except KeyError as exc:
            raise ToolNotFoundError(f"Unknown tool: {name}") from exc

    def list_tools(
        self,
    ) -> list[Tool]:
        return list(self._tools.values())

    def specifications(
        self,
    ) -> list[dict]:
        return [tool.specification() for tool in self.list_tools()]
