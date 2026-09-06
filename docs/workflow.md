# Run the workflow

Start with `/revibe <your task>` (or your harness's equivalent). The controller reads the protocol and relevant stage, creates a run for the assignment, and dispatches bounded work to subagents. It waits for their results, verifies the evidence, and brings meaningful decisions back to you. A direct stage invocation uses the same run and review contract.

The stages are separate because they settle different questions. Discovery inventories the project without claiming deep understanding. Verification reconstructs execution and gathers behavioral evidence. Alignment defines the desired product. Design examines whole-system effects. Strategy presents an approach you can review before planning turns it into detailed work. Implementation coordinates that work. Validation attempts to disprove correctness. Coherence checks the product as a whole. Finalization leaves a maintainable repository.

## Review is part of the result

A stage first saves an `awaiting_review` handoff. Before asking, the active stage
checks the current harness's exposed tools and schemas by capability, not by a
fixed name; different harnesses may call the same question capability different
things. If a structured question tool exists, the stage uses it for every
user-facing review question. It enumerates all meaningful decisions, asks them
until each is answered, deferred, or blocked, and uses manageable batches only
for independent questions. Each choice has an evidence-backed `Recommended`
option, its tradeoffs, and a custom/free-text path where useful.

You can accept, reject, correct, modify, prioritize, or defer any item. The final question in each review cycle is a separate open-ended check:

> Is there anything REVibe missed, misunderstood, or that you want to add?

If the harness has no permitted structured question tool, the controller falls back to plain
text, records that capability limit, and remains `awaiting_review` until you answer. An explicit plain-text answer can satisfy the review. The controller
incorporates your answers before calling the stage complete, saves and reads back
the state/handoff pair, and dispatches the next eligible stage automatically.
You do not need to invoke each stage. A request for more work loops back through
the affected scope. An explicit stop/pause checkpoints the run. Waiting for an
answer, a genuine blocker, or finishing the assignment also stops active work;
the controller never treats silence as “continue.”
An unanswered question stays unanswered. Accepting a feature inventory does not
prove the features work; accepting an implementation strategy does not prove
its changes pass validation.

## What persists

Each assignment has its own `.revibe/<run-id>/` directory. A new task creates a
new run; answering questions and moving between stages stay in the same run.
Requests, decisions, evidence, revisions, and archives never share a global
state file. Record IDs can repeat in separate runs without being merged.

Use `/revibe resume <run-id>` to resume an exact assignment. An ambiguous resume
asks you to choose; it does not pick the most recent folder. Completed runs stay
historical unless explicitly reopened. Runs sharing source files still need
separate checkouts or serialized edits—separate state alone does not isolate code.

The authoritative [operating protocol](../product/skills/revibe/references/protocol.md) defines the state format and recovery rules. The [state template](../product/skills/revibe/references/state-template.json) is the starting shape. Those files are installed with the router and shared by the other skills.

| Artifact | Purpose |
| --- | --- |
| `.revibe/<run-id>/state.json` | Current project baseline, stage status, findings, evidence, decisions, task index, risks, relationships, and next stage |
| `.revibe/<run-id>/handoffs/<stage>.md` | Stage result, evidence, uncertainties, user feedback, and continuation |
| `.revibe/<run-id>/evidence/` | Optional bounded evidence files and logs referenced by findings |
| `.revibe/<run-id>/state.json.bak` | Last known good state during a manual update |

The orchestrator is the only state writer. Workers return narrow evidence packets. Raw logs stay outside the compact state; superseded material is retained only as needed for traceability and archived according to the contract. Keep sensitive runtime data out of logs and handoffs.

Each handoff matches its own stage's output revision. An earlier discovery result remains valid when verification advances the global state revision. Stages record the specific prior decisions and findings they consume; task IDs resolve through the compact task index. Corrections can therefore identify affected work without rewriting every historical handoff.

Decide whether your project's `.revibe/` should be versioned according to its contents and team needs. REVibe's own repository ignores dogfooding state; the installer does not change your project's ignore rules.

## Changes travel forward

Suppose discovery records “delete an account,” verification finds soft deletion, and you decide accounts must be recoverable for 30 days. Alignment records that intent. Design traces it into storage, authorization, UI, retention, and migration. Planning links work and validation criteria to that decision.

If you later change retention to 7 days, the agent records the correction and marks dependent conclusions stale. It revisits the affected design, tasks, and checks before treating them as current. A stale artifact can explain history, but cannot authorize new work.

Similarly, runtime evidence can invalidate an assumption without changing your intent. A failed concurrency check routes work back to implementation or design as appropriate; the agent cannot silently replace the desired behavior with whatever is easiest to build.

## Resume and recover

Ask `/revibe resume <run-id>`. The agent checks the run identity, request, project baseline, and relevant handoff, then reconciles changed files or incomplete operations. It does not repeat a migration just because the earlier conversation is missing.

Legacy `.revibe/state.json` remains intact. Explicitly select the legacy task to
copy it into a new schema-2 run, retaining its evidence and user decisions while
remapping run-owned paths. The [run contract](../product/skills/revibe/references/runs.md)
defines migration and selection; no automatic merge or deletion is performed.

Malformed state is preserved for diagnosis. Temporary and backup files are checked against their handoffs, not selected by timestamp alone. If the evidence cannot establish a coherent state, the agent reconstructs only what is supported and brings unresolved choices back for review.

For a narrower run, keep the same contracts. A documentation-only project has no application runtime to validate; a file-reading harness cannot manufacture test results. Record that a concern is inapplicable or unavailable, explain why, and review the limit with the user. The process should fit the project rather than force irrelevant work into it.

## One controller, every stage

The router and each stage share one controller role. It assigns substantive work to available, permitted subagents, checks their returned evidence, and owns the conversation and canonical state. Invoking a stage directly uses the same loop. Workers investigate, propose, edit, or test within their assigned scope; finishing an assignment does not complete the stage.

1. **Assign:** provide a question, baseline/revision, accepted inputs, file ownership, expected evidence, and completion criteria.
2. **Check:** wait for final worker results, inspect artifacts and material claims, and compare the result with the criteria.
3. **Repair:** return gaps or conflicts as focused follow-ups; preserve valid work.
4. **Discuss:** save the result for review, present findings and choices, then ask the same final addition question.
5. **Persist and continue:** incorporate your feedback, verify run identity and the state/handoff pair, and immediately rerun affected work or dispatch the next stage after completion.

Independent scopes may run in parallel. Shared design decisions, conflicting writes, and migrations are serialized. Without permitted subagents, the same agent performs the worker and controller roles sequentially and records the reduced independence of review.

| Event | State and next action |
| --- | --- |
| Worker finishes | Stage stays `in_progress` while the controller checks the result |
| Evidence or deliverable is missing | Keep `in_progress`; assign a focused follow-up |
| Result or blocker needs your judgment | Save `awaiting_review`; ask the relevant questions |
| You request more work | Return to `in_progress`, or mark the upstream owner and affected dependents `stale` |
| Criteria are met and feedback is incorporated | Save `complete`, read back the pair, then dispatch the next stage |
| You have not answered | Keep `awaiting_review`; no implied approval |
| You explicitly stop | Save run status `paused` and its resume point |
| Finalization is reviewed and finished | Save stage and run `complete`; stop |

The handoff Trace stores a compact checkpoint: run ID, assignment/result references, consumed baseline/revision, controller checks, outstanding work, feedback IDs, and the next action's owning stage. A fresh session can reconcile partial changes and resume without relying on live worker IDs. Every transition waits for a successful persistence check; missing checkpoints are reconstructed only from durable evidence.

Use the project's own build, test, and runtime tools where available. REVibe supplies the reasoning workflow, not a universal test runner or a promise that every installed agent will follow instructions perfectly.
