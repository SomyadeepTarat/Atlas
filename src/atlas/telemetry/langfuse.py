from contextlib import (
    nullcontext,
)

from langfuse import get_client

from atlas.core.config import (
    get_settings,
)


def generation_observation(
    *,
    name: str,
    model: str,
):
    settings = get_settings()

    if not settings.langfuse_enabled:
        return nullcontext()

    client = get_client()

    return client.start_as_current_observation(
        as_type="generation",
        name=name,
        model=model,
    )


async def generate_with_observation(self, output_schema):
    with generation_observation(
        name="ollama-structured-generation",
        model="ollama",
    ) as observation:
        result = await self._generate(...)

        if observation is not None:
            observation.update(
                output={
                    "schema": output_schema.__name__,
                }
            )

        return result
