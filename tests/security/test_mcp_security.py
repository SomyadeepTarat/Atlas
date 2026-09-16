import pytest
from mcp import Client

from atlas.mcp.server.app import (
    mcp,
    register_capabilities,
)
from atlas.security.policy import MCPServerSecurityPolicy

register_capabilities()


@pytest.mark.anyio
async def test_high_risk_write_not_exposed_over_mcp():
    async with Client(mcp) as client:
        result = await client.list_tools()

        names = {tool.name for tool in result.tools}

        assert "mock_external_write" not in names


def test_unknown_mcp_tool_not_allowed():
    policy = MCPServerSecurityPolicy(
        server_name="external",
        allowed_tools=frozenset({"search"}),
    )

    assert "delete_files" not in policy.allowed_tools
