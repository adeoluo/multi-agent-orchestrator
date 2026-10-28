"""A micro-benchmark for orchestration throughput.

Measures how many orchestrated runs per second the system completes (planner, workers,
critic over a blackboard), and the consensus throughput, so the README can quote numbers.
Run with:

    uv run python benchmarks/benchmark.py
"""

from __future__ import annotations

import time

from multi_agent_orchestrator.agents import EchoWorker, KeywordPlanner, LengthCritic
from multi_agent_orchestrator.consensus import ConsensusOrchestrator
from multi_agent_orchestrator.core.types import Subtask, WorkerResult
from multi_agent_orchestrator.orchestrator import Orchestrator

_GOAL = "research the topic and then draft an outline and then write the report"


def _bench_orchestration(num_runs: int) -> float:
    orchestrator = Orchestrator(KeywordPlanner(chain_dependencies=True), [EchoWorker()], LengthCritic())
    start = time.perf_counter()
    for _ in range(num_runs):
        orchestrator.run(_GOAL)
    elapsed = time.perf_counter() - start
    return num_runs / elapsed if elapsed > 0 else float("inf")


class _FixedWorker:
    def __init__(self, answer: str, name: str) -> None:
        self._answer = answer
        self.name = name

    def execute(self, subtask: Subtask, context: object) -> WorkerResult:  # type: ignore[override]
        return WorkerResult(subtask_id=subtask.id, worker=self.name, output=self._answer)


def _bench_consensus(num_runs: int) -> float:
    orchestrator = ConsensusOrchestrator(
        [_FixedWorker("yes", "w1"), _FixedWorker("yes", "w2"), _FixedWorker("no", "w3")]
    )
    subtask = Subtask("s", "decide")
    start = time.perf_counter()
    for _ in range(num_runs):
        orchestrator.run(subtask)
    elapsed = time.perf_counter() - start
    return num_runs / elapsed if elapsed > 0 else float("inf")


def main() -> None:
    runs_per_sec = _bench_orchestration(20_000)
    consensus_per_sec = _bench_consensus(50_000)
    print("Multi-Agent Orchestrator micro-benchmark\n")
    print(f"  orchestrated 3-subtask runs : {runs_per_sec:>12,.0f} runs/sec")
    print(f"  3-worker consensus decisions : {consensus_per_sec:>12,.0f} runs/sec")


if __name__ == "__main__":
    main()
