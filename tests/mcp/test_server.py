import pytest
from mcp import Client
from mcp.types import (
    TextResourceContents,
)

from atlas.mcp.server.app import (
    mcp,
    register_capabilities,
)

register_capabilities()


@pytest.mark.anyio
async def test_calculate_tool():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "calculate",
            {"expression": "6 * 7"},
        )

        assert result.is_error is False

        assert result.structured_content == {"result": 42.0}


@pytest.mark.anyio
async def test_about_resource():
    async with Client(mcp) as client:
        result = await client.read_resource("atlas://about")

        text_items = [
            item
            for item in result.contents
            if isinstance(
                item,
                TextResourceContents,
            )
        ]

        assert text_items
        assert "Atlas" in text_items[0].text


@pytest.mark.anyio
async def test_high_risk_tool_not_exposed():
    async with Client(mcp) as client:
        tools = await client.list_tools()

        names = {tool.name for tool in tools.tools}

        assert "mock_external_write" not in names
