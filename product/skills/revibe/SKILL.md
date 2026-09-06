---
name: revibe
description: Route or resume the connected REVibe engineering workflow from a project state, preserving evidence, user intent, and durable stage handoffs.
---

# REVibe router

Use this skill when the user wants REVibe to understand, change, verify, reconcile, or finish a software project. Read [the shared protocol](references/protocol.md) before operating. Use [state-template.json](references/state-template.json) only to initialize a project that has no canonical state.

The router is the workflow controller. It selects one stage skill and operates that stage as its controller: delegate bounded work, verify returned evidence, discuss the result with the user, and commit the state and handoff. Keep that ownership across stage boundaries and resume it from durable artifacts after interruption. Selecting a stage does not transfer user dialogue or canonical state ownership to a worker.

## Start or resume

1. Identify the project root and the baseline being examined: a commit, branch, snapshot, or explicit working-tree description.
2. Look for `.revibe/state.json`. If absent, create `.revibe/`, copy the template shape, set `project.root` and `project.baseline`, and initialize with revision `0`. Follow the manual atomic write procedure in the protocol.
3. Read the state and only the handoffs needed to select or resume the next stage. Validate the schema, stage keys, statuses, revisions, record IDs, dependencies, and artifact paths before doing new work.
4. Select the earliest `stale` stage first. Otherwise resume an `in_progress` stage, surface an `awaiting_review` stage for user review, or route to `next_stage` when its `stage:<short-stage>` dependencies are `complete`. If `next_stage` is missing or inconsistent, choose the earliest pending stage whose dependencies are complete and record the repair.
5. Do not skip an incomplete or awaiting-review dependency because a later stage looks easier. If the user explicitly changes scope, record that direction and route back to the owning stage so downstream work can become stale deliberately.

Before entering a selected stale or pending stage, trace its unmet dependencies back to the earliest incomplete prerequisite. Surface an awaiting-review prerequisite before rerunning its downstream consumer. `next_stage` records the recommended continuation; it never overrides this gate.

When state is malformed, do not overwrite it to make routing succeed. Preserve the file, inspect `.tmp` and `.bak` candidates, and recover only from a matched, coherent state/artifact pair or completed handoffs as described in the protocol; never choose a file merely because its revision is highest. Leave unresolved recovery as a visible question.

## Stage map

| State key | Skill to invoke | Purpose and required predecessor |
| --- | --- | --- |
| `discover` | `revibe-discover` | Build a bounded inventory of the project and candidate features. First stage. |
| `verify` | `revibe-verify` | Determine how confirmed features actually behave. Requires reviewed discovery. |
| `align` | `revibe-align` | Reconcile expectation, reality, and user intent into a target. Requires verified findings. |
| `design` | `revibe-design` | Design one coherent system around the accepted target. Requires alignment. |
| `strategize` | `revibe-strategize` | Select a reviewable solution direction and migration approach. Requires design. |
| `plan` | `revibe-plan` | Turn the accepted direction into executable, dependency-aware work. Requires strategy. |
| `implement` | `revibe-implement` | Coordinate scoped changes with continuous integration checks. Requires an accepted plan. |
| `validate` | `revibe-validate` | Try to disprove the implemented result with appropriate checks. Requires implementation. |
| `cohere` | `revibe-cohere` | Inspect the finished result as one deliberate product. Requires validation. |
| `finalize` | `revibe-finalize` | Clean, document, and leave the repository ready to continue or release. Requires coherence. |

Invoke the selected skill by its folder name when that skill is available. If it is unavailable, continue the same stage using the objective and contract in its `SKILL.md` only when the required evidence can still be collected; record the unsupported capability and lower confidence. Never claim that a missing skill or tool ran.

## Coordination rules

Before a stage begins, discover the capabilities available in the current harness: agents, skills, MCPs, CLIs, language servers, build systems, test runners, browsers, debuggers, analyzers, and especially the structured user-question capability described in the shared protocol. Match that capability by behavior and schema, not by a hardcoded tool name; names differ across harnesses. Use it for every user-facing review question when available, with the shared recommendation and final open-ended-question rules. Use capabilities as accelerators, and keep the reasoning path usable with a single agent and targeted repository inspection when they are absent.

Follow the shared protocol's assignment and return contract and controller loop for every selected stage. Supply workers only the relevant state revision, baseline, prior handoffs, scoped source paths, accepted decisions, question, and completion criteria. Wait for their final results, verify material claims, and send gaps back as scoped follow-ups before presenting the stage result. The controller is the single writer for `.revibe/state.json` and its handoff; workers neither approve nor advance stages. Record outstanding assignments and next actions in the handoff Trace or referenced notes so resumption does not depend on live worker sessions.

At every stage boundary, write `.revibe/handoffs/<stage>.md`, set `awaiting_review`, and use the shared interactive user-question protocol to review all meaningful findings, recommendations, uncertainties, and choices with the user. The final question must be the open-ended addition check. Incorporate its response; when feedback requires more work, reassign the affected scope and repeat verification and review before setting `complete`. Read the handoff back with the state and require matching `output_revision` values. Unanswered items remain pending. A recommendation is never approval.

After a correction, changed baseline, invalidated assumption, or material implementation discovery, mark dependent records and downstream stages `stale` using `depends_on`, preserve the earlier handoff, and route to the earliest affected stage. Keep `next_stage` aligned with the repaired dependency graph.

The router has no stage record of its own and does not add a separate router `complete` field. At the end of each router turn, give the user a concise status of the current stage, the meaningful pending/recovery choices, the evidence limits, what the next stage will do, and an exact command to continue. Use the active stage's review cycle; do not add a duplicate router review or repeat an answered addition check without a new material decision. The router may stop with `next_stage: null` only when finalization is reviewed and complete, or when a visible blocker requires user direction. It must report remaining uncertainty and evidence limits; it must not promise a bug-free result.
