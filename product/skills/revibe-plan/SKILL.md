---
name: revibe-plan
description: Convert an accepted REVibe strategy into an executable, repository-grounded implementation plan with dependencies, parallel boundaries, verification, and rollback criteria.
---

# REVibe implementation planning

Read [the shared protocol](../revibe/references/protocol.md). Consume complete design and strategy handoffs plus the reviewed target and verification limits. Planning makes the work executable by agents without requiring them to rediscover the architecture; it does not start implementation.

## Entry and objective

Require `strategize` to be `complete` and its recommendation accepted. Set `plan` to `in_progress` with the current `input_revision`. Inspect the actual repository structure, ownership, dependency graph, build/test commands, configuration, and working-tree state needed to ground the plan. Reconcile any mismatch with the strategy before writing tasks.

Produce a task graph with stable IDs such as `task.<area>.<verb>`. Each task should state:

- purpose and user-visible or system outcome;
- exact scope, likely files/modules, ownership boundary, and dependencies;
- implementation approach tied to the accepted design;
- safe parallelism or serialization requirements;
- intermediate checks, tests, integration checks, and evidence to collect;
- migration, data safety, rollback, and recovery steps;
- completion criteria and the condition that sends work back for review.

Order tasks by actual dependency and risk. Group small related edits when that makes ownership and verification clearer. Keep cleanup, documentation, configuration, observability, and release work visible when they are part of the target.

Index each task in canonical `tasks` with its ID, status, dependencies, scope, `origin_stage: plan`, and reference to its detailed handoff packet. This is the lookup used by implementation and correction propagation; task IDs must not exist only in prose.

## Orchestration and review

**Controller loop.** Act as this stage's controller under the shared protocol: discover and call the permitted subagent-dispatch capability for each planning lane, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Use the selected run throughout. Every question must name the task, dependency, or acceptance criterion, cite evidence, explain impact, and ask one choice at a time. After actual review answers, persist and read back the state/handoff, then dispatch the next stage automatically or rerun affected work; no new invocation is required. If the harness catalog proves no dispatch capability exists, record that evidence and use the sequential fallback; a failed dispatch keeps the stage in progress or blocked.

Discover available planning, architecture, test, migration, and adversarial-review capabilities. Delegate separate bounded reviews for task completeness, dependency ordering, test coverage, operational recovery, and architecture drift when they materially improve confidence. Require each reviewer to identify omissions or contradictions, not to rewrite or approve the whole plan.

Parallelize only tasks with disjoint ownership, no shared decision, and no dependency on another task's output. Mark tasks that must serialize because they touch shared abstractions, migrations, generated code, public contracts, or integration seams. State how parallel changes will be isolated and merged when the harness supports it.

Use a task trace:

```text
task: task.<id>
depends_on: <task, decision, evidence IDs>
scope: <paths, component, feature>
change: <specific outcome>
verification: <checks and expected evidence>
rollback: <reversal or recovery boundary>
done_when: <observable criteria>
owner: <agent or user-controlled boundary, if known>
```

Treat an existing dirty working tree as input. Identify which changes predate the plan and which files are safe for a worker. Never ask an agent to overwrite unrelated work merely to simplify task boundaries.

## Review and handoff

Write `.revibe/<run-id>/handoffs/plan.md` with the accepted strategy, task graph, dependency and parallelism map, repository paths, verification matrix, migration and rollback plan, integration checkpoints, open issues, risks, and completion criteria. Link every task to design, strategy, feature, constraint, or evidence IDs. Record plan recommendations and review findings with clear statuses.

Set `plan` to `awaiting_review`. Present task boundaries, ordering, parallelism, migration, verification, rollback, and material assumptions for user review. Allow correction, reprioritization, splitting, merging, deferral, or custom work. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Incorporate the response before setting `complete` and `next_stage: implement`. Do not start code changes while a material plan question is pending.

## Edge cases and recovery

- If the accepted strategy no longer matches the repository baseline, pause and route to `strategize` or `design` with the evidence; do not hide drift in task wording.
- If a task cannot name a scope, owner, dependency, verification, and rollback boundary, keep it as an open planning question rather than handing an ambiguous task to an agent.
- If safe parallelism is unclear, serialize the task and explain the cost; concurrency is optional, correctness is not.
- If generated files, external APIs, migrations, monorepo packages, or release configuration span ownership boundaries, split discovery and verification from mutations and identify the required integration checkpoint.
- If implementation is already partially done, map existing changes to tasks, preserve them, and plan only the remaining work plus verification.
- If tests or tools are unavailable, specify the best manual or static check and record the validation limitation as a constraint or risk.
- For partial planning, preserve completed task packets and leave the graph `in_progress`; resume from unresolved dependencies.
- If user feedback invalidates a strategy or design choice, preserve the plan for traceability, mark it stale, and route to the earliest affected stage.
