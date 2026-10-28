"""Entrypoint: `python -m multi_agent_orchestrator`."""

from __future__ import annotations

from multi_agent_orchestrator import __version__
from multi_agent_orchestrator.configuration import settings


def main() -> None:
    header = f"Multi Agent Orchestrator v{__version__}"
    status = f"environment={settings.environment}, seed={settings.seed}"
    print(f"{header} - {status}")


if __name__ == "__main__":
    main()
