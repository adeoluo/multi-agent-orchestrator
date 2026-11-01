"""Tests for durable orchestration: checkpointing and crash recovery."""

from __future__ import annotations

from pathlib import Path

import pytest

from multi_agent_orchestrator.agents import EchoWorker, KeywordPlanner, LengthCritic
from multi_agent_orchestrator.core.blackboard import Blackboard
from multi_agent_orchestrator.durable import (
    CrashError,
    inspect_checkpoint,
    load_checkpoint,
    resume_durable,
    run_durable,
    save_checkpoint,
)
from multi_agent_orchestrator.orchestrator import Orchestrator

_GOAL = "research the topic and then draft an outline and then write the report"


def _orchestrator() -> Orchestrator:
    return Orchestrator(KeywordPlanner(chain_dependencies=True), [EchoWorker()], LengthCritic())


def test_blackboard_snapshot_round_trip() -> None:
    board = _orchestrator().run(_GOAL).blackboard
    restored = Blackboard.restore(board.snapshot())
    assert restored.snapshot() == board.snapshot()
    assert restored.all_complete() == board.all_complete()
    assert [s.id for s in restored.subtasks] == [s.id for s in board.subtasks]
    assert restored.results.keys() == board.results.keys()
    assert [m.content for m in restored.messages] == [m.content for m in board.messages]


def test_run_durable_completes_and_checkpoints(tmp_path: Path) -> None:
    checkpoint = tmp_path / "run.checkpoint"
    result = run_durable(_orchestrator(), _GOAL, checkpoint)
    assert result.completed
    status = inspect_checkpoint(checkpoint)
    assert status.complete
    assert status.completed == result.num_subtasks


def test_interrupted_run_resumes_identically(tmp_path: Path) -> None:
    baseline = run_durable(_orchestrator(), _GOAL, tmp_path / "baseline.checkpoint")

    crashed = tmp_path / "crashed.checkpoint"
    with pytest.raises(CrashError):
        run_durable(_orchestrator(), _GOAL, crashed, crash_after=1)

    status = inspect_checkpoint(crashed)
    assert status.interrupted
    assert status.completed == 1
    assert "interrupted" in status.format()

    resumed = resume_durable(_orchestrator(), crashed)
    assert resumed.completed
    # The resumed run reaches a state identical to the uninterrupted one, byte for byte.
    assert resumed.blackboard.snapshot() == baseline.blackboard.snapshot()


def test_resume_at_every_crash_point_is_identical(tmp_path: Path) -> None:
    baseline = run_durable(_orchestrator(), _GOAL, tmp_path / "baseline.checkpoint")
    total = baseline.num_subtasks
    for crash_after in range(1, total + 1):
        checkpoint = tmp_path / f"crash-{crash_after}.checkpoint"
        with pytest.raises(CrashError):
            run_durable(_orchestrator(), _GOAL, checkpoint, crash_after=crash_after)
        resumed = resume_durable(_orchestrator(), checkpoint)
        assert resumed.completed
        assert resumed.blackboard.snapshot() == baseline.blackboard.snapshot()


def test_resumed_outputs_match_a_plain_run(tmp_path: Path) -> None:
    plain = _orchestrator().run(_GOAL)
    checkpoint = tmp_path / "run.checkpoint"
    with pytest.raises(CrashError):
        run_durable(_orchestrator(), _GOAL, checkpoint, crash_after=2)
    resumed = resume_durable(_orchestrator(), checkpoint)
    assert resumed.final_outputs() == plain.final_outputs()
    assert resumed.completed == plain.completed


def test_save_and_load_checkpoint_helpers(tmp_path: Path) -> None:
    board = _orchestrator().run("do a and then do b").blackboard
    checkpoint = tmp_path / "manual.checkpoint"
    save_checkpoint(checkpoint, board)
    reloaded = load_checkpoint(checkpoint)
    assert reloaded.goal == board.goal
    assert reloaded.all_complete()
