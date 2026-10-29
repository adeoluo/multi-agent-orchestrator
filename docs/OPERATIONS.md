# Operations Guide - Multi-Agent Orchestrator

The operational contract of the orchestration service.

## Running the service

```bash
uv run python -m multi_agent_orchestrator serve --host 0.0.0.0 --port 8000
```

A standard-library HTTP server with **zero runtime dependencies**. It runs the
planner/workers/critic loop over a goal and returns the structured run.

## Endpoints

| Method | Path | Body | Success |
|---|---|---|---|
| GET | `/health` | none | status, worker names, planner name |
| POST | `/run` | `{"goal"}` | subtasks, outputs, blackboard messages, completed |
| POST | `/compare` | `{"goal"}` | single-agent vs multi-agent structure |

Errors return JSON `{"error": ...}` with a 4xx status. `goal` is bounded to 2000 characters.

## Service level objectives

Measured by `benchmarks/stress.py` on a developer laptop:

| Objective | Target | Observed (single worker) |
|---|---|---|
| Run latency p50 | < 1 ms | about 0.02 ms |
| Run latency p99 | < 1 ms | about 0.04 ms |
| Throughput | > 10000 runs/second/core | about 38000 runs/second |

Observed with the deterministic offline agents. Real model-backed workers would dominate
latency and cost; the orchestration structure is unchanged.

## Operational constraints

- **Orchestration is CPU bound with offline agents and holds the global interpreter lock.**
  Throughput is flat across threads in one process; scale with **processes**. With
  model-backed workers, concurrency is bound by provider rate limits, and independent
  subtasks can be dispatched in parallel.
- **The plan is a dependency graph.** Subtasks run in dependency order; a cyclic or
  unsatisfiable plan cannot complete. The planner is deterministic, so plans are
  reproducible and inspectable.
- **Goals are bounded** to 2000 characters, so a single request cannot produce an unbounded
  plan.
- **Workers are the trust boundary.** Built-in workers are pure; any model-backed or
  tool-using worker must validate its input and must not execute untrusted content.
- **No persistence, no authentication.** Front the service with a gateway.

## Failure modes and responses

| Symptom | Likely cause | Response |
|---|---|---|
| `completed: false` | A subtask failed critique or a dependency was unmet | Inspect the messages; adjust the critic or plan |
| Single subtask for a compound goal | Goal lacked connective words | Expected; the planner splits on connectives |
| `400` on run | Empty or overlong goal | Inspect the `error` field |

## Capacity planning

With offline agents a single core serves tens of thousands of runs per second. With
model-backed workers, provision for provider latency and rate limits and parallelize
independent subtasks.
