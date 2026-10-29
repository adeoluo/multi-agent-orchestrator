# End-to-End Case Study - Planning, Working, and Critiquing a Goal

How a compound goal is decomposed, worked, and reviewed, and why that beats a single agent.

## Scenario

> "Summarize the report and then format the output."

A single agent would do this in one undifferentiated pass. The orchestrator plans it into
dependent subtasks, assigns each to a worker, and has a critic review the results.

## Running

```bash
curl -s -X POST localhost:8000/run -d '{"goal": "summarize the report and then format the output"}'
```

The response contains the plan (subtasks with dependencies), each worker's output, the
critic's reviews, and the full blackboard message log, with `completed: true`. Every step is
recorded, so the run is auditable.

## Comparing to a single agent

```bash
curl -s -X POST localhost:8000/compare -d '{"goal": "summarize and format"}'
```

```json
{
  "single_agent": {"subtasks": 1},
  "multi_agent": {"subtasks": 2, "completed": true}
}
```

The single agent collapses the goal into one step; the orchestrator decomposes it into two
dependent subtasks and reviews each. The structural difference is the point: decomposition
plus review catches per-subtask failures a single pass would miss.

## What an operator sees

- **A dependency graph, not a monolith.** The plan makes the structure explicit, so
  independent subtasks can later run in parallel and failures are localized.
- **A blackboard trace.** Every message between planner, workers, and critic is recorded,
  so a reviewer can see exactly how the goal was handled.
- **A critic gate.** Outputs are reviewed before being accepted, which is where quality and
  safety checks live.

## Takeaway

Structuring the system as a planner, workers, and a critic over a shared blackboard turns a
compound goal into an auditable, decomposable, reviewable process, which is what makes a
multi-agent system operable rather than an opaque swarm.
