# ADR-0002: Blackboard coordination instead of direct agent calls

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

The planner, workers, and critic must share information: the plan, each subtask's result,
and each review. They could call each other directly, or communicate through a shared
workspace.

## Decision

Use a blackboard: a single shared object that holds the goal, the plan, results, reviews,
and an ordered message log. Agents read from and write to the blackboard; they never call
each other. The orchestrator reads the blackboard to decide what to dispatch next.

## Alternatives considered

- **Direct agent-to-agent calls.** Couples the agents to each other's interfaces and
  scatters coordination logic; hard to audit.
- **A message queue between agents.** More scalable but heavier, and overkill for a
  single-process orchestrator.

## Consequences

- Agents stay decoupled and single-purpose.
- Scheduling (which subtasks are ready) and progress detection live in one place.
- The full run is an inspectable, ordered history - every post is recorded.
