# AGENTS.md

Working notes for coding agents and contributors in **Multi-Agent Orchestrator**. The [README](README.md)
explains what the project does and why; this file explains how to change it safely.

## Project

A multi-agent orchestrator built from scratch: a planner decomposes a goal, specialized workers execute subtasks, and a critic verifies, coordinated over a shared blackboard.

## Layout

- `benchmarks/`: benchmark scripts and recorded results
- `docker-compose.yml`: local container setup
- `docs/`: documentation, architecture diagram source and render, design records
- `src/`: library and service source
- `tests/`: test suite

Key modules:

- `src/multi_agent_orchestrator/__init__.py`: Multi-Agent Orchestrator - planner, workers, and a critic over a blackboard.
- `src/multi_agent_orchestrator/agents.py`: Deterministic, offline built-in agents.
- `src/multi_agent_orchestrator/agents_extra.py`: A tool-using worker and additional planners.
- `src/multi_agent_orchestrator/baseline.py`: A single-agent baseline for comparison.
- `src/multi_agent_orchestrator/cli.py`: Command-line interface for the multi-agent orchestrator.
- `src/multi_agent_orchestrator/comparison.py`: An honest single-agent vs multi-agent comparison over multi-step workloads.
- `src/multi_agent_orchestrator/consensus.py`: Consensus coordination: many workers answer the same task, then aggregate.
- `src/multi_agent_orchestrator/core/__init__.py`: Core abstractions for multi-agent orchestration.
- `src/multi_agent_orchestrator/core/agents.py`: Agent roles as protocols.
- `src/multi_agent_orchestrator/core/blackboard.py`: The shared blackboard: the single source of truth for a run.
- `src/multi_agent_orchestrator/core/types.py`: Core types for multi-agent coordination.
- `src/multi_agent_orchestrator/durable.py`: Durable orchestration: checkpoint the blackboard and resume an interrupted run.
- `src/multi_agent_orchestrator/graph.py`: Dependency-graph validation.
- `src/multi_agent_orchestrator/memory.py`: Shared memory for agents.
- `src/multi_agent_orchestrator/metrics.py`: Metrics over an orchestrated run.
- `src/multi_agent_orchestrator/observability.py`: In-process request metrics for the HTTP service.
- `src/multi_agent_orchestrator/orchestrator.py`: The orchestrator: the coordination loop over planner, workers, and critic.
- `src/multi_agent_orchestrator/service.py`: A standard-library HTTP service exposing the orchestrator.
- `src/multi_agent_orchestrator/trace.py`: Serializing an orchestrated run to JSON.

## Commands

| Command | Purpose |
|---|---|
| `make help` | Show this help |
| `make setup` | Install dependencies and pre-commit hooks |
| `make format` | Format automatically |
| `make lint` | Lint (no fixes) |
| `make type` | Type-check |
| `make test` | Run tests |
| `make coverage` | Tests with coverage gate |
| `make evaluation` | Reproduce the results table |
| `make run` | Run the application entrypoint |
| `make diagram` | Render architecture diagram to SVG |
| `make docker-build` | Build the image |
| `make docker-up` | Run via docker compose |
| `make clean` | Remove caches and artifacts |
| `make all` | Full local gate (mirror of continuous integration) |
| `make changelog` | Regenerate CHANGELOG.md from Conventional Commits (git-cliff) |
| `make cut-release` | Cut a release locally: version bump, changelog, tag, GitHub release (RELEASE_VERSION=vX.Y.Z optional) |

Run the full local gate (`make all`) before committing; CI runs the same checks.

## Conventions

- Commits follow Conventional Commits (`feat:`, `fix:`, `perf:`, `refactor:`, `docs:`, `test:`, `ci:`, `chore:`).
  The changelog and the next version number are derived from them.
- Every number quoted in the README is produced by a command in this repository. When behavior
  changes, rerun that command and update the number in the same commit.
- When a component is added, removed or renamed, update `docs/architecture/architecture.mmd`
  and re-render `architecture.svg` so the diagram matches the code.
- README sections keep their fixed order. Prose avoids em and en dashes and promotional wording.
- Tests accompany behavior changes; a bug fix comes with a test that fails without it.
- Releases are cut by the maintainer with `make cut-release`, never from CI.

## Python notes

- Python is managed with `uv`; run commands through `uv run` so the locked environment is used.
- Lint and format with `ruff`; type-check with `mypy`; tests use `pytest`.
- Public functions carry type hints and a docstring that states the contract, not the steps.
