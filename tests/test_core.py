"""Tests for core types and the blackboard."""

from __future__ import annotations

import pytest

from multi_agent_orchestrator.core import (
    Blackboard,
    Message,
    Review,
    Role,
    Subtask,
    WorkerResult,
)


# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #
def test_subtask_validates() -> None:
    with pytest.raises(ValueError, match="id"):
        Subtask(id="", description="x")
    with pytest.raises(ValueError, match="description"):
        Subtask(id="s1", description="")


# --------------------------------------------------------------------------- #
# Blackboard basics
# --------------------------------------------------------------------------- #
def test_blackboard_requires_goal() -> None:
    with pytest.raises(ValueError, match="goal"):
        Blackboard("")


def test_post_and_read_messages() -> None:
    board = Blackboard("goal")
    board.post(Message(role=Role.PLANNER, content="planned"))
    board.post(Message(role=Role.WORKER, content="worked"))
    assert [m.content for m in board.messages] == ["planned", "worked"]


def test_set_plan_rejects_duplicates() -> None:
    board = Blackboard("goal")
    with pytest.raises(ValueError, match="duplicate"):
        board.set_plan([Subtask("s1", "a"), Subtask("s1", "b")])


def test_record_result_and_review() -> None:
    board = Blackboard("goal")
    board.set_plan([Subtask("s1", "do a thing")])
    board.record_result(WorkerResult(subtask_id="s1", worker="w", output="done"))
    assert board.result("s1") is not None
    assert not board.is_complete("s1")  # no approving review yet
    board.record_review(Review(subtask_id="s1", approved=True))
    assert board.is_complete("s1")


# --------------------------------------------------------------------------- #
# Dependency scheduling
# --------------------------------------------------------------------------- #
def test_ready_subtasks_respects_dependencies() -> None:
    board = Blackboard("goal")
    board.set_plan(
        [
            Subtask("s1", "first"),
            Subtask("s2", "second", depends_on=("s1",)),
        ]
    )
    # Only s1 is ready initially.
    ready_ids = {s.id for s in board.ready_subtasks()}
    assert ready_ids == {"s1"}

    # Completing s1 unlocks s2.
    board.record_result(WorkerResult(subtask_id="s1", worker="w", output="x"))
    board.record_review(Review(subtask_id="s1", approved=True))
    assert {s.id for s in board.ready_subtasks()} == {"s2"}


def test_rejected_review_keeps_subtask_pending() -> None:
    board = Blackboard("goal")
    board.set_plan([Subtask("s1", "a")])
    board.record_result(WorkerResult(subtask_id="s1", worker="w", output="x"))
    board.record_review(Review(subtask_id="s1", approved=False, feedback="redo"))
    assert not board.is_complete("s1")
    assert {s.id for s in board.ready_subtasks()} == {"s1"}


def test_all_complete() -> None:
    board = Blackboard("goal")
    board.set_plan([Subtask("s1", "a"), Subtask("s2", "b")])
    assert not board.all_complete()
    for sid in ("s1", "s2"):
        board.record_result(WorkerResult(subtask_id=sid, worker="w", output="x"))
        board.record_review(Review(subtask_id=sid, approved=True))
    assert board.all_complete()


def test_all_complete_empty_plan_is_false() -> None:
    assert not Blackboard("goal").all_complete()
