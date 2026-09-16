import pytest

from atlas.research.streaming import (
    ResearchStreamAdapter,
)
from atlas.schemas.model import (
    GroundedAnswer,
)


class FakeGraph:
    async def astream(
        self,
        *_args,
        **_kwargs,
    ):
        yield {
            "type": "updates",
            "ns": (),
            "data": {"plan": {"research_queries": ["query one"]}},
        }

        yield {
            "type": "updates",
            "ns": (),
            "data": {
                "synthesize": {
                    "answer": GroundedAnswer(
                        answer="Test answer.",
                        used_chunk_ids=["chunk-1"],
                        confidence=0.9,
                        insufficient_context=False,
                    )
                }
            },
        }

        yield {
            "type": "updates",
            "ns": (),
            "data": {
                "verify": {
                    "verification_passed": True,
                    "verification_reason": "Supported.",
                }
            },
        }


@pytest.mark.asyncio
async def test_stream_ends_with_complete_event():
    adapter = ResearchStreamAdapter(
        FakeGraph(),
        max_iterations=3,
    )

    events = [
        event
        async for event in adapter.stream(
            question="Test question",
            thread_id="thread-1",
        )
    ]

    assert events[-1].type.value == ("complete")

    assert events[-1].data["verification_passed"] is True
