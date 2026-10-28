# System Card - Multi-Agent Orchestrator

## Overview

- **What it is:** a from-scratch multi-agent coordination framework - a planner, workers,
  and a critic coordinated over a shared blackboard.
- **What it is not:** a model. The built-in agents are deterministic stubs; model-backed
  agents plug in behind the same protocols.
- **Version:** 0.1.0.

## Intended use

- **Primary use cases:** learning and demonstrating multi-agent coordination, task
  decomposition, dependency scheduling, and critic-driven review; a reference for the
  blackboard architecture.
- **Primary users:** engineers and researchers building or studying agent systems.

## Out-of-scope / prohibited use

- Not a production autonomous system; the built-in agents do not perform real work.
- Do not attach side-effecting workers without adding the authorization and sandboxing your
  setting requires.

## Performance

The deterministic demo decomposes a goal into dependency-ordered subtasks and completes
them under review, offline and in well under a millisecond. Coordination correctness
(dependencies, retries, termination) is covered by tests.

## Risks and limitations

- Built-in agents are stubs; quality depends entirely on the agents a user supplies.
- Sequential execution; no parallel dispatch yet.

## Safety mitigations

- Bounded iterations guarantee termination.
- Agents coordinate only through the blackboard, so there is no hidden agent-to-agent
  channel; every exchange is recorded.

## Environmental / cost footprint

Negligible; the built-in run performs only in-memory coordination with no model calls.
