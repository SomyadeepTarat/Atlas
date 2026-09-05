from __future__ import annotations

from atlas.models.service import ResearchModelService
from atlas.research.workflow.state import (
    ResearchWorkflowState,
)
from atlas.retrieval.context import (
    build_context,
    select_context_chunks,
)
from atlas.retrieval.deduplication import (
    deduplicate_adjacent_chunks,
)
from atlas.retrieval.service import (
    RetrievalService,
)
from atlas.retrieval.types import (
    RetrievedChunk,
)
from atlas.tools.executor import (
    ToolExecutor,
)
from atlas.tools.registry import (
    ToolRegistry,
)
from atlas.tools.types import ToolExecutionContext, ToolPermission


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
        question = state.get("question", "")

        result = await self._model.create_research_plan(question)

        queries = [query for query in result.output.queries]

        return {
            "plan": result.output,
            "queries": queries,
        }

    async def retrieve(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        question = state.get("question", "")

        queries = state.get(
            "queries",
            [question],
        )

        existing_chunks: list[RetrievedChunk] = state.get(
            "retrieved_chunks",
            [],
        )

        new_chunks: list[RetrievedChunk] = []

        for query in queries:
            chunks = self._retrieval.search_candidates(query)

            new_chunks.extend(chunks)

        merged = self._merge_chunks(existing_chunks + new_chunks)

        return {
            "retrieved_chunks": merged,
        }

    async def assess_evidence(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        question = state.get("question", "")

        retrieved_chunks: list[RetrievedChunk] = state.get(
            "retrieved_chunks",
            [],
        )

        if not retrieved_chunks:
            return {
                "context_chunks": [],
                "context": "",
                "verification_reason": ("No evidence was retrieved."),
            }

        deduplicated = deduplicate_adjacent_chunks(retrieved_chunks)

        context_chunks = select_context_chunks(
            deduplicated,
            max_chunks=8,
            max_chars=12000,
        )

        context = build_context(context_chunks)

        result = await self._model.assess_evidence(
            question=question,
            context=context,
        )

        return {
            "context_chunks": context_chunks,
            "context": context,
            "evidence_assessment": result.output,
        }

    async def synthesize(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        question = state.get("question", "")

        context = state.get(
            "context",
            "",
        )

        result = await self._model.answer_from_context(
            question=question,
            context=context,
        )

        return {
            "answer": result.output,
        }

    async def verify(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        question = state.get("question", "")
        context = state.get("context", "")
        answer = state.get("answer")
        if answer is None:
            raise ValueError(
                "Cannot repair answer: no answer exists in workflow state."
            )

        result = await self._model.verify_answer(
            question=question,
            context=context,
            answer=answer,
        )

        verification = result.output

        return {
            "verification": verification,
            "verification_passed": verification.supported,
            "verification_reason": verification.reason,
        }

    async def repair(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        question = state.get("question", "")

        context = state.get(
            "context",
            "",
        )

        answer = state.get("answer")
        if answer is None:
            raise ValueError(
                "Cannot repair answer: no answer exists in workflow state."
            )

        verification = state.get("verification")
        if verification is None:
            raise ValueError(
                "Cannot repair answer: no verification exists in workflow state."
            )

        result = await self._model.repair_answer(
            question=question,
            context=context,
            answer=answer,
            verification=verification,
        )

        repair_attempts = state.get(
            "repair_attempts",
            0,
        )

        return {
            "answer": result.output,
            "repair_attempts": (repair_attempts + 1),
        }

    async def expand_retrieval(
        self,
        state: ResearchWorkflowState,
    ) -> ResearchWorkflowState:
        question = state.get("question", "")

        iteration = state.get(
            "iteration",
            0,
        )

        result = await self._model.create_research_plan(question)

        return {
            "plan": result.output,
            "queries": list(result.output.queries),
            "iteration": iteration + 1,
        }

    async def decide_tool(
        self,
        state: ResearchWorkflowState,
    ) -> dict:
        result = await self._model.choose_tool(
            question=state.get("question", ""),
            tool_specs=self._tool_registry.specifications(),
        )

        decision = result.output

        return {
            "tool_required": decision.use_tool,
            "tool_name": decision.tool_name,
            "tool_arguments": decision.arguments,
        }

    async def execute_tool(
        self,
        state: ResearchWorkflowState,
    ) -> dict:
        tool_name = state.get("tool_name")

        if not tool_name:
            return {"tool_output": None}

        result = await self._tool_executor.execute(
            tool_name=tool_name,
            raw_input=state.get("tool_arguments", {}),
            context=ToolExecutionContext(
                permissions=frozenset(
                    {
                        ToolPermission.CALCULATE,
                        ToolPermission.DOCUMENT_READ,
                    }
                )
            ),
        )

        return {"tool_output": result.output.model_dump()}

    @staticmethod
    def _merge_chunks(
        chunks: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        seen: set[str] = set()
        merged: list[RetrievedChunk] = []

        for chunk in chunks:
            if chunk.chunk_id in seen:
                continue

            seen.add(chunk.chunk_id)
            merged.append(chunk)

        return merged
