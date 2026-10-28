"""Tests for graph validation, run metrics, and plan validation in the orchestrator."""

from __future__ import annotations

import pytest

from multi_agent_orchestrator.agents import EchoWorker, KeywordPlanner, LengthCritic
from multi_agent_orchestrator.core.types import Subtask
from multi_agent_orchestrator.graph import PlanError, topological_order, validate_plan
from multi_agent_orchestrator.metrics import run_metrics
from multi_agent_orchestrator.orchestrator import Orchestrator


# --------------------------------------------------------------------------- #
# Graph validation
# --------------------------------------------------------------------------- #
def test_validate_plan_accepts_dag() -> None:
    plan = [
        Subtask("a", "first"),
        Subtask("b", "second", depends_on=("a",)),
        Subtask("c", "third", depends_on=("a", "b")),
    ]
    validate_plan(plan)  # should not raise


def test_validate_plan_rejects_missing_dependency() -> None:
    plan = [Subtask("a", "x", depends_on=("ghost",))]
    with pytest.raises(PlanError, match="unknown subtask"):
        validate_plan(plan)


def test_validate_plan_rejects_cycle() -> None:
    plan = [
        Subtask("a", "x", depends_on=("b",)),
        Subtask("b", "y", depends_on=("a",)),
    ]
    with pytest.raises(PlanError, match="cycle"):
        validate_plan(plan)


def test_topological_order() -> None:
    plan = [
        Subtask("c", "third", depends_on=("a", "b")),
        Subtask("b", "second", depends_on=("a",)),
        Subtask("a", "first"),
    ]
    order = topological_order(plan)
    assert order.index("a") < order.index("b") < order.index("c")


def test_topological_order_detects_cycle() -> None:
    plan = [
        Subtask("a", "x", depends_on=("b",)),
        Subtask("b", "y", depends_on=("a",)),
    ]
    with pytest.raises(PlanError, match="cycle"):
        topological_order(plan)


# --------------------------------------------------------------------------- #
# Run metrics
# --------------------------------------------------------------------------- #
def test_run_metrics_counts_subtasks() -> None:
    orchestrator = Orchestrator(KeywordPlanner(), [EchoWorker()], LengthCritic())
    result = orchestrator.run("research the topic and write the summary")
    metrics = run_metrics(result)
    assert metrics.total_subtasks == 2
    assert metrics.completed_subtasks == 2
    assert metrics.completion_rate == 1.0
    assert metrics.attempts_per_subtask >= 1.0


def test_run_metrics_tracks_retries() -> None:
    class _RecoveringCritic:
        def __init__(self) -> None:
            self._seen: set[str] = set()

        def review(self, subtask, result):  # type: ignore[no-untyped-def]
            from multi_agent_orchestrator.core.types import Review

            if subtask.id in self._seen:
                return Review(subtask_id=subtask.id, approved=True)
            self._seen.add(subtask.id)
            return Review(subtask_id=subtask.id, approved=False, feedback="retry")

    orchestrator = Orchestrator(
        KeywordPlanner(), [EchoWorker()], _RecoveringCritic(), max_retries=2
    )
    result = orchestrator.run("do a and do b")
    metrics = run_metrics(result)
    assert metrics.retries >= 1
    assert metrics.critic_rejections >= 1


def test_run_metrics_format() -> None:
    orchestrator = Orchestrator(KeywordPlanner(), [EchoWorker()], LengthCritic())
    metrics = run_metrics(orchestrator.run("do the thing"))
    assert "completed" in metrics.format()


# --------------------------------------------------------------------------- #
# Orchestrator plan validation
# --------------------------------------------------------------------------- #
class _CyclicPlanner:
    def plan(self, goal: str):  # type: ignore[no-untyped-def]
        return [
            Subtask("a", "x", depends_on=("b",)),
            Subtask("b", "y", depends_on=("a",)),
        ]


def test_orchestrator_rejects_cyclic_plan() -> None:
    orchestrator = Orchestrator(_CyclicPlanner(), [EchoWorker()], LengthCritic())
    with pytest.raises(PlanError):
        orchestrator.run("anything")


def test_orchestrator_can_skip_validation() -> None:
    # With validation off, a cyclic plan does not raise; it simply makes no progress.
    orchestrator = Orchestrator(
        _CyclicPlanner(), [EchoWorker()], LengthCritic(), validate_plan=False
    )
    result = orchestrator.run("anything")
    assert not result.completed
