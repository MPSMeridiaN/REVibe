---
name: revibe-validate
description: Validate an implemented REVibe target with feature, integration, lifecycle, recovery, and adversarial evidence that tries to disprove correctness.
---

# REVibe validation

Read [the shared protocol](../revibe/references/protocol.md). Consume the reviewed implementation handoff, accepted target and design, plan checks, and earlier verification limits. Validation is an evidence-producing attempt to disprove the result; a passing build alone is never a completion claim.

## Entry and objective

Require `implement` to be `complete` and the working baseline to match its handoff. Set `validate` to `in_progress` with the current `input_revision`. If implementation has unreviewed deviations or incomplete tasks, return to implementation review first.

Build a validation matrix that maps each accepted feature and important invariant to:

- normal behavior and user-visible acceptance;
- integration and dependency boundaries;
- invalid, empty, stale, duplicated, corrupted, or oversized inputs;
- error, timeout, retry, cancellation, recovery, and partial failure;
- concurrency, repeated operations, races, idempotency, and lifecycle cleanup;
- startup, shutdown, migration, persistence, serialization, and compatibility;
- security, permission, performance, resource, platform, locale, and browser concerns when relevant;
- documentation, configuration, build, packaging, and operational behavior.

Choose checks proportional to the risk and project. Use existing tests, targeted new scenarios, runtime probes, static inspection, integration harnesses, browser flows, and separate review agents where available. State what each check can and cannot establish.

## Orchestration and adversarial review

Discover available build, test, runtime, browser, profiler, static-analysis, fuzzing, dependency, and adversarial-review capabilities. Run independent feature or boundary checks in parallel only when they do not share mutable state; serialize migrations, persistent environments, lifecycle tests, and timing-sensitive scenarios.

Ask an independent reviewer, when available, to inspect the implementation and validation evidence against the target without being given the expected conclusion. Give it the feature/invariant, scenario, scope, and acceptance criterion. Merge its findings as evidence packets and preserve disagreements.

For every check, record a trace:

```text
check: ev.validation.<feature>.<scenario>
question: what could be false?
preconditions: environment, data, flags, seed, credentials, baseline
action: command, test, probe, or inspection
result: observed output/state/error/timing
evidence: stable source refs and run artifact
confidence: level and reason
limit: untested or unavailable condition
disposition: passed | failed | inconclusive | blocked
```

Separate a failed product behavior from a failed environment setup. A flaky or nondeterministic result remains a risk until its cause and boundary are understood. A green assertion proves its assertion under its conditions; it does not prove all feature states.

## Outcome and routing

Classify every accepted feature and invariant as supported by evidence, failed, partial, or unverified. Link failures and gaps to risks and task or decision IDs. If a fix is required, state the smallest upstream stage that owns the choice: implementation for an accepted design defect, design/strategy/plan for an invalid solution, or alignment for changed intent. Do not silently patch a failed behavior while presenting a clean validation report.

Write `.revibe/handoffs/validate.md` with the matrix, checks and results, adversarial findings, regressions, confidence, blocked checks, open risks, and recommended route. Keep run logs outside the handoff and reference stable paths.

Set `validate` to `awaiting_review`. Present meaningful failures, inconclusive checks, residual risks, and the evidence supporting each positive claim. Let the user confirm, correct, request additional scenarios, accept a bounded risk, or route back for fixes. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Incorporate feedback and the matched output revision before setting `complete`. Use `next_stage: cohere` only when the reviewed result is sufficient; otherwise route to `implement` or the owning upstream stage.

## Edge cases and recovery

- If a build is green but a feature or lifecycle scenario fails, keep the failure prominent and route it; do not average it with passing checks.
- If tests are flaky, retain attempts, environment, seeds, timing, and failure signatures; classify confidence as limited and add a risk.
- If runtime, browser, network, credentials, data, device, or production-like dependencies are unavailable, record the strongest available static/test evidence and the exact unverified boundary.
- If a check mutates persistent data or performs a migration, isolate it or restore a known fixture; do not repeat it blindly after an interruption.
- If validation reveals a race, leak, timeout, stale state, or cancellation bug, capture the trigger and lifecycle boundary and route to the owning implementation/design decision.
- If the baseline contains unrelated failures, reproduce them before the change when possible and keep attribution separate.
- For partial validation, preserve completed matrix rows, leave the stage `in_progress`, and resume unverified rows only.
- If state/artifact recovery finds mismatched output revisions, keep the last matched pair and record the missing validation result rather than declaring success.
