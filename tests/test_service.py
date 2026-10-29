"""Tests for the dependency-free HTTP orchestration service (pure handler layer)."""

from __future__ import annotations

from multi_agent_orchestrator.service import OrchestrationService, handle

_SERVICE = OrchestrationService.build()


def test_health() -> None:
    status, payload = handle("GET", "/health", {}, _SERVICE)
    assert status == 200
    assert payload["status"] == "ok"
    assert "echo-worker" in payload["workers"]
    assert payload["planner"] == "keyword-planner"


def test_run_orchestrates() -> None:
    status, payload = handle(
        "POST", "/run", {"goal": "summarize the report and then format the output"}, _SERVICE
    )
    assert status == 200
    assert payload["completed"] is True
    assert payload["subtasks"]
    assert payload["messages"]


def test_compare_multi_beats_single_on_structure() -> None:
    status, payload = handle("POST", "/compare", {"goal": "summarize and format"}, _SERVICE)
    assert status == 200
    assert payload["single_agent"]["subtasks"] == 1
    assert payload["multi_agent"]["subtasks"] >= 2


def test_run_rejects_missing_goal() -> None:
    status, payload = handle("POST", "/run", {}, _SERVICE)
    assert status == 400
    assert "goal" in payload["error"]


def test_run_rejects_overlong_goal() -> None:
    status, _ = handle("POST", "/run", {"goal": "a" * 5000}, _SERVICE)
    assert status == 400


def test_unknown_route() -> None:
    status, payload = handle("GET", "/nope", {}, _SERVICE)
    assert status == 404
    assert "error" in payload
