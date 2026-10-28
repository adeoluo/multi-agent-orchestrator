# Data Card - Multi-Agent Orchestrator

This project ships no datasets. It processes a single goal string at runtime and produces a
blackboard of subtasks, results, reviews, and messages.

## runtime data

- **Input:** a natural-language goal provided by the caller.
- **Produced:** subtasks (from the planner), worker outputs, critic reviews, and an ordered
  message log, all held in memory for the duration of a run.
- **Sensitivity:** whatever the caller places in the goal or that model-backed agents
  generate. Treat the blackboard as potentially sensitive if real agents are attached.

## Ethical considerations

The built-in agents are synthetic and deterministic and generate no external content. Users
attaching model-backed agents take on the data governance of those models' inputs and
outputs.
