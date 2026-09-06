---
name: revibe-cohere
description: Inspect the validated result as one deliberate product, finding cross-layer contradictions, duplicated responsibility, stale documentation, and historical debris before finalization.
---

# REVibe final coherence pass

Read [the shared protocol](../revibe/references/protocol.md). Consume reviewed validation, implementation, design, strategy, alignment, and relevant discovery handoffs. Coherence asks whether the finished system belongs together, not only whether individual checks pass.

## Entry and objective

Require `validate` to be `complete`. Set `cohere` to `in_progress` with the current `input_revision`. Inspect the repository and durable artifacts as a whole and confirm:

- each accepted feature has a clear purpose, boundary, owner, and consistent runtime status;
- component responsibilities, names, data flow, state, lifecycle, and dependencies do not duplicate or contradict one another;
- frontend/backend, API/schema, storage/migration, configuration, and integration expectations agree;
- UX, error states, accessibility or operational behavior match the implemented system where applicable;
- tests, fixtures, observability, documentation, examples, build, and release configuration reflect reality;
- historical layers, compatibility shims, placeholders, and dead paths have an intentional reason to remain;
- remaining risks, assumptions, and evidence limits are visible and tied to the accepted target.

Do not treat a working feature as automatically belonging in the final product. Compare the result to accepted alignment decisions and target design. Identify the smallest correction or cleanup that restores coherence, and route changes to implementation or an upstream decision owner.

## Orchestration and traces

**Controller loop.** Act as this stage's controller under the shared protocol: discover and call the permitted subagent-dispatch capability for each coherence lane, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Use the selected run throughout. Before every question, explain the subject in plain language, name its source artifact, state the observed claim and confidence, and explain downstream impact. A bare count or label is invalid; enumerate and explain each item before asking its decision. Every question must name the contradiction, product surface, or invariant, cite evidence, explain impact, and ask one choice at a time. After actual review answers, persist and read back the state/handoff, then dispatch the next stage automatically or rerun affected work; no new invocation is required. If the harness catalog proves no dispatch capability exists, record that evidence and use the sequential fallback; a failed dispatch keeps the stage in progress or blocked.

Discover available architecture, naming, dependency, UX, documentation, test, and repository-review capabilities. Delegate separate read-only lenses for cross-layer behavior, public contracts, state/lifecycle, and repository hygiene, then have the controller synthesize findings. All reviewers must cite the same baseline and return bounded packets; the controller resolves contradictions.

For each finding create or link a stable record such as `ev.cohere.<topic>` or `risk.cohere.<topic>`:

```text
surface: feature, boundary, artifact, or repository area
expected: accepted target/design statement
observed: current implementation, behavior, or documentation
coherence result: coherent | drift | duplicate | stale | unclear
evidence: stable refs and validation IDs
impact: user, architecture, reliability, maintenance, or release effect
recommendation: keep | adjust | remove | document | route upstream
confidence: level and reason
```

Review naming and responsibility at the level of the whole project. Check that cleanup does not remove useful history or compatibility. Keep proposed removals separate from accepted removals until the user reviews them.

## Review and handoff

Write `.revibe/<run-id>/handoffs/cohere.md` with the whole-system coherence assessment, cross-layer findings, retained versus cleanup candidates, documentation/configuration/test drift, risks, evidence limits, and recommendations for `finalize` or a return to implementation/upstream alignment.

Set `cohere` to `awaiting_review`. Present meaningful contradictions, cleanup candidates, compatibility decisions, documentation gaps, and residual risks. Offer recommended dispositions and custom choices. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Incorporate the response and match the handoff's `output_revision` to canonical state before setting `complete`. Set `next_stage: finalize` only when no material coherence issue is silently deferred; otherwise route to its owner.

## Edge cases and recovery

- If validation is partial, flaky, or stale, route to `validate` and identify the exact missing evidence.
- If a feature works but conflicts with accepted intent, preserve its runtime evidence, mark the target decision stale, and return to `align` rather than rationalizing it as coherent.
- If documentation, configuration, tests, and code disagree, record each source and recommend the owner that can resolve the mismatch.
- If cleanup would remove generated, vendored, compatibility, or historical files, identify their source and consumer before recommending removal.
- If two components perform the same responsibility but the user intentionally retains both, record the explicit boundary and avoid speculative consolidation.
- If a whole-system review capability is unavailable, perform targeted manual cross-checks and record the reduced confidence.
- For partial work, preserve completed review lenses and leave synthesis `in_progress`; resume from unresolved cross-layer findings.
- If upstream feedback invalidates coherence conclusions, retain the artifact, mark downstream stages stale through finalization, and rerun only affected checks.
