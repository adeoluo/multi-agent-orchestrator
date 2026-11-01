"""Single-agent baseline vs multi-agent orchestrator over multi-step workloads.

Runs the same suite of goals through a single undifferentiated agent and the planner/
workers/critic orchestrator, and reports the honest trade-off: worker-call cost, raw content
coverage (typically a tie on decomposable goals), and verified coverage (independently
reviewed sub-deliverables, where the orchestrator's critic is the differentiator).

Deterministic and offline. Run with:

    uv run python benchmarks/compare.py
"""

from __future__ import annotations

from multi_agent_orchestrator.comparison import DEFAULT_SUITE, compare_suite


def main() -> None:
    summary = compare_suite(list(DEFAULT_SUITE))
    print("Single-agent baseline vs multi-agent orchestrator\n")
    header = (
        f"{'parts':>5}  {'single calls':>12}  {'multi calls':>11}  "
        f"{'raw S/M':>9}  {'verified S/M':>12}  {'multi done':>10}"
    )
    print(header)
    print("-" * len(header))
    for row in summary.rows:
        print(
            f"{row.parts:>5}  {row.single.worker_calls:>12}  {row.multi.worker_calls:>11}  "
            f"{row.single.raw_coverage:>4.2f}/{row.multi.raw_coverage:<4.2f}  "
            f"{row.single.verified_coverage:>5.2f}/{row.multi.verified_coverage:<5.2f}  "
            f"{row.multi.completed!s:>10}"
        )
    print()
    print(
        f"totals: worker calls single={summary.single_worker_calls} "
        f"multi={summary.multi_worker_calls} ({summary.cost_ratio:.1f}x); "
        f"verified sub-deliverables single={summary.single_verified} "
        f"multi={summary.multi_verified}"
    )
    print()
    print(summary.verdict())


if __name__ == "__main__":
    main()
