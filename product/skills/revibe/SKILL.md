---
name: revibe
description: Orchestrate a user-requested engineering task through delegated REVibe stages, user review, automatic continuation, and isolated resumable run state.
---

# REVibe router

Use this skill when the user invokes `/revibe <task>` (or the harness's equivalent) to understand, change, verify, reconcile, or finish a project. Read [the shared protocol](references/protocol.md), [run selection](references/runs.md), and the selected stage's entrypoint before dispatch. Use [state-template.json](references/state-template.json) to initialize each new assignment in its own run.

The router is the workflow controller. It selects one stage skill and operates that stage as its controller: delegate bounded work, verify returned evidence, discuss the result with the user, and commit the state and handoff. Keep that ownership across stage boundaries and resume it from durable artifacts after interruption. Selecting a stage does not transfer user dialogue or canonical state ownership to a worker.

## Start or resume

1. Identify the project root and the baseline being examined: a commit, branch, snapshot, or explicit working-tree description.
2. Select or create the run using the run-selection contract. A new task gets a new `.revibe/<run-id>/state.json`; feedback and stage transitions remain in that run. Set its request, identity, baseline, and initial revision `0`. Never use another run's state or legacy `.revibe/state.json` by convenience.
3. Read the state and only the handoffs needed to select or resume the next stage. Validate the schema, run identity, stage keys, statuses, revisions, record IDs, dependencies, and artifact paths before doing new work. A paused run needs an explicit resume; a blocked run needs its recorded blocker resolved. Revalidate before setting it active. Do not reopen a complete run without explicit direction.
4. Select the earliest `stale` stage first. Otherwise resume an `in_progress` stage, surface an `awaiting_review` stage for user review, or route to `next_stage` when its `stage:<short-stage>` dependencies are `complete`. If `next_stage` is missing or inconsistent, choose the earliest pending stage whose dependencies are complete and record the repair.
5. Do not skip an incomplete or awaiting-review dependency because a later stage looks easier. If the user explicitly changes scope, record that direction and route back to the owning stage so downstream work can become stale deliberately.

After selecting the stage, create bounded worker assignments and spawn available permitted subagents to gather the task-relevant evidence or perform the scoped work. Do this before an end-of-stage review, rather than replying with a plan and a command for the user to invoke the stage. Choose worker count by independent scopes and available capacity; the controller remains responsible for verifying final packets and asking the user. Missing information needed for a safe assignment may be asked first, while independent work proceeds.

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

Before a stage begins, discover the capabilities available in the current harness: agents, skills, MCPs, CLIs, language servers, build systems, test runners, browsers, debuggers, analyzers, and especially the structured user-question and subagent-dispatch capabilities described in the shared protocol. Match them by behavior and schema, not by a hardcoded tool name; names differ across harnesses. Use the question capability for every review question when available, and use every permitted subagent-dispatch capability for substantive assignments before doing that work in the controller. A discovered dispatch capability must be called; otherwise record orchestration failure and keep the assignment in progress. Use the sequential fallback only when the catalog proves no permitted dispatch capability exists.

Follow the shared protocol's assignment, return, question-context, and controller-loop contracts for every selected stage. Supply workers only the relevant state revision, baseline, prior handoffs, scoped source paths, accepted decisions, question, and completion criteria. Wait for their final results, verify material claims, and send gaps back as scoped follow-ups before presenting the stage result. Before every user question, explain the subject, its plain-language meaning, source artifact, observed evidence, confidence, and downstream impact; a bare count or label such as “the ten features” is invalid. Enumerate and explain each item individually before asking for its decision. The controller is the single writer for `.revibe/<run-id>/state.json` and its handoff; workers neither approve nor advance stages. Record outstanding assignments and next actions in the handoff Trace or referenced notes so resumption does not depend on live worker sessions.

At every stage boundary, write `.revibe/<run-id>/handoffs/<stage>.md`, set `awaiting_review`, and use the shared interactive user-question protocol to review all meaningful findings, recommendations, uncertainties, and choices with the user. The final question must be the open-ended addition check. Incorporate its response; when feedback requires more work, reassign the affected scope and repeat verification and review before setting `complete`. Read the handoff back with the state and require matching `output_revision` values. Unanswered items remain pending. A recommendation is never approval.

After a correction, changed baseline, invalidated assumption, or material implementation discovery, mark dependent records and downstream stages `stale` using `depends_on`, preserve the earlier handoff, and route to the earliest affected stage. Keep `next_stage` aligned with the repaired dependency graph.

## Continue until the assignment is settled

The initial request authorizes the connected workflow within its stated scope. After each actual review answer, incorporate feedback and check the completion criteria. If the user requests more work, rerun the affected scope or owning upstream stage. If the review is settled and the final addition answer introduces no new work, commit and read back the state/handoff, then dispatch the next eligible stage immediately. Do not end with “run this command to continue,” add a separate “may I proceed?” gate, or stop just because a stage finished.

The final open-ended addition check also accepts an explicit stop/pause request; its absence in an actual answer means continue within the authorized task. Silence is not an answer. An asynchronous question may require yielding to the user; resume this loop when the answer arrives. Do not bypass unanswered questions or a genuine permission boundary.

Respect an explicitly bounded request such as “discovery only.” A direct stage invocation alone selects the entry stage; it does not grant unrelated implementation or publishing scope. If the user limited the work to that stage, finish its review, save `run.status: paused` and the next possible stage, and report that the requested scope is finished. Do not widen the task to justify continuation.

Pause only for an actual user stop, an outstanding answer, a real blocker/permission boundary, or completed finalization. Record `run.status` appropriately (`active` while awaiting an answer), preserve `next_stage` as the resume point, and explain the specific reason if work cannot continue. Supply `/revibe resume <run-id>` only as recovery guidance when paused/interrupted, not as a routine stage gate. The router has no stage record of its own; use the stage's review once, then continue. Never promise a bug-free result.
