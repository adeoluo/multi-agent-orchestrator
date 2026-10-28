"""Command-line interface for the multi-agent orchestrator.

Subcommands:

- ``run`` - orchestrate planner, workers, and critic over a goal and print the blackboard
  log and final outputs.
- ``compare`` - run the same goal through the single-agent baseline and the multi-agent
  orchestrator and contrast their structure, making the value of coordination concrete.

The CLI wires the agents and the orchestrator together; it holds no coordination logic.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from multi_agent_orchestrator import __version__
from multi_agent_orchestrator.agents import (
    EchoWorker,
    KeywordPlanner,
    LengthCritic,
    UppercaseWorker,
)
from multi_agent_orchestrator.baseline import SingleAgent, compare_structure
from multi_agent_orchestrator.orchestrator import Orchestrator

_DEFAULT_GOAL = "research the subject and then draft an outline and then write the report"


def _orchestrator() -> Orchestrator:
    return Orchestrator(
        KeywordPlanner(chain_dependencies=True),
        [EchoWorker(), UppercaseWorker()],
        LengthCritic(),
    )


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(
        prog="multi-agent-orchestrator",
        description="A planner/workers/critic multi-agent orchestrator built from scratch.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Orchestrate agents over a goal.")
    run_parser.add_argument("goal", nargs="?", default=_DEFAULT_GOAL, help="The goal.")
    run_parser.set_defaults(handler=_handle_run)

    compare_parser = subparsers.add_parser(
        "compare", help="Contrast single-agent and multi-agent on a goal."
    )
    compare_parser.add_argument("goal", nargs="?", default=_DEFAULT_GOAL, help="The goal.")
    compare_parser.set_defaults(handler=_handle_compare)
    return parser


def _handle_run(args: argparse.Namespace) -> int:
    result = _orchestrator().run(args.goal)
    print(f"Goal: {args.goal}")
    print(f"Completed: {result.completed} ({result.num_subtasks} subtasks)\n")
    for message in result.blackboard.messages:
        print(f"  [{message.role}] {message.content}")
    return 0 if result.completed else 1


def _handle_compare(args: argparse.Namespace) -> int:
    single = SingleAgent(EchoWorker()).run(args.goal)
    multi = _orchestrator().run(args.goal)
    print(f"Goal: {args.goal}\n")
    print("Single-agent output:")
    print(f"  {single.output}\n")
    print("Multi-agent outputs:")
    for subtask_id, output in multi.final_outputs().items():
        print(f"  [{subtask_id}] {output}")
    print()
    print(compare_structure(single.subtasks, multi.num_subtasks))
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point; returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = args.handler
    exit_code: int = handler(args)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
