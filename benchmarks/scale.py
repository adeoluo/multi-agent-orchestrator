"""A large-workload scale benchmark for the orchestration loop.

Where ``benchmark.py`` times fixed 3-subtask runs, this script asks how the
orchestrator scales as the *plan* grows: it orchestrates goals that decompose into
progressively longer dependency chains (25 -> 200 subtasks) with the planner,
worker, and critic over a blackboard, reporting per-goal latency, subtask
throughput, peak memory (via the stdlib ``tracemalloc``), and the critic-approved
completion rate.

The interesting signal is super-linear: the scheduler rescans the blackboard for
ready subtasks on every iteration, so subtask throughput falls as the chain grows
even though every subtask still completes. That is the honest cost of a simple,
auditable from-scratch control loop.

The data is synthetic and the loop is pure Python with offline deterministic
agents: these numbers measure coordination overhead, not real agent latency, and
are not a comparison against a hosted multi-agent framework. The point is to show
how this implementation scales, honestly.

Run with:

    uv run python benchmarks/scale.py
"""

from __future__ import annotations

import time
import tracemalloc
from dataclasses import dataclass

from multi_agent_orchestrator.agents import EchoWorker, KeywordPlanner, LengthCritic
from multi_agent_orchestrator.metrics import run_metrics
from multi_agent_orchestrator.orchestrator import Orchestrator

_SUBTASK_COUNTS: tuple[int, ...] = (25, 50, 100, 200)
_TARGET_SUBTASKS = 12_000


def build_goal(num_subtasks: int) -> str:
    """Build a goal that the keyword planner splits into ``num_subtasks`` chained steps."""
    return " and then ".join(f"handle step number {i} carefully" for i in range(num_subtasks))


def _new_orchestrator() -> Orchestrator:
    return Orchestrator(KeywordPlanner(chain_dependencies=True), [EchoWorker()], LengthCritic())


@dataclass(frozen=True, slots=True)
class ScaleResult:
    """One row of the scale table."""

    subtasks: int
    seconds_per_goal: float
    subtasks_per_sec: float
    peak_mib: float
    completion_rate: float


def measure(num_subtasks: int) -> ScaleResult:
    """Orchestrate a ``num_subtasks``-long plan and report latency, throughput, memory.

    Throughput is measured over a batch sized so each point does roughly equal total
    work; peak memory is captured in a separate ``tracemalloc`` pass over one goal.
    """
    goal = build_goal(num_subtasks)
    orchestrator = _new_orchestrator()
    metrics = run_metrics(orchestrator.run(goal))
    repeats = max(1, _TARGET_SUBTASKS // metrics.total_subtasks)

    start = time.perf_counter()
    for _ in range(repeats):
        orchestrator.run(goal)
    elapsed = time.perf_counter() - start

    total_subtasks = repeats * metrics.total_subtasks
    peak = _peak_memory(goal)

    return ScaleResult(
        subtasks=metrics.total_subtasks,
        seconds_per_goal=elapsed / repeats,
        subtasks_per_sec=total_subtasks / elapsed if elapsed else 0.0,
        peak_mib=peak / (1024 * 1024),
        completion_rate=metrics.completion_rate,
    )


def _peak_memory(goal: str) -> int:
    """Return the peak bytes to orchestrate one goal and retain its blackboard."""
    tracemalloc.start()
    _new_orchestrator().run(goal)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def main() -> None:
    print("Synthetic goals; from-scratch pure-Python orchestration with offline agents.")
    print("Measures coordination overhead, not real agent latency or a hosted framework.\n")
    header = f"{'subtasks':>9}{'sec/goal':>11}{'subtasks/sec':>14}{'peak MiB':>11}{'completed':>11}"
    print(header)
    print("-" * len(header))
    for num_subtasks in _SUBTASK_COUNTS:
        result = measure(num_subtasks)
        print(
            f"{result.subtasks:>9}{result.seconds_per_goal:>11.4f}{result.subtasks_per_sec:>14.0f}"
            f"{result.peak_mib:>11.2f}{result.completion_rate:>11.2f}"
        )


if __name__ == "__main__":
    main()
