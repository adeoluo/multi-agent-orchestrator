"""A production-style stress benchmark for the orchestration service.

Drives the full run handler (plan, dispatch workers, critique) under sustained,
concurrent load over synthetic goals and reports throughput with p50, p95, and
p99 latency. Deterministic and offline; run with:

    uv run python benchmarks/stress.py
"""

from __future__ import annotations

import random
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

from multi_agent_orchestrator.service import OrchestrationService, handle

_VERBS = ["summarize", "format", "translate", "review", "expand", "shorten"]
_NOUNS = ["the report", "the output", "the draft", "the notes", "the summary"]


def _goal(rng: random.Random, clauses: int) -> str:
    parts = [f"{rng.choice(_VERBS)} {rng.choice(_NOUNS)}" for _ in range(clauses)]
    return " and then ".join(parts)


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(fraction * len(ordered)))]


def main() -> None:
    service = OrchestrationService.build()
    rng = random.Random(0)
    requests = [{"goal": _goal(rng, rng.randint(1, 4))} for _ in range(2000)]

    def one(body: dict[str, str]) -> float:
        start = time.perf_counter()
        handle("POST", "/run", body, service)
        return (time.perf_counter() - start) * 1000

    print(f"Requests: {len(requests)}")
    for workers in (1, 4, 8):
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=workers) as pool:
            latencies = list(pool.map(one, requests))
        wall = time.perf_counter() - start
        print(
            f"workers={workers:<2}  "
            f"throughput={len(requests) / wall:>7.0f} req/s  "
            f"p50={statistics.median(latencies):>6.3f} ms  "
            f"p95={_percentile(latencies, 0.95):>6.3f} ms  "
            f"p99={_percentile(latencies, 0.99):>6.3f} ms"
        )


if __name__ == "__main__":
    main()
