# Run the workflow

Start with `revibe` when the project is unfamiliar or you are resuming an interrupted run. The router inspects stored state, identifies the earliest useful stage, and explains why. You can also invoke a named stage directly; it checks its inputs before proceeding.

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

You can accept, reject, correct, modify, prioritize, or defer any item. Every stage finishes its review with:

The final question in the review cycle is a separate open-ended check:

> Is there anything REVibe missed, misunderstood, or that you want to add?

If the harness has no structured question tool, the stage falls back to plain
text, records that capability limit, and remains `awaiting_review`. The agent
incorporates your answers before calling the stage complete, then explains the
current status, what the next stage will do, and the exact command to continue.
An unanswered question stays unanswered. Accepting a feature inventory does not
prove the features work; accepting an implementation strategy does not prove
its changes pass validation.

## What persists

The authoritative [operating protocol](../product/skills/revibe/references/protocol.md) defines the state format and recovery rules. The [state template](../product/skills/revibe/references/state-template.json) is the starting shape. Those files are installed with the router and shared by the other skills.

| Artifact | Purpose |
| --- | --- |
| `.revibe/state.json` | Current project baseline, stage status, findings, evidence, decisions, task index, risks, relationships, and next stage |
| `.revibe/handoffs/<stage>.md` | Stage result, evidence, uncertainties, user feedback, and continuation |
| `.revibe/runs/` | Optional bounded evidence files and logs referenced by findings |
| `.revibe/state.json.bak` | Last known good state during a manual update |

The orchestrator is the only state writer. Workers return narrow evidence packets. Raw logs stay outside the compact state; superseded material is retained only as needed for traceability and archived according to the contract. Keep sensitive runtime data out of logs and handoffs.

Each handoff matches its own stage's output revision. An earlier discovery result remains valid when verification advances the global state revision. Stages record the specific prior decisions and findings they consume; task IDs resolve through the compact task index. Corrections can therefore identify affected work without rewriting every historical handoff.

Decide whether your project's `.revibe/` should be versioned according to its contents and team needs. REVibe's own repository ignores dogfooding state; the installer does not change your project's ignore rules.

## Changes travel forward

Suppose discovery records “delete an account,” verification finds soft deletion, and you decide accounts must be recoverable for 30 days. Alignment records that intent. Design traces it into storage, authorization, UI, retention, and migration. Planning links work and validation criteria to that decision.

If you later change retention to 7 days, the agent records the correction and marks dependent conclusions stale. It revisits the affected design, tasks, and checks before treating them as current. A stale artifact can explain history, but cannot authorize new work.

Similarly, runtime evidence can invalidate an assumption without changing your intent. A failed concurrency check routes work back to implementation or design as appropriate; the agent cannot silently replace the desired behavior with whatever is easiest to build.

## Resume and recover

Ask: “Use revibe to resume from this project's saved state.” The agent checks the project identity and baseline, reads the relevant handoff, and reconciles changed files or incomplete operations. It does not repeat a migration just because the earlier conversation is missing.

Malformed state is preserved for diagnosis. Temporary and backup files are checked against their handoffs, not selected by timestamp alone. If the evidence cannot establish a coherent state, the agent reconstructs only what is supported and brings unresolved choices back for review.

For a narrower run, keep the same contracts. A documentation-only project has no application runtime to validate; a file-reading harness cannot manufacture test results. Record that a concern is inapplicable or unavailable, explain why, and review the limit with the user. The process should fit the project rather than force irrelevant work into it.

## Orchestration, not fixed agent choreography

Each skill defines its objective, evidence, investigation boundaries, synthesis, handoff, review, and exit criteria. The executing agent decides which available tools improve the result.

Independent feature traces can run in parallel. Shared design decisions, conflicting write scopes, and migrations are serialized. Workers receive only their question, relevant context, ownership, and expected evidence packet. Contradictions trigger a focused follow-up instead of a majority vote. Without subagents, the orchestrator does the same work sequentially and records the reduced independence of review.

Use the project's own build, test, and runtime tools where available. REVibe supplies the reasoning workflow, not a universal test runner or a promise that every installed agent will follow instructions perfectly.
