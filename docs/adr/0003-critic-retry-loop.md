# ADR-0003: A critic-driven retry loop with bounded iterations

- **Status:** Accepted
- **Date:** 2026-01-01

## Context

Worker output is not always acceptable. The system needs a way to reject poor work and try
again, without risking an infinite loop.

## Decision

After a worker produces a result, the critic reviews it. On approval the subtask is marked
complete; on rejection the worker retries, up to `max_retries`, with the opportunity to use
prior context. The orchestrator additionally bounds total iterations as a function of the
plan size and retry limit, so the loop always terminates even under persistent rejection or
unsatisfiable dependencies.

## Alternatives considered

- **No review.** Simpler, but defeats the purpose of a critic and ships unverified output.
- **Unbounded retries until approval.** Risks an infinite loop when the critic can never be
  satisfied.

## Consequences

- Poor work is caught and retried, improving final quality.
- Termination is guaranteed; a subtask that cannot pass review is left incomplete and the
  run reports `completed = False`.
- The retry count is a single, tunable knob.
