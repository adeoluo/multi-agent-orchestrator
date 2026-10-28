# Evaluation Report - Multi-Agent Orchestrator

> Reproduce with `python -m multi_agent_orchestrator compare`. The built-in agents are
> deterministic, so the output is exact and stable.

## Setup

- **Goal:** "research the subject and then draft an outline and then write the report".
- **Planner:** KeywordPlanner with dependency chaining (each step depends on the prior).
- **Workers:** EchoWorker and UppercaseWorker, dispatched deterministically by subtask id.
- **Critic:** LengthCritic (approves non-trivial output).

## Structure comparison

| Approach | Passes | Decomposition | Review |
|---|---|---|---|
| Single-agent | 1 | none | none |
| Multi-agent | 3 | planned, dependency-ordered | per subtask |

## Multi-agent run

```text
[planner] planned 3 subtasks
[worker]  RESEARCH THE SUBJECT
[critic]  approved
[worker]  (given task-0) done: draft an outline
[critic]  approved
[worker]  (given task-1) done: write the report
[critic]  approved
```

Each worker receives its predecessor's result as context (`given task-0`), demonstrating
dependency-aware scheduling, and every output passes critic review.

## Coordination properties (tested)

- Dependencies are respected: a subtask is dispatched only once its dependencies are
  complete.
- Rejected work is retried with feedback and recovers; persistently rejected work leaves
  the run incomplete rather than looping forever (bounded iterations).

## Reproducibility

Everything is offline and deterministic; the output above regenerates exactly.
