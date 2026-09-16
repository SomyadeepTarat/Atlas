from __future__ import annotations

from dataclasses import dataclass
from time import monotonic
from typing import Any
from uuid import UUID

from langfuse import propagate_attributes
from langgraph.errors import GraphRecursionError

from atlas.reliability.deadline import (
    workflow_deadline,
)
from atlas.research.errors import (
    WorkflowDeadlineExceededError,
)
from atlas.schemas.model import GroundedAnswer
from atlas.security.trust import ContentSource
from atlas.telemetry.logging import (
    bind_log_context,
    get_logger,
    reset_log_context,
)
from atlas.telemetry.tracing import (
    get_langfuse,
)

logger = get_logger(__name__)


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
        deadline_seconds: float = 300.0,
    ) -> None:
        self._graph = graph
        self._max_iterations = max_iterations
        self._deadline_seconds = deadline_seconds

    @property
    def graph(self) -> Any:
        return self._graph

    async def answer(
        self,
        question: str,
        *,
        thread_id: str,
    ) -> ResearchWorkflowResult:

        langfuse = get_langfuse()

        try:
            thread_uuid = UUID(thread_id)
        except ValueError as exc:
            raise ValueError(f"Invalid research thread ID: {thread_id}") from exc

        tokens = bind_log_context(thread_id=thread_id)

        started_at = monotonic()

        logger.info(
            "research.started",
            extra={
                "question_chars": len(question),
                "deadline_seconds": (self._deadline_seconds),
                "max_iterations": (self._max_iterations),
            },
        )

        initial_state = {
            "question": question,
            "iteration": 0,
            "max_iterations": (self._max_iterations),
            "repair_attempts": 0,
            "max_repair_attempts": 1,
        }

        try:
            with langfuse.start_as_current_observation(
                name="atlas-research",
                as_type="agent",
                input={
                    "question": question,
                },
            ) as root:
                with propagate_attributes(
                    trace_name=("atlas-research"),
                    session_id=thread_id,
                    tags=[
                        "atlas",
                        "research",
                    ],
                    metadata={
                        "thread_id": (thread_id),
                    },
                ):
                    try:
                        async with workflow_deadline(self._deadline_seconds):
                            state = await self._graph.ainvoke(
                                initial_state,
                                config={
                                    "configurable": {"thread_id": (thread_id)},
                                    "recursion_limit": 30,
                                },
                            )

                    except GraphRecursionError as exc:
                        logger.error(
                            ("research.graph_recursion_limit"),
                            extra={
                                "recursion_limit": 30,
                            },
                        )

                        raise (
                            WorkflowDeadlineExceededError(
                                "Research workflow exceeded its graph execution budget."
                            )
                        ) from exc

                    result = ResearchWorkflowResult(
                        answer=state["answer"],
                        iterations=(
                            state.get(
                                "iteration",
                                0,
                            )
                            + 1
                        ),
                        verification_passed=(
                            state.get(
                                ("verification_passed"),
                                False,
                            )
                        ),
                        verification_reason=(state.get("verification_reason")),
                    )

                    root.update(
                        output={
                            "answer": (result.answer.model_dump()),
                            "iterations": (result.iterations),
                            "verification_passed": (result.verification_passed),
                            "verification_reason": (result.verification_reason),
                        }
                    )

                    duration_seconds = monotonic() - started_at

                    logger.info(
                        "research.completed",
                        extra={
                            "duration_seconds": (duration_seconds),
                            "iterations": (result.iterations),
                            "verification_passed": (result.verification_passed),
                        },
                    )

                    return result

        except WorkflowDeadlineExceededError:
            logger.exception(
                ("research.deadline_exceeded"),
                extra={
                    "duration_seconds": (monotonic() - started_at),
                    "deadline_seconds": (self._deadline_seconds),
                },
            )

            raise

        except Exception:
            logger.exception(
                "research.failed",
                extra={
                    "duration_seconds": (monotonic() - started_at),
                },
            )

            raise

        finally:
            reset_log_context(tokens)

        await self._memory_service.consider_message(
            user_message=question,
            thread_id=thread_uuid,
            source=ContentSource.USER,
        )
