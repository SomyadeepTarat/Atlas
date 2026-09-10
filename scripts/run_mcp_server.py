from atlas.mcp.server.app import (
    mcp,
    register_capabilities,
)


def main() -> None:
    register_capabilities()

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001,
    )


if __name__ == "__main__":
    main()
