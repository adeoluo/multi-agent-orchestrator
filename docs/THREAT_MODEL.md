# Threat Model - Multi-Agent Orchestrator

## Assets

- Integrity of the coordination (correct scheduling, honest review).
- Any sensitive content placed on the blackboard by model-backed agents.

## Trust boundaries

- **The goal and all agent outputs are untrusted text** on the blackboard. They are stored
  and passed between steps, never executed by the framework.

## Threats and mitigations

| Threat | Vector | Impact | Mitigation |
|---|---|---|---|
| Non-terminating run | Critic never approves, or cyclic dependencies | Hang / resource exhaustion | Bounded total iterations; incomplete subtasks reported, not looped forever |
| Rogue worker action | A side-effecting worker performs a harmful action | Unexpected effects | Built-in workers are pure; users must sandbox and authorize side-effecting workers |
| Blackboard tampering | A buggy agent corrupts shared state | Wrong results | Immutable record types; the blackboard mediates all writes and records every post |
| Sensitive data exposure | Model-backed agents write secrets to the blackboard | Data leak if exported | Documented guidance; the blackboard is in-memory and not exported by default |
| Supply-chain compromise | Malicious dependency | Code execution | Zero runtime dependencies; Dependabot and CodeQL in continuous integration |

## Residual risk

The framework guarantees termination and auditability but cannot vouch for the behavior of
user-supplied model-backed agents; their safety is the integrator's responsibility.
