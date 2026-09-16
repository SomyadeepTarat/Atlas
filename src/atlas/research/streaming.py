from collections.abc import AsyncIterator
from typing import Any

from atlas.research.workflow.types import (
    ResearchWorkflowResult,
)
from atlas.schemas.model import (
    GroundedAnswer,
)
from atlas.schemas.streaming import (
    ResearchEventType,
    ResearchStage,
    ResearchStreamEvent,
)

_NODE_STATUS: dict[
    str,
    tuple[ResearchStage, str],
] = {
    "plan": (
        ResearchStage.PLANNING,
        "Created a research plan.",
    ),
    "retrieve": (
        ResearchStage.RETRIEVING,
        "Retrieved relevant evidence.",
    ),
    "assess_evidence": (
        ResearchStage.ASSESSING,
        "Evaluated evidence coverage.",
    ),
    "advance_query": (
        ResearchStage.RETRIEVING,
        "Refining the evidence search.",
    ),
    "synthesize": (
        ResearchStage.SYNTHESIZING,
        "Synthesized the research answer.",
    ),
    "verify": (
        ResearchStage.VERIFYING,
        "Verified claims against evidence.",
    ),
    "repair": (
        ResearchStage.REPAIRING,
        "Revising unsupported claims.",
    ),
}


class ResearchStreamAdapter:
    def __init__(
        self,
        graph: Any,
        *,
        max_iterations: int,
    ) -> None:
        self._graph = graph

        self._max_iterations = max_iterations

    async def stream(
        self,
        *,
        question: str,
        thread_id: str,
    ) -> AsyncIterator[ResearchStreamEvent]:
        sequence = 0

        yield ResearchStreamEvent(
            type=ResearchEventType.STARTED,
            stage=ResearchStage.STARTING,
            message="Research started.",
            sequence=sequence,
        )

        sequence += 1

        latest_answer: GroundedAnswer | None = None

        latest_iteration = 0

        verification_passed = False

        verification_reason: str | None = None

        config = {
            "configurable": {
                "thread_id": thread_id,
            },
            "recursion_limit": 30,
        }

        initial_state = {
            "question": question,
            "iteration": 0,
            "max_iterations": (self._max_iterations),
            "repair_attempts": 0,
            "max_repair_attempts": 1,
        }

        async for part in self._graph.astream(
            initial_state,
            config=config,
            stream_mode="updates",
            version="v2",
        ):
            if part["type"] != "updates":
                continue

            updates = part["data"]

            for node_name, update in updates.items():
                if not isinstance(
                    update,
                    dict,
                ):
                    continue

                status = _NODE_STATUS.get(node_name)

                if status is not None:
                    stage, message = status

                    event_data: dict[
                        str,
                        Any,
                    ] = {}

                    if node_name == "retrieve":
                        chunks = update.get(
                            "retrieved_chunks",
                            [],
                        )

                        event_data["chunk_count"] = len(chunks)

                    if node_name == "plan":
                        queries = update.get(
                            "research_queries",
                            [],
                        )

                        event_data["query_count"] = len(queries)

                    yield ResearchStreamEvent(
                        type=(ResearchEventType.STATUS),
                        stage=stage,
                        message=message,
                        sequence=sequence,
                        data=event_data,
                    )

                    sequence += 1

                iteration = update.get("iteration")

                if isinstance(
                    iteration,
                    int,
                ):
                    latest_iteration = iteration

                answer = update.get("answer")

                if isinstance(
                    answer,
                    GroundedAnswer,
                ):
                    latest_answer = answer

                verification = update.get("verification_passed")

                if isinstance(
                    verification,
                    bool,
                ):
                    verification_passed = verification

                reason = update.get("verification_reason")

                if isinstance(
                    reason,
                    str,
                ):
                    verification_reason = reason

        if latest_answer is None:
            raise RuntimeError("Research workflow finished without an answer.")

        result = ResearchWorkflowResult(
            answer=latest_answer,
            iterations=(latest_iteration + 1),
            verification_passed=(verification_passed),
            verification_reason=(verification_reason),
        )

        yield ResearchStreamEvent(
            type=ResearchEventType.COMPLETE,
            stage=ResearchStage.COMPLETE,
            message="Research complete.",
            sequence=sequence,
            data={
                "answer": (result.answer.model_dump(mode="json")),
                "iterations": (result.iterations),
                "verification_passed": (result.verification_passed),
                "verification_reason": (result.verification_reason),
            },
        )
