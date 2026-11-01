"""Tests for the single-agent vs multi-agent comparison."""

from __future__ import annotations

import pytest

from multi_agent_orchestrator.comparison import (
    DEFAULT_SUITE,
    compare_goal,
    compare_suite,
)

_MULTI_GOAL = "research the topic and then draft an outline and then write the report"


def test_compare_goal_measures_the_tradeoff() -> None:
    comparison = compare_goal(_MULTI_GOAL)
    assert comparison.parts == 3
    # Single agent: one call, no review, so nothing is independently verified.
    assert comparison.single.worker_calls == 1
    assert comparison.single.reviewed_deliverables == 0
    assert comparison.single.verified_coverage == 0.0
    # Multi agent: one call per subtask, every one reviewed and approved.
    assert comparison.multi.worker_calls == comparison.parts
    assert comparison.multi.reviewed_deliverables == comparison.parts
    assert comparison.multi.verified_coverage == 1.0
    assert comparison.multi.completed


def test_raw_coverage_is_a_tie_on_decomposable_goals() -> None:
    comparison = compare_goal(_MULTI_GOAL)
    # A single pass that echoes the whole goal already mentions every part.
    assert comparison.single.raw_coverage == 1.0
    assert comparison.multi.raw_coverage == 1.0


def test_single_part_goal_is_equivalent_and_coordination_is_overhead() -> None:
    comparison = compare_goal("write the report")
    assert comparison.parts == 1
    assert comparison.single.worker_calls == comparison.multi.worker_calls == 1
    assert comparison.single.raw_coverage == comparison.multi.raw_coverage


def test_compare_suite_aggregates_cost_and_verification() -> None:
    summary = compare_suite(list(DEFAULT_SUITE))
    assert len(summary.rows) == len(DEFAULT_SUITE)
    # Coordination costs strictly more worker calls once any goal has multiple parts.
    assert summary.multi_worker_calls > summary.single_worker_calls
    assert summary.cost_ratio > 1.0
    # The baseline verifies nothing; the orchestrator verifies every delivered subtask.
    assert summary.single_verified == 0
    assert summary.multi_verified > 0
    # Raw coverage is a tie on these goals.
    assert summary.mean_single_raw_coverage == summary.mean_multi_raw_coverage == 1.0
    verdict = summary.verdict()
    assert "verification" in verdict
    assert "overhead" in verdict


def test_cli_measure_and_durable(capsys: pytest.CaptureFixture[str]) -> None:
    from multi_agent_orchestrator.cli import main

    assert main(["measure"]) == 0
    out = capsys.readouterr().out
    assert "verified" in out

    assert main(["durable"]) == 0
    out = capsys.readouterr().out
    assert "Resumed outputs identical to uninterrupted run: True" in out
