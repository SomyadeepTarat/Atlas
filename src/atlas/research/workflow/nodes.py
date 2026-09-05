from __future__ import annotations
from unittest import result

from mypy.state import state

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


class ResearchWorkflowNodes:
    def __init__(
        self,
        *,
        retrieval: RetrievalService,
        model: ResearchModelService,
    ) -> None:
        self._retrieval = retrieval
        self._model = model

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
