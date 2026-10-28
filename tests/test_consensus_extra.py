"""Tests for consensus coordination, tool workers, and extra planners."""

from __future__ import annotations

import pytest

from multi_agent_orchestrator.agents_extra import (
    ExplicitPlanner,
    TemplatePlanner,
    ToolWorker,
)
from multi_agent_orchestrator.consensus import (
    ConsensusOrchestrator,
    majority_vote,
    unanimous,
)
from multi_agent_orchestrator.core.types import Subtask, WorkerResult


# --------------------------------------------------------------------------- #
# Aggregators
# --------------------------------------------------------------------------- #
def test_majority_vote() -> None:
    assert majority_vote(["a", "b", "a"]) == "a"


def test_majority_vote_empty() -> None:
    assert majority_vote([]) is None


def test_unanimous_agrees() -> None:
    assert unanimous(["a", "a", "a"]) == "a"


def test_unanimous_disagrees() -> None:
    assert unanimous(["a", "a", "b"]) is None


# --------------------------------------------------------------------------- #
# Consensus orchestrator
# --------------------------------------------------------------------------- #
class _FixedWorker:
    def __init__(self, answer: str, name: str) -> None:
        self._answer = answer
        self.name = name

    def execute(self, subtask: Subtask, context: object) -> WorkerResult:  # type: ignore[override]
        return WorkerResult(subtask_id=subtask.id, worker=self.name, output=self._answer)


def test_consensus_majority() -> None:
    workers = [_FixedWorker("yes", "w1"), _FixedWorker("yes", "w2"), _FixedWorker("no", "w3")]
    orchestrator = ConsensusOrchestrator(workers)
    result = orchestrator.run(Subtask("s", "decide"))
    assert result.answer == "yes"
    assert result.num_votes == 3
    assert not result.agreed


def test_consensus_unanimous_agreed() -> None:
    workers = [_FixedWorker("yes", "w1"), _FixedWorker("yes", "w2")]
    orchestrator = ConsensusOrchestrator(workers, aggregator=unanimous)
    result = orchestrator.run(Subtask("s", "decide"))
    assert result.answer == "yes"
    assert result.agreed


def test_consensus_requires_two_workers() -> None:
    with pytest.raises(ValueError, match="at least two"):
        ConsensusOrchestrator([_FixedWorker("x", "w1")])


# --------------------------------------------------------------------------- #
# Tool worker
# --------------------------------------------------------------------------- #
def test_tool_worker_invokes_tool() -> None:
    worker = ToolWorker(tools={"shout": str.upper})
    subtask = Subtask("s", "do it", metadata={"tool": "shout", "arg": "hello"})
    result = worker.execute(subtask, {})
    assert result.output == "HELLO"
    assert result.success


def test_tool_worker_unknown_tool() -> None:
    worker = ToolWorker(tools={})
    result = worker.execute(Subtask("s", "x", metadata={"tool": "missing"}), {})
    assert not result.success
    assert "unknown tool" in result.output


# --------------------------------------------------------------------------- #
# Planners
# --------------------------------------------------------------------------- #
def test_explicit_planner() -> None:
    plan = [Subtask("a", "first"), Subtask("b", "second")]
    assert ExplicitPlanner(plan).plan("ignored goal") == plan


def test_template_planner_chains_roles() -> None:
    subtasks = TemplatePlanner().plan("write a report")
    assert [s.metadata["role"] for s in subtasks] == ["research", "draft", "review"]
    assert subtasks[1].depends_on == ("task-0",)


def test_template_planner_custom_roles() -> None:
    subtasks = TemplatePlanner(roles=("plan", "execute")).plan("goal")
    assert len(subtasks) == 2
