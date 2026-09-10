from functools import lru_cache

from atlas.core.config import get_settings
from atlas.mcp.client.adapter import MCPServerConfig
from atlas.tools.types import ToolPermission


@lru_cache
def get_mcp_server_configs() -> tuple[MCPServerConfig, ...]:
    settings = get_settings()

    return (
        MCPServerConfig(
            name="research-tools",
            url=settings.atlas_mcp_url,
            allowed_tools=frozenset(
                {
                    "calculate",
                    "search_documents",
                }
            ),
            required_permission=(ToolPermission.DOCUMENT_READ),
        ),
    )
