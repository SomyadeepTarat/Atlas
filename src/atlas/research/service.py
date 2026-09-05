from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from atlas.schemas.model import GroundedAnswer


@dataclass(frozen=True)
class ResearchWorkflowResult:
    answer: GroundedAnswer
    iterations: int
    verification_passed: bool
    verification_reason: str | None


class ResearchService:
    def __init__(
        self,
        graph: Any,
        *,
        max_iterations: int,
    ) -> None:
        self._graph = graph
        self._max_iterations = max_iterations

    async def answer(
        self,
        question: str,
        *,
        thread_id: str,
    ) -> ResearchWorkflowResult:
        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        state = await self._graph.ainvoke(
            {
                "question": question,
                "iteration": 0,
                "max_iterations": self._max_iterations,
                "repair_attempts": 0,
                "max_repair_attempts": 1,
            },
            config=config,
        )

        return ResearchWorkflowResult(
            answer=state["answer"],
            iterations=state.get(
                "iteration",
                0,
            )
            + 1,
            verification_passed=state.get(
                "verification_passed",
                False,
            ),
            verification_reason=state.get("verification_reason"),
        )
