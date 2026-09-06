---
name: revibe-implement
description: Orchestrate the accepted implementation plan through scoped changes, safe parallelism, continuous checks, and explicit handling of deviations.
---

# REVibe implementation orchestration

Read [the shared protocol](../revibe/references/protocol.md). Consume the complete reviewed plan, design, strategy, alignment, and relevant verification handoffs. Implementation changes the project within those accepted boundaries and keeps the state useful while work is in motion.

## Entry and preflight

Require `plan` to be `complete`, its material tasks accepted, and the working baseline to be understood. Set `implement` to `in_progress` with the current `input_revision`. Before changing code:

- read the task graph, dependencies, acceptance criteria, migration and rollback boundaries;
- inspect the current working tree and identify pre-existing changes, generated files, and unowned edits;
- confirm the repository commands and capabilities needed for the first safe checkpoint;
- map each task to a bounded scope and an owner or worker packet;
- check that no upstream decision, plan, or baseline became stale.

Do not overwrite unrelated user work or assume a clean checkout. Respect repository conventions for branches, worktrees, commits, formatting, generated artifacts, and release files. Committing, pushing, publishing, or deploying remains subject to the user's existing authorization and repository instructions.

## Orchestration

**Controller loop.** Act as this stage's controller under the shared protocol: discover and call the permitted subagent-dispatch capability for each implementation task, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Use the selected run throughout. Before every question, explain the subject in plain language, name its source artifact, state the observed claim and confidence, and explain downstream impact. A bare count or label is invalid; enumerate and explain each item before asking its decision. Every question must name the task or changed behavior, cite evidence, explain impact, and ask one choice at a time. After actual review answers, persist and read back the state/handoff, then dispatch the next stage automatically or rerun affected work; no new invocation is required. If the harness catalog proves no dispatch capability exists, record that evidence and use the sequential fallback; a failed dispatch keeps the stage in progress or blocked.

Discover available coding agents, language tools, build systems, test runners, browsers, debuggers, and review skills. Use the smallest capability set that can make and verify each task. A single sequential worker role is a valid fallback only when delegation is unavailable or forbidden; record that limitation and perform controller review.

Group tasks by dependency and ownership. Parallelize only when scopes are disjoint, task inputs are complete, and workers cannot make incompatible architecture or contract choices. Isolate parallel work with the harness's worktrees or branches when available; otherwise serialize edits to shared files and integration seams. Never let workers independently redefine an accepted design.

For every worker assignment, including a sequential fallback role, provide the task ID, accepted decision IDs, exact scope, dependency context, completion criteria, and checks to run. Require an implementation packet:

```text
task: task.<id>
scope: files, component, feature
changes: concise description of edits
checks: commands, tests, or manual checks and results
evidence: stable refs, diff paths, baseline/revision
deviations: any target, API, schema, UX, or task change
risks/gaps: unresolved behavior, tool limits, or follow-up
next: integration or review action
```

The controller integrates worker results in dependency order. After each meaningful boundary, inspect the diff, run the narrowest relevant check, and update evidence. Keep migrations, generated outputs, public interfaces, and shared abstractions serialized with their consumers. Do not repeatedly run destructive or non-idempotent operations without restoring or confirming preconditions.

## Deviation and state trace

Record implementation evidence with stable IDs such as `ev.impl.<task>.<check>` and link it to task, decision, feature, and risk IDs. Update the canonical `tasks` index at each checkpoint. The handoff should show task status (`pending`, `in_progress`, `blocked`, `complete`, or `needs_review`), what changed, checks run, and what remains.

If implementation reveals that the accepted design, strategy, plan, or user intent is invalid, stop the affected task at a safe boundary. Record the evidence and alternatives, mark dependent records and stages stale through the protocol's transitive invalidation rules, and route to the owning upstream stage. Do not silently redesign while coding. Small mechanical deviations may continue only when they preserve accepted behavior and are recorded for review.

## Review and handoff

Write `.revibe/<run-id>/handoffs/implement.md` with the implementation summary, task graph disposition, files or components changed, integration checkpoints, evidence and confidence, deviations, remaining risks, rollback state, and validation entry points. Include the baseline and any pre-existing work that limited attribution.

Set `implement` to `awaiting_review`. Present meaningful user-visible changes, public-contract or migration effects, deviations, unresolved risks, and any task that could not be completed. Let the user confirm, correct, narrow, defer, or redirect work. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Incorporate feedback and make the handoff/state a matched pair with the same `output_revision` before setting `complete` and `next_stage: validate`. If material work remains, keep the stage `in_progress` or `awaiting_review` and do not imply implementation is done.

## Edge cases and recovery

- If a worker conflicts with another change, stop at the integration seam, preserve both scoped results, and resolve ownership or design direction before merging.
- If the build or a narrow check fails, classify the failure as setup, implementation, regression, or unrelated baseline work; record evidence and do not report the task complete.
- If a dependency, credential, platform, generated source, or external service is unavailable, use a bounded fallback and record the unverified check, constraint, and next action.
- If the plan contains a destructive migration, require the planned backup, compatibility window, rollback, or recovery checkpoint before proceeding.
- If the working tree changes unexpectedly, refresh the baseline and task map; never assume a prior diff still belongs to this run.
- If an agent stops after a partial edit, preserve the diff, record its last known check, and resume or hand off from the scoped packet rather than replaying mutations blindly.
- If a commit, branch, or worktree operation is interrupted, inspect the repository state and plan before retrying; do not use destructive reset operations to force a clean view.
- If state or handoff writing fails, preserve code changes, keep the stage `in_progress`, and recover a matched state/artifact pair per the protocol.
