from mcp import Client


class MCPClientManager:
    def __init__(
        self,
        server_url: str,
    ) -> None:
        self._server_url = server_url

    def create_client(
        self,
    ) -> Client:
        return Client(self._server_url)

    async def read_resource(
        self,
        uri: str,
    ) -> list[str]:
        async with Client(self._server_url) as client:
            result = await client.read_resource(uri)

            texts: list[str] = []

            for item in result.contents:
                text = getattr(
                    item,
                    "text",
                    None,
                )

                if text is not None:
                    texts.append(text)

            return texts

    async def inspect_server(
        self,
    ) -> dict[str, object]:
        async with Client(self._server_url) as client:
            tools = await client.list_tools()

        return {
            "server": (client.server_info.name if client.server_info else None),
            "protocol_version": (client.protocol_version),
            "tool_names": [tool.name for tool in tools.tools],
        }
