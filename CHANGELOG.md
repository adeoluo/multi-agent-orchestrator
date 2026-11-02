# Changelog

All notable changes to this project are documented here. The file is generated
from Conventional Commits by [git-cliff](https://git-cliff.org) when a release is cut
with `make cut-release`.

## Unreleased

### Documentation

- Standard README structure and language framing (#3)
- Vertical layered architecture diagram
- Horizontal layered architecture diagram
- Compact horizontal architecture diagram

### Build and CI

- Run CodeQL on main and on a weekly schedule only

## [0.1.0] 2026-11-02

### Features

- **core:** Add coordination types, blackboard, and agent protocols
- **orchestrator:** Add the coordination loop and built-in agents
- **cli:** Add a single-agent baseline and the command-line interface
- **graph:** Add plan validation, topological ordering, and run metrics
- **consensus:** Add consensus coordination, tool workers, and planners
- **memory:** Add shared memory, run serialization, and CLI flags
- Add HTTP service, stress benchmark, and operations documentation
- Add production observability (metrics and readiness) and reword footer
- Durable execution and an honest single-agent vs multi-agent comparison (#1)

### Bug fixes

- Deterministic worker dispatch and accurate retry metric (#19)

### Documentation

- Write README, architecture diagram, and responsible-AI cards
- Add orchestration benchmark and refresh the README
- Use plain, factual wording (#18)
- Remove em dashes from documentation (#2)

### Maintenance

- Scaffold multi-agent-orchestrator from standards template
- Apply formatter
- Wrap long line in benchmark
- **deps-dev:** Bump the python-dependencies group across 1 directory with 4 updates
- **deps:** Bump actions/upload-artifact from 4 to 7
- **deps:** Bump astral-sh/setup-uv from 4 to 7
- **deps:** Bump actions/checkout from 4 to 7
- **ci:** Bump GitHub Actions to current major versions
- Remove Dependabot configuration

### Bench

- Add large-workload scale benchmark (#20)
