from atlas.models.service import (
    ResearchModelService,
)
from atlas.research.workflow.state import (
    ResearchWorkflowState,
)
from atlas.retrieval.context import (
    build_context,
)
from atlas.retrieval.service import (
    RetrievalService,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)
from atlas.telemetry.logging import (
    get_logger,
)
from atlas.telemetry.tracing import (
    tracer,
)
from atlas.tools.executor import ToolExecutor
from atlas.tools.registry import ToolRegistry

logger = get_logger(__name__)


class ResearchWorkflowNodes:
    def __init__(
        self,
        *,
        retrieval: RetrievalService,
        model: ResearchModelService,
        tool_registry: ToolRegistry,
        tool_executor: ToolExecutor,
    ) -> None:
        self._retrieval = retrieval
        self._model = model
        self._tool_registry = tool_registry
        self._tool_executor = tool_executor

    async def plan(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        with tracer.start_as_current_span("research-plan") as span:
            question = state.get("question") or ""
            if question is None:
                raise ValueError("Research workflow state is missing a question")

            result = await self._model.create_research_plan(question)

            queries = list(result.output.queries)

            span.set_attribute(
                "atlas.plan.query_count",
                len(queries),
            )

            logger.info(
                "research.plan.completed",
                extra={"query_count": (len(queries))},
            )

            return {
                "plan": result.output,
                "queries": queries,
            }

    async def retrieve(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        with tracer.start_as_current_span("retrieval") as span:
            question = state.get(
                "question",
                "",
            )

            queries = state.get(
                "queries",
                [question],
            )

            existing_chunks = state.get(
                "retrieved_chunks",
                [],
            )

            new_chunks: list[RetrievedChunk] = []

            for query in queries:
                new_chunks.extend(self._retrieval.retrieve_context(query))

            merged = self._merge_chunks(existing_chunks + new_chunks)

            span.set_attribute(
                "atlas.retrieval.query_count",
                len(queries),
            )

            span.set_attribute(
                "atlas.retrieval.chunk_count",
                len(merged),
            )

            logger.info(
                "research.retrieval.completed",
                extra={
                    "query_count": (len(queries)),
                    "chunk_count": (len(merged)),
                },
            )

            return {"retrieved_chunks": (merged)}

    async def assess_evidence(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        with tracer.start_as_current_span("evidence-assessment") as span:
            question = state.get("question")
            if question is None:
                raise ValueError("Research workflow state is missing a question")

            chunks = state.get(
                "retrieved_chunks",
                [],
            )

            if not chunks:
                span.set_attribute(
                    "atlas.evidence.status",
                    "insufficient",
                )

                logger.info(
                    ("research.evidence.insufficient"),
                    extra={"reason": ("no_chunks")},
                )

                return {
                    "context_chunks": [],
                    "context": "",
                    ("evidence_sufficient"): False,
                }

            context = build_context(chunks)

            result = await self._model.assess_evidence(
                question=question,
                context=context,
            )

            assessment = result.output

            status = "sufficient" if assessment.sufficient else "insufficient"

            span.set_attribute(
                "atlas.evidence.status",
                status,
            )

            span.set_attribute(
                ("atlas.evidence.chunk_count"),
                len(chunks),
            )

            logger.info(
                "research.evidence.assessed",
                extra={
                    "status": status,
                    "chunk_count": (len(chunks)),
                },
            )

            return {
                "context_chunks": (chunks),
                "context": context,
                ("evidence_assessment"): assessment,
                ("evidence_sufficient"): (assessment.sufficient),
            }

    async def expand_retrieval(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        question = state.get("question")
        if question is None:
            raise ValueError("Research workflow state is missing a question")

        result = await self._model.create_research_plan(question)

        iteration = state.get(
            "iteration",
            0,
        )

        logger.info(
            "research.retrieval.expanded",
            extra={
                "next_iteration": (iteration + 1),
                "query_count": (len(result.output.queries)),
            },
        )

        return {
            "plan": result.output,
            "queries": list(result.output.queries),
            "iteration": (iteration + 1),
        }

    async def synthesize(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        with tracer.start_as_current_span("synthesis") as span:
            question = state.get("question") or ""

            context = state.get(
                "context",
                "",
            )

            span.set_attribute(
                "atlas.context.chars",
                len(context),
            )

            result = await self._model.answer_from_context(
                question=question,
                context=context,
            )

            span.set_attribute(
                ("atlas.answer.insufficient_context"),
                (result.output.insufficient_context),
            )

            logger.info(
                "research.synthesis.completed",
                extra={("insufficient_context"): (result.output.insufficient_context)},
            )

            return {"answer": (result.output)}

    async def verify(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        with tracer.start_as_current_span("verification") as span:
            question = state.get("question", "")

            context = state.get(
                "context",
                "",
            )

            answer = state.get("answer")
            if answer is None:
                raise ValueError("Research workflow state is missing an answer")

            result = await self._model.verify_answer(
                question=question,
                context=context,
                answer=answer,
            )

            verification = result.output

            passed = verification.supported

            span.set_attribute(
                "atlas.verification.status",
                ("passed" if passed else "failed"),
            )

            logger.info(
                ("research.verification.completed"),
                extra={
                    "passed": passed,
                    "reason": (verification.reason),
                },
            )

            return {
                "verification": (verification),
                ("verification_passed"): passed,
                ("verification_reason"): (verification.reason),
            }

    async def repair(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        with tracer.start_as_current_span("repair"):
            answer = state.get("answer")
            if answer is None or isinstance(
                answer,
                str,
            ):
                raise ValueError("Research workflow state is missing a grounded answer")

            verification = state.get(
                "verification",
            )
            if verification is None:
                raise ValueError("Research workflow state is missing verification")

            result = await self._model.repair_answer(
                question=state.get(
                    "question",
                    "",
                ),
                context=(
                    state.get(
                        "context",
                        "",
                    )
                ),
                answer=answer,
                verification=verification,
            )

            attempts = state.get(
                "repair_attempts",
                0,
            )

            return {
                "answer": result.output,
                "repair_attempts": (attempts + 1),
            }

    @staticmethod
    def _merge_chunks(
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        seen: set[str] = set()

        result: list[RetrievedChunk] = []

        for chunk in chunks:
            if chunk.chunk_id in seen:
                continue

            seen.add(chunk.chunk_id)

            result.append(chunk)

        return result
