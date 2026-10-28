"""Multi-Agent Orchestrator - planner, workers, and a critic over a blackboard.

Public API: the core types, the blackboard, and the agent protocols. The orchestrator
loop and built-in agents live in their own modules.
"""

from __future__ import annotations

from multi_agent_orchestrator.core import (
    Blackboard,
    Critic,
    Message,
    Planner,
    Review,
    Role,
    Subtask,
    Worker,
    WorkerResult,
)

__version__ = "0.1.0"

__all__ = [
    "Blackboard",
    "Critic",
    "Message",
    "Planner",
    "Review",
    "Role",
    "Subtask",
    "Worker",
    "WorkerResult",
    "__version__",
]
