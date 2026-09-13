from atlas.telemetry.tracing import (
    get_langfuse,
    tracer,
)


def main() -> None:
    langfuse = get_langfuse()

    authenticated = langfuse.auth_check()

    print(
        "Langfuse authenticated:",
        authenticated,
    )

    with langfuse.start_as_current_observation(
        name="atlas-test",
        as_type="agent",
        input={"message": ("Atlas observability test")},
    ) as root:
        with tracer.start_as_current_span("test-child-span"):
            pass

        root.update(output={"success": True})

    langfuse.flush()

    print("Trace sent.")


if __name__ == "__main__":
    main()
