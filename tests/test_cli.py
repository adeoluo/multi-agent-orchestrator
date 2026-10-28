"""Tests for the single-agent baseline and the CLI."""

from __future__ import annotations

import pytest

from multi_agent_orchestrator.agents import EchoWorker
from multi_agent_orchestrator.baseline import SingleAgent, compare_structure
from multi_agent_orchestrator.cli import main


# --------------------------------------------------------------------------- #
# Baseline
# --------------------------------------------------------------------------- #
def test_single_agent_one_pass() -> None:
    result = SingleAgent(EchoWorker()).run("do everything in one go")
    assert result.subtasks == 1
    assert "do everything" in result.output
    assert not result.reviewed


def test_compare_structure_text() -> None:
    text = compare_structure(1, 4)
    assert "single-agent: 1" in text
    assert "multi-agent: 4" in text


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def test_cli_run(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["run", "research the topic and write the summary"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "planner" in output
    assert "Completed: True" in output


def test_cli_run_default_goal(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["run"])
    assert exit_code == 0
    assert "Completed" in capsys.readouterr().out


def test_cli_compare(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["compare", "do a and do b"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "Single-agent output" in output
    assert "Multi-agent outputs" in output
    assert "undifferentiated pass" in output


def test_cli_requires_command() -> None:
    with pytest.raises(SystemExit):
        main([])
