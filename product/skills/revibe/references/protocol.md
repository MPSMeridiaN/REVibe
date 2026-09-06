# REVibe operating protocol

This is the shared contract for the connected REVibe skills. Read it before creating or changing `.revibe/state.json` or a stage handoff. The contract is intentionally instruction-only: it does not require a runtime, package, service, or particular harness.

## Interactive user questions

When a stage needs a user decision, inspect the actual current harness before asking. Search its exposed tool/function catalog, schemas, and descriptions by capability rather than assuming a fixed display name. Names such as `request_user_input`, `ask_user`, `elicitation`, `prompt_user`, `question`, and `clarify` are only discovery hints; confirm that the candidate can pause for a user response, present choices or free text, and return that response. Do not mistake a generic message, screen, approval, or notification tool for a question tool. If the catalog is not visible, use the harness's documented capability-discovery path and record the limit.

The controller (the active stage owner) is the only actor that asks the user. Before the first question, enumerate every meaningful unresolved choice for the stage, order dependent questions, and keep asking until each is answered, explicitly deferred, or blocked. If a structured question tool exists and is permitted in the current mode, use it for every user-facing question in the review; never switch to plain conversational questions merely for convenience. Batch only independent questions when the tool supports batching; otherwise make repeated calls and use each answer before asking a dependent question. An asynchronous question is pending until its actual answer arrives; do not infer an answer from a successful tool call, timeout, or preselected option.

Every choice question must identify one evidence-backed option as `Recommended`, include a concise reason and material tradeoffs, and provide a custom/free-text path. After all decision questions, ask one separate final open-ended question equivalent in the user's language to: “Is there anything REVibe missed, misunderstood, or that you want to add?” If the tool requires options, include a no-additions option marked `Recommended` plus a free-text/custom option; the prompt must remain open-ended. If the answer introduces a new material decision, process it as a new question cycle and repeat the final open-ended question last.

Record the question IDs, recommendations, answers, deferrals, and blockers in the handoff/state. If no permitted structured question tool exists, use the plain-text fallback and record the unavailable capability. Keep the stage `awaiting_review` until the actual response is incorporated; an explicit plain-text answer can satisfy review just as a structured answer can. Absence of the tool is never approval.

## Workflow and authority

REVibe moves a project through these short stages:

`discover → verify → align → design → strategize → plan → implement → validate → cohere → finalize`

The router may resume a stage, return to an earlier stage, or recommend a branch when evidence or user direction requires it. A later stage must consume the durable state and relevant handoffs; it must not rebuild context from conversation memory alone.

The user owns intent, priorities, acceptance, and permission for consequential changes. Evidence can support a recommendation but cannot become user intent by implication. A stage may recommend the next stage, but it must not silently accept a recommendation, silently resolve a conflict, or silently treat an unanswered question as answered.

At the end of every stage:

1. Set the stage to `awaiting_review` and write the handoff with the meaningful findings, uncertainties, recommendations, and choices that need the user's response.
2. Apply the interactive user-question protocol above. Present every meaningful item so the user can confirm, reject, correct, modify, prioritize, defer, or replace it, with a recommended choice, tradeoffs, and a custom path.
3. Ask the final open-ended addition question only after all other review questions have been answered, deferred, or blocked.
4. Incorporate the response into the handoff and canonical state before marking the stage `complete`.
5. Set `next_stage` to the recommended logical continuation, or to the earlier stage that must be revisited when the result is incomplete.
6. Tell the user the current status, what the next stage will do, and the exact command to continue (for example, `Use revibe to continue to <next_stage>`); when review or a blocker remains, state the answer or command needed to resume the current stage.

Silence is pending. It does not mean approval, completion, or permission. If an interactive question mechanism is unavailable, leave the stage `awaiting_review`, record the questions, and return the review request in the conversation.

## Canonical state

The project state lives at `.revibe/state.json`. Use [state-template.json](state-template.json) as the shape for a new project. Keep it compact: store decisions and traceable conclusions, not raw command output or a copy of the repository.

The root object has:

| Field | Contract |
| --- | --- |
| `schema_version` | Integer. The current contract is `1`. Do not silently migrate another schema. |
| `revision` | Nonnegative integer. Increase it for every canonical state write. |
| `project` | `{root, baseline}`. `root` identifies the project examined; `baseline` identifies the commit, branch, snapshot, or explicit working-tree description. |
| `stages` | Map keyed by `discover`, `verify`, `align`, `design`, `strategize`, `plan`, `implement`, `validate`, `cohere`, `finalize`. Each record has `status`, `input_revision`, `output_revision`, `artifact`, and may include `depends_on`. |
| `features` | Feature inventory and feature-level conclusions. |
| `evidence` | Traceable observations and tests. |
| `decisions` | User choices and explicitly labelled recommendations. |
| `risks` | Risks, impact, mitigation, and disposition. |
| `questions` | Open, answered, deferred, or blocked questions. |
| `constraints` | Constraints that are active, relaxed, or unknown. |
| `relationships` | Important observed or target relationships between records or system parts. |
| `assumptions` | Assumptions that remain unverified, confirmed, or invalidated. |
| `tasks` | Compact task index: stable IDs, status, dependencies, scope, and a reference to the detailed plan packet. Initialize as an empty array; absent in earlier schema-1 runs means no indexed tasks yet. |
| `next_stage` | A short stage key, or `null` when the workflow is complete or blocked pending direction. |

Every active record in the arrays has a stable `id`, a `status`, a `depends_on` array, and a `source_refs` array unless the record is a user decision with no external source. Keep IDs stable across revisions. Record IDs use disjoint prefixes: `feat.`, `ev.`, `dec.`, `risk.`, `q.`, `con.`, `rel.`, `asm.`, or `task.`. Stage dependencies use `stage:<short-stage>` and never collide with a record ID. A `depends_on` value may be either one of those stage IDs or a record ID. Dependencies refer to established inputs or earlier tasks, including ordered tasks in the same stage; never make a stage depend on a later stage's completion. The graph must remain acyclic.

Each stage adds the specific prior record IDs it consumed to its `depends_on`, alongside predecessor stages. Do not add a stage's own produced records as its inputs; `origin_stage` is provenance, not a dependency edge. Record the producing stage on new records as `origin_stage`; for older records infer it from the referenced handoff or record the missing provenance. Task IDs must resolve through `tasks`, not exist only in a prose plan. Keep the detailed task packet in the plan handoff and its compact status/index in state. This makes corrections reachable through the dependency graph.

The state is a bounded index, not an ever-growing journal. When a record is superseded or invalidated, write its full prior form to `.revibe/archive/records/<kind>-<id>.json` (or a clearly equivalent durable archive), add `superseded_by` or `invalidated_by` plus `archive_ref` to the replacement or compact tombstone, and remove the full record from the active arrays once no active record, feature `evidence_ids`, stage handoff, or open question references it. Keep a small tombstone with the pointer when an active reference must remain. Never delete an archive record that is needed to explain a user decision or evidence conflict.

Use these record shapes as a practical minimum:

```json
{
  "features": [{
    "id": "feat.example",
    "origin_stage": "discover",
    "status": "active",
    "review_status": "confirmed",
    "runtime_status": "unknown",
    "name": "Example capability",
    "claim": "What this capability is expected to do",
    "source_refs": ["README.md:12", "src/example.ts:4-38"],
    "evidence_ids": ["ev.example.runtime"],
    "depends_on": [],
    "notes": "Short context for the next stage"
  }],
  "evidence": [{
    "id": "ev.example.runtime",
    "origin_stage": "verify",
    "status": "observed",
    "kind": "runtime",
    "claim": "What was actually observed",
    "source_refs": ["command: npm test", ".revibe/runs/2026-01-01/test.log"],
    "confidence": "high",
    "depends_on": ["feat.example"],
    "notes": "Conditions and limitations"
  }],
  "decisions": [{
    "id": "dec.target.example",
    "origin_stage": "align",
    "status": "accepted",
    "question": "What should happen to the capability?",
    "choice": "Keep and simplify",
    "source_refs": [],
    "depends_on": ["feat.example"],
    "user_feedback": "User's words or a faithful concise paraphrase"
  }]
}
```

For features, keep user-reviewed existence separate from behavior: `review_status` is `candidate`, `confirmed`, `rejected`, or `deferred`, while `runtime_status` is `unknown`, `working`, `partial`, `broken`, `misleading`, `duplicated`, `obsolete`, `unreachable`, or `unverified`. A feature may be confirmed to exist while its runtime status is unknown or broken, and a code path may work while the user rejects it as out of scope. The feature's generic `status` remains its record lifecycle (`active`, `stale`, or `superseded`).

The other arrays use the same provenance pattern. Give risks, questions, constraints, relationships, and assumptions a short description or statement, and add `impact`, `mitigation`, `answer`, `from`/`to`/`kind`, or other stage-relevant fields as needed. A field that is unknown should be represented as unknown or an open question, never invented.

Stage statuses have a narrow meaning:

- `pending`: the stage has not started or is waiting for an earlier dependency.
- `in_progress`: work is actively collecting or synthesizing evidence.
- `awaiting_review`: the artifact is ready for user review; no approval is implied.
- `complete`: review feedback is incorporated and the stage's completion criteria are met.
- `stale`: a correction, changed baseline, invalidated assumption, or upstream change means the artifact must be reconsidered.

Record `input_revision` when a stage starts. When writing that stage's handoff, set its `output_revision` and the stage record's `output_revision` to the new root `revision`. On later reads, the handoff must match its own stage record, with `output_revision <= revision`; earlier handoffs keep their original revisions when another stage advances state. Do not rewrite prior handoffs merely to match the newest root revision. A stage may write a new `revision` while working, but it must not overwrite a newer state it did not read. If two writers exist, stop and reconcile as a matched state/artifact pair; do not choose a state merely because its revision is numerically highest. The active stage is the single canonical state writer. Parallel workers may inspect, test, or draft scoped notes, but they return evidence packets and do not edit the canonical state or claim user approval.

## Evidence and traceability

Separate what a source says from what the system does:

1. documentation and historical notes express claims or intent;
2. specifications and user statements express desired behavior;
3. configuration and dependency graphs imply behavior;
4. implementation shows possible behavior;
5. tests show what their assertions exercised;
6. runtime or reproducible external behavior proves what happened under stated conditions.

The order is a guide to strength, not a reason to discard disagreement. When sources conflict, record both claims, their source references, conditions, and the unresolved question. A passing test is evidence of the covered path; it is not proof that a feature works in every state.

Use confidence `high`, `medium`, or `low` with a reason in the handoff. A useful trace names the question, scope, action or observation, result, source reference, confidence, and gap. Prefer stable references such as `path:line`, a commit or revision, a reproducible command with relevant flags, a URL supplied by the user, or a compact artifact path. Do not paste large logs into state.

Each worker evidence packet should contain only:

```text
scope: the files, feature, or scenario inspected
question: the question being answered
finding: observed result, including contradictions
evidence: source refs and conditions
confidence: high | medium | low, with reason
gaps: what could not be established
recommendation: optional next action, clearly labelled
```

Merge packets by stable IDs and source references. Preserve contradictory packets until a targeted check or user decision resolves them. Bound context by reading the state, the relevant prior handoff, and targeted files; do not ask every worker to load the whole repository.

## Handoff artifact

Each completed stage writes `.revibe/handoffs/<stage>.md`. Keep it concise enough for a later stage to read in one pass. It must contain these sections, in this order:

```markdown
# <stage> handoff

- status: in_progress | awaiting_review | complete | stale
- input_revision: <integer>
- output_revision: <integer>
- next_stage: <stage or null>

## Outcome
<One paragraph describing what the stage established and what remains uncertain.>

## Evidence and confidence
| ID | Finding | Confidence | Source refs |
| --- | --- | --- | --- |

## Open issues
- <question, gap, conflict, or risk with its stable ID>

## Recommendations
| ID | Recommendation | Status | Tradeoff or rationale |
| --- | --- | --- | --- |

## User feedback
- <accepted, rejected, corrected, modified, prioritized, deferred, or unanswered item>

## Trace
- <compact stage-specific actions, boundaries, skipped checks, and recovery notes>
```

Before marking a handoff complete, make sure every meaningful recommendation has a status (`accepted`, `rejected`, `deferred`, or `pending`), every correction has a source and affected IDs, and `next_stage` is justified. Read the newly written handoff and canonical state back together; its `output_revision` must equal the stage record's `output_revision` and the root `revision` at that commit. Prior handoffs only need to match their own stage record. A handoff can remain `awaiting_review` with open items; later stages must not treat it as complete. `next_stage` is a recommendation, not permission to bypass a pending review. Reuse already accepted user decisions unless new evidence, a correction, or a scope change requires reconsideration.

## Orchestration and capabilities

Every stage runs as a controller-led loop, including directly invoked stage skills. The router and active stage owner are roles of the same controller, not competing state writers. The controller owns scope, assignment, evidence review, user dialogue, canonical state, and routing. Delegate substantive investigation, proposals, implementation, and validation to workers when delegation is available and permitted. Do not hand the whole workflow or the user's review gate to a worker. The controller may inspect sources and run targeted checks to verify returned claims; it should send substantial missing work back as a scoped assignment instead of taking over the worker's job.

At stage start, discover the harness's agent and question capabilities and relevant tools. Use the user's model preferences where supported; do not require a vendor-specific model in the portable product. If delegation is unavailable or prohibited, record the reason and perform the worker and controller roles sequentially with the same evidence and review contract. Do not claim independent review in that fallback or let missing delegation block otherwise feasible work.

### Assignment and return contract

Give each worker a bounded assignment containing:

- an assignment ID, stage, baseline, and consumed state revision;
- the question, expected deliverable, completion criteria, and stopping condition;
- relevant accepted decisions, dependency IDs, handoffs, and scoped source paths;
- file ownership and permitted actions, including checks and explicit exclusions;
- the required evidence packet and where to preserve partial work if interrupted.

Workers return the evidence packet above plus their assignment ID, consumed baseline/revision, result (`done`, `partial`, or `blocked`), changed files or artifact references, checks actually run and their outcomes, and unresolved items. A worker's `done` means its assignment is finished, never that the stage is accepted. Workers do not write canonical state or stage handoffs, ask the user, approve decisions, or dispatch a downstream stage.

Parallelize only independent scopes. Serialize dependent conclusions, overlapping writes, migrations, and checks that require a stable integrated result. Wait for assigned workers to finish before dependent synthesis or integration; progress messages are not final packets. If a worker fails or is interrupted, preserve its partial result, reconcile actual files, and reassign only the remaining scope. Do not launch a second writer while the first can still modify that scope.

If user feedback or new evidence invalidates an active assignment, stop or redirect the affected worker and establish that it can no longer write the obsolete scope before starting replacement work. Preserve and inspect partial changes; do not discard unrelated user edits. Mark affected dependencies stale and reconcile returned packets against the revised inputs before integration.

### Controller loop

1. **Load and assign.** Validate the state/handoff pair and prerequisite decisions, set the stage `in_progress`, and issue bounded assignments. Save assignment references and outstanding scope in the handoff Trace or referenced scoped notes so a fresh controller can resume.
2. **Receive and check.** Read final packets and inspect their source or artifact references. Compare claims and checks with the assignment's completion criteria and current baseline. Reproduce material claims where feasible; record checks not repeated and their evidence limits. Reconcile a packet produced before a relevant input changed before using it; revision age alone does not invalidate unrelated evidence.
3. **Repair gaps.** Return unsupported claims, conflicts, failed checks, or missing deliverables to the appropriate worker with a precise follow-up. Stay `in_progress` while work is required. Preserve valid results; rerun only affected scopes. When progress needs a user decision or a blocker cannot be resolved, save the partial evidence and surface it for review instead of looping blindly.
4. **Review with the user.** Publish a matched `awaiting_review` state/handoff pair. Summarize what is established, what remains uncertain, the controller's verification, and the decisions needed. Apply the same interactive question sequence at every stage, ending with the separate open-ended addition check. Reuse accepted answers unless new evidence or changed scope makes them relevant again.
5. **Apply feedback and route.** Record actual answers before changing status. Editorial clarification can update the reviewed result directly. Feedback requiring new work returns the owning stage to `in_progress` (or marks an upstream owner and its dependents `stale`), creates a focused assignment, and repeats verification and review for changed conclusions. Set `complete` only when completion criteria are met, feedback is incorporated, and no unresolved item blocks the next stage. Explicitly deferred nonblocking items retain their IDs and disposition. Never complete a stage merely because the user replied or a worker finished.
6. **Commit the handoff.** Use the matched-pair write and read-back procedure, record the recommended next stage and exact continuation command, and stop at the established review boundary. Another session resumes from those artifacts, not worker IDs or conversation memory.

In each handoff's Trace, retain a compact controller checkpoint: assignment IDs and result/artifact references, consumed baseline/revision, accepted or returned packets and why, verification performed, outstanding work, feedback IDs, and the next action with its owning stage. Link lengthy packets rather than embedding logs. This extends the existing handoff content without new required JSON fields or a schema migration. On older handoffs, reconstruct missing checkpoints only from durable evidence and record any gap.

Do not fabricate tool output, test success, runtime access, user feedback, or approval. If a command cannot run because of missing credentials, network, platform, data, or harness support, record the attempted check and its limitation. A partial result is useful when its boundary is explicit.

## Review and invalidation

User feedback can change any upstream conclusion. When it does, add the feedback and a new decision or evidence record, then invalidate the exact transitive dependents:

1. Seed the set with each changed record ID or `stage:<short-stage>`. Include the changed record's `origin_stage` when its handoff must be corrected, then propagate from that stage. If provenance is incomplete, locate its producing handoff before reusing downstream work; do not silently leave the old conclusion current.
2. Build a reverse index from every `depends_on` value to the records and stages that name it. Traverse that index until no new IDs appear; every reached record becomes `stale` (or `superseded` when a replacement is accepted), and every reached stage becomes `stale`.
3. Add the feature provenance index from `features[*].evidence_ids`. A feature correction invalidates its linked evidence; an evidence correction invalidates every feature that lists it, then their downstream dependents. `evidence_ids` is a provenance association, not a `depends_on` edge, so it may be inspected in both directions without introducing a dependency cycle; use a visited set during traversal.
4. Follow stage dependencies by their `stage:<short-stage>` IDs. Do not mark an unrelated earlier stage stale merely because a later stage changed.
5. Preserve the affected handoff and archive records as the bounded-state rules require. Write a new handoff only after the affected stage is rerun and reviewed.

Before accepting a write, reject self-dependencies, forward stage dependencies, unknown IDs, and cycles in the `depends_on` graph. Keep provenance links separate from the acyclic dependency graph. Do not continue a plan, implementation, or finalization that relies on invalidated intent.

If a stage discovers a material mismatch, pause at the nearest review boundary and route back to the stage that owns the decision. If implementation or validation reveals that the target is impossible, record the failure, the evidence, and candidate alternatives; ask the user to choose before silently changing scope.

## Manual atomic write and recovery

No executable state manager is required. Initialization creates revision `0` from the template without a handoff; pending stages may reference artifacts that do not yet exist. Routing-only updates and in-progress checkpoints may advance state without creating a handoff; preserve each stage's previous `output_revision`. Use these steps when committing a new or revised stage result:

1. Read `.revibe/state.json`, validate `schema_version`, stage keys, statuses, IDs, dependencies, and `revision`; note the revision consumed.
2. Prepare the complete next handoff with `output_revision: N+1` and the complete next JSON object with `revision: N+1` in same-directory temporary files: `.revibe/handoffs/<stage>.md.tmp` and `.revibe/state.json.tmp`. The stage record's `output_revision` and `artifact` must identify the same stage and revision.
3. Read back and validate both temporary files before replacement. Check that the handoff's stage, `input_revision`, `output_revision`, and `next_stage` agree with state, and that all referenced IDs and dependencies exist.
4. Replace the handoff and state as one logical transaction, preserving `.bak` copies where supported. The state replacement is the commit point; verify by reading the canonical state and its referenced handoff back and checking that both output revisions equal the canonical `revision`.
5. Remove temporary files only after the matched pair has been read back successfully. A progress checkpoint may advance state without a new artifact when the stage record remains `in_progress`; keep the prior artifact and `output_revision` unchanged. Any new or revised handoff, including an `awaiting_review` handoff, must use the matched pair procedure.

If work stops mid-write, keep the original files and inspect `.tmp` and `.bak` pairs. A candidate is recoverable only when the state and the referenced handoff both parse, name the same stage, have matching `output_revision` values, and have coherent dependencies and artifact references. Prefer the canonical matched pair when valid. Otherwise choose a matched temporary/backup pair only when its predecessor revision is the canonical revision (or its transaction is explicitly recorded in the handoff trace); never choose a file merely because its revision is highest. If more than one matched candidate remains, preserve all candidates, leave the stage `awaiting_review` or `in_progress` as appropriate, and record the recovery question. If the canonical state is malformed, preserve it as a recovery copy, restore a matched valid pair or rebuild from the template plus completed handoffs, and record the recovery in the next handoff. Never erase a user's existing state to make a stage appear complete.

For partial work, first preserve any scoped notes or code changes, then update the stage to `in_progress` with a trace of what was completed and what is still unknown. For a missing handoff, reconstruct only from durable evidence and mark confidence low until reviewed. For an interrupted or conflicting implementation, inspect the working tree and plan before resuming; do not repeat mutations blindly. For an unavailable capability, continue with the best bounded fallback and leave the limitation visible.
