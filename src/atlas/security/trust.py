from enum import StrEnum


class TrustLevel(StrEnum):
    TRUSTED = "trusted"
    INTERNAL = "internal"
    UNTRUSTED = "untrusted"


class ContentSource(StrEnum):
    USER = "user"
    DOCUMENT = "document"
    WEB = "web"
    MCP = "mcp"
    TOOL = "tool"
    MEMORY = "memory"
    SYSTEM = "system"
