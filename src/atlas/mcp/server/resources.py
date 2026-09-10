from atlas.mcp.server.app import mcp


@mcp.resource(
    "atlas://about",
    title="About Atlas",
    description=("Information about the Atlas research system."),
    mime_type="text/plain",
)
def atlas_about() -> str:
    return (
        "Atlas is an evidence-driven "
        "research agent with hybrid retrieval, "
        "reranking, evaluation, and "
        "policy-controlled tools."
    )
