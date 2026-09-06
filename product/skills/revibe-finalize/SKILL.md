---
name: revibe-finalize
description: Finish a reviewed REVibe project by auditing repository hygiene, documentation, dependencies, release readiness, and evidence-backed cleanup while preserving user authority.
---

# REVibe repository finalization

Read [the shared protocol](../revibe/references/protocol.md). Consume reviewed coherence, validation, implementation, design, strategy, alignment, and relevant discovery handoffs. Finalization leaves the project understandable, usable, maintainable, and ready for its stated next use without fabricating certainty.

## Entry and objective

Require `cohere` to be `complete`. Set `finalize` to `in_progress` with the current `input_revision`. Audit the project at its current baseline for:

- temporary artifacts, debug output, stale implementation versions, superseded files, dead code, unused dependencies, and unnecessary generated outputs;
- duplicated or misleading documentation, placeholders, outdated examples, comments, names, configuration, and scripts;
- ignored files, build outputs, release/package metadata, install or bootstrap instructions, and repository organization;
- test fixtures, checks, observability, migrations, compatibility layers, and known validation limits;
- clone, understand, build, use, maintain, and continue-development paths relevant to the target.

Compare every proposed cleanup with evidence and the accepted target. Consolidate or preserve historical information intentionally. Existing authorization for the accepted strategy and plan persists: routine, reversible cleanup within that scope may be applied and then reviewed at the stage boundary without asking for permission again. For a new destructive action, migration, release action, external publication, or material scope change, identify its exact target, consumers, recovery path, and the needed user decision or existing authorization before applying it. Keep scope within the project and the user's authority.

## Orchestration and audit trace

**Controller loop.** Act as this stage's controller under the shared protocol: delegate substantive work, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Use the selected run throughout. After actual review answers, persist and read back the state/handoff, then dispatch the next stage automatically or rerun affected work; no new invocation is required. Pause only for an explicit stop, unanswered question, real blocker, or finished finalization. When delegation is unavailable or forbidden, record the limitation and perform worker/controller roles sequentially without claiming independent review.

Discover available repository, dependency, build, packaging, documentation, security, and release checks. Delegate independent read-only audits for source hygiene, docs/configuration, dependencies/build, and reproducibility, then have the controller synthesize. Do not ask all reviewers to load the whole repository.

For each cleanup or readiness item record a stable ID such as `ev.finalize.<topic>` or `risk.finalize.<topic>`:

```text
item: exact path, dependency, command, or repository surface
evidence: why it is stale, required, misleading, or intentionally retained
action: keep | consolidate | update | remove | defer | user decision
scope: files and consumers affected
verification: check after the action
recovery: restore or rollback boundary
confidence: level and reason
```

Apply evidence-backed changes within the accepted scope. After each meaningful cleanup, inspect the diff and rerun the narrowest affected check. Perform final build, test, packaging, or manual checks appropriate to the project and state their conditions. Report residual uncertainty, unavailable environments, and known risks plainly; never claim “bug-free.”

## Review and handoff

Write `.revibe/<run-id>/handoffs/finalize.md` with the final readiness assessment, applied and deferred cleanup, documentation/configuration updates, validation evidence, remaining risks and limitations, recovery notes, and a concise continuation or release recommendation. Link actions to source refs, feature/decision/risk IDs, and the final baseline.

Set `finalize` to `awaiting_review`. Present every material deletion, dependency or compatibility change, documentation claim, release/readiness limitation, and deferred risk. Let the user confirm, reject, modify, defer, or request a final check. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Incorporate the response and set `finalize` and `run.status` to `complete` with `next_stage: null` only after the review is closed and required work is finished. Commit and read back the matched run identity, state, and handoff revisions before reporting completion. If a correction affects prior behavior, mark the affected stage stale and route back instead of sealing an inconsistent repository.

## Edge cases and recovery

- If the user has not authorized a consequential cleanup, preserve the candidate and record it as deferred or pending; do not infer approval from silence.
- If a file is generated, vendored, shared, ignored, or owned by another system, identify its source and consumer before changing or removing it.
- If the repository is dirty with unrelated work, separate attribution and leave unrelated changes intact.
- If dependency or release checks need network, credentials, a platform, production data, or a publishing service, record the exact unavailable boundary and use a safe local check.
- If cleanup reveals a design or implementation defect, route back to the owning stage and preserve the finalization audit as a stale artifact.
- If build outputs or temporary files are useful for diagnosis, preserve them in an intentional location or archive reference before recommending removal.
- For interrupted finalization, preserve each applied diff and its post-change check, leave the stage `in_progress`, and resume from the audit trace.
- If state/artifact replacement is interrupted, recover only a matched pair whose state revision and handoff `output_revision` agree; never finalize from an unmatched highest revision.
