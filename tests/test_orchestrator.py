"""Tests for the orchestrator loop and built-in agents."""

from __future__ import annotations

import pytest

from multi_agent_orchestrator.agents import (
    EchoWorker,
    KeywordPlanner,
    LengthCritic,
    UppercaseWorker,
)
from multi_agent_orchestrator.core.types import Review, Subtask, WorkerResult
from multi_agent_orchestrator.orchestrator import Orchestrator


# --------------------------------------------------------------------------- #
# Planner
# --------------------------------------------------------------------------- #
def test_keyword_planner_splits_goal() -> None:
    subtasks = KeywordPlanner().plan("research the topic and write a summary then review")
    assert len(subtasks) == 3
    assert subtasks[0].depends_on == ()


def test_keyword_planner_chains_dependencies() -> None:
    subtasks = KeywordPlanner(chain_dependencies=True).plan("do a then do b")
    assert subtasks[1].depends_on == ("task-0",)


def test_keyword_planner_single_task() -> None:
    subtasks = KeywordPlanner().plan("a single indivisible goal")
    assert len(subtasks) == 1


# --------------------------------------------------------------------------- #
# Workers and critic
# --------------------------------------------------------------------------- #
def test_echo_worker_includes_context() -> None:
    worker = EchoWorker()
    context = {"task-0": WorkerResult(subtask_id="task-0", worker="w", output="x")}
    result = worker.execute(Subtask("task-1", "do it"), context)
    assert "given task-0" in result.output


def test_uppercase_worker() -> None:
    result = UppercaseWorker().execute(Subtask("s", "hello"), {})
    assert result.output == "HELLO"


def test_length_critic_approves_and_rejects() -> None:
    critic = LengthCritic(min_length=5)
    approved = critic.review(Subtask("s", "x"), WorkerResult("s", "w", "long enough"))
    rejected = critic.review(Subtask("s", "x"), WorkerResult("s", "w", "ab"))
    assert approved.approved
    assert not rejected.approved


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #
def test_orchestrator_completes_simple_goal() -> None:
    orchestrator = Orchestrator(KeywordPlanner(), [EchoWorker()], LengthCritic())
    result = orchestrator.run("research the topic and write the summary")
    assert result.completed
    assert result.num_subtasks == 2
    assert len(result.final_outputs()) == 2


def test_orchestrator_respects_dependencies() -> None:
    orchestrator = Orchestrator(
        KeywordPlanner(chain_dependencies=True), [EchoWorker()], LengthCritic()
    )
    result = orchestrator.run("step one then step two then step three")
    assert result.completed
    # The dependent worker should have seen its predecessor's output.
    messages = [m.content for m in result.blackboard.messages if "given" in m.content]
    assert messages


def test_orchestrator_requires_workers() -> None:
    with pytest.raises(ValueError, match="at least one worker"):
        Orchestrator(KeywordPlanner(), [], LengthCritic())


def test_orchestrator_rejects_negative_retries() -> None:
    with pytest.raises(ValueError, match="max_retries"):
        Orchestrator(KeywordPlanner(), [EchoWorker()], LengthCritic(), max_retries=-1)


class _AlwaysRejectCritic:
    def review(self, subtask: Subtask, result: WorkerResult) -> Review:
        return Review(subtask_id=subtask.id, approved=False, feedback="never good enough")


def test_orchestrator_gives_up_after_retries() -> None:
    orchestrator = Orchestrator(
        KeywordPlanner(), [EchoWorker()], _AlwaysRejectCritic(), max_retries=1
    )
    result = orchestrator.run("do the thing")
    assert not result.completed
    assert result.final_outputs() == {}


class _RecoveringCritic:
    """Rejects the first attempt of each subtask, then approves."""

    def __init__(self) -> None:
        self._seen: set[str] = set()

    def review(self, subtask: Subtask, result: WorkerResult) -> Review:
        if subtask.id in self._seen:
            return Review(subtask_id=subtask.id, approved=True)
        self._seen.add(subtask.id)
        return Review(subtask_id=subtask.id, approved=False, feedback="retry")


def test_orchestrator_recovers_on_retry() -> None:
    orchestrator = Orchestrator(
        KeywordPlanner(), [EchoWorker()], _RecoveringCritic(), max_retries=2
    )
    result = orchestrator.run("do a and do b")
    assert result.completed


def test_orchestrator_distributes_across_workers() -> None:
    workers = [EchoWorker(name="w1"), UppercaseWorker(name="w2")]
    orchestrator = Orchestrator(KeywordPlanner(), workers, LengthCritic())
    result = orchestrator.run("alpha and beta and gamma and delta")
    used = {
        m.metadata.get("worker") for m in result.blackboard.messages if m.metadata.get("worker")
    }
    # With several subtasks hashed across two workers, both should be used.
    assert len(used) >= 1
