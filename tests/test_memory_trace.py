"""Tests for shared memory, run serialization, and the CLI additions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from multi_agent_orchestrator.agents import EchoWorker, KeywordPlanner, LengthCritic
from multi_agent_orchestrator.cli import main
from multi_agent_orchestrator.memory import SharedMemory
from multi_agent_orchestrator.orchestrator import Orchestrator
from multi_agent_orchestrator.trace import run_to_dict, run_to_json


# --------------------------------------------------------------------------- #
# Shared memory
# --------------------------------------------------------------------------- #
def test_memory_set_and_get() -> None:
    memory = SharedMemory()
    memory.set("count", 3)
    assert memory.get("count") == 3
    assert memory.get("missing", default=0) == 0


def test_memory_namespacing() -> None:
    memory = SharedMemory()
    memory.set("x", 1, namespace="worker-a")
    memory.set("x", 2, namespace="worker-b")
    assert memory.get("x", namespace="worker-a") == 1
    assert memory.get("x", namespace="worker-b") == 2


def test_memory_has() -> None:
    memory = SharedMemory()
    memory.set("k", "v")
    assert memory.has("k")
    assert not memory.has("other")


def test_memory_append() -> None:
    memory = SharedMemory()
    memory.append("items", "a")
    memory.append("items", "b")
    assert memory.get("items") == ["a", "b"]


def test_memory_append_type_error() -> None:
    memory = SharedMemory()
    memory.set("k", "not a list")
    with pytest.raises(TypeError, match="not a list"):
        memory.append("k", "x")


def test_memory_keys_namespaced() -> None:
    memory = SharedMemory()
    memory.set("a", 1, namespace="ns")
    memory.set("b", 2, namespace="ns")
    memory.set("global", 3)
    assert set(memory.keys(namespace="ns")) == {"a", "b"}
    assert set(memory.keys()) == {"global"}


# --------------------------------------------------------------------------- #
# Run serialization
# --------------------------------------------------------------------------- #
def _result() -> object:
    orchestrator = Orchestrator(KeywordPlanner(), [EchoWorker()], LengthCritic())
    return orchestrator.run("research the topic and write the summary")


def test_run_to_dict_structure() -> None:
    payload = run_to_dict(_result())  # type: ignore[arg-type]
    assert payload["completed"] is True
    assert len(payload["subtasks"]) == 2
    assert payload["messages"]
    assert all("role" in m for m in payload["messages"])


def test_run_to_json_round_trips_through_json() -> None:
    text = run_to_json(_result())  # type: ignore[arg-type]
    parsed = json.loads(text)
    assert parsed["goal"]


# --------------------------------------------------------------------------- #
# CLI additions
# --------------------------------------------------------------------------- #
def test_cli_run_with_metrics(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["run", "do a and do b", "--metrics"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "completed" in output.lower()


def test_cli_run_writes_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "run.json"
    exit_code = main(["run", "do a and do b", "--json", str(out)])
    assert exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["completed"] is True
