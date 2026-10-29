# Scaling and Design Tradeoffs - Multi-Agent Orchestrator

How the reference design grows, and the tradeoffs taken.

## Reference architecture (today)

A single process runs a planner, a set of workers, and a critic over an in-memory
blackboard, served over a standard-library HTTP service. Offline deterministic agents;
stateless per request.

## Scaling path

| Stage | Bottleneck | Change |
|---|---|---|
| Offline agents, one process | CPU, global interpreter lock | One replica per core |
| Model-backed workers | Model latency and rate limits | Dispatch independent subtasks in parallel; batch and cache |
| Deep plans | Sequential dependency chains | Parallelize independent branches of the plan graph |
| Shared state | In-memory blackboard | Move the blackboard to a shared store for cross-process runs |
| Repeated goals | Re-planning the same goal | Cache plans and subtask results by goal |

With offline agents the service is shared-nothing and throughput is linear in replicas; with
model-backed workers the binding constraint moves to the providers.

## Substantial tradeoffs

- **Planner/workers/critic vs a single agent.** Decomposition and review localize failure
  and enable parallelism, at the cost of coordination overhead and more model calls. A single
  agent is cheaper but opaque and monolithic; the `compare` endpoint makes the structural
  difference explicit.
- **Blackboard vs direct message passing.** A shared blackboard makes the whole run auditable
  and decouples agents, at the cost of being a central structure to scale. Direct messaging is
  leaner but harder to observe. The reference chooses auditability.
- **Dependency-graph plans vs linear scripts.** A graph lets independent subtasks run in
  parallel and makes dependencies explicit, at the cost of a scheduler; a linear script is
  simpler but serial.
- **Offline agents vs model-backed agents.** Offline agents make runs deterministic and free;
  model-backed agents generalize at the cost of latency, spend, and nondeterminism. Agents are
  protocols, so either drops in.

## What would change under real load

Parallelize independent subtasks, move the blackboard to a shared store for cross-process
runs, cache plans and results, and place model-backed workers behind a batched, rate-limit
aware client. The planner, critic, and blackboard contracts are unchanged.
