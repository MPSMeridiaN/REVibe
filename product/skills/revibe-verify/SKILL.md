---
name: revibe-verify
description: Trace reviewed project features through implementation and reproducible behavior, exposing contradictions, broken paths, hidden coupling, and evidence limits.
---

# REVibe verification

Read [the shared protocol](../revibe/references/protocol.md). Consume the reviewed discovery handoff and the current state; do not silently revive a rejected or unconfirmed feature. Verification determines what the system actually does under stated conditions so alignment can reason from reality.

## Entry and objective

Require `discover` to be `complete` and its artifact to be readable. Set `verify` to `in_progress` with the current `input_revision`. If discovery is awaiting review or stale, route back instead of filling the gap with assumptions.

For every in-scope feature or system concern, trace:

`documented/spec expectation → implementation path → dependencies and data flow → executed behavior → failures and limits`

Determine the feature's `runtime_status`: `working`, `partial`, `broken`, `misleading`, `duplicated`, `obsolete`, `unreachable`, or `unverified` when current evidence cannot establish behavior. Keep the discovery `review_status` (whether the user confirmed the feature belongs in scope) separate from this runtime classification. Explain why behavior exists when the evidence supports that conclusion. Surface disagreement between documentation, code, tests, configuration, and runtime observations.

## Orchestration

**Controller loop.** Act as this stage's controller under the shared protocol: discover and call the permitted subagent-dispatch capability for each verification lane, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Use the selected run throughout. Before every question, explain the subject in plain language, name its source artifact, state the observed claim and confidence, and explain downstream impact. A bare count or label is invalid; enumerate and explain each item before asking its decision. Every question must name the feature or behavior under verification, cite the runtime/source evidence, explain impact, and ask one choice at a time. After actual review answers, persist and read back the state/handoff, then dispatch the next stage automatically or rerun affected work; no new invocation is required. If the harness catalog proves no dispatch capability exists, record that evidence and use the sequential fallback; a failed dispatch keeps the stage in progress or blocked.

Discover available static analyzers, language servers, dependency graphs, test runners, browsers, debuggers, sandboxes, and runtime environments. Select the smallest useful combination. Delegate parallel lanes for independent feature paths or read-only static checks; serialize execution where shared state, migrations, timing, or environment setup makes results dependent.

Each lane should have a feature or boundary, an explicit question, and a stopping condition. Good lanes include:

| Lane | Questions to answer |
| --- | --- |
| Path trace | Which entry points, branches, handlers, and ownership boundaries serve the feature? |
| Data and state | How do data, persistence, caches, events, and state transitions move through the path? |
| Failure and lifecycle | What happens on invalid input, cancellation, retries, startup, shutdown, timeout, or dependency failure? |
| Reproduction | Which static, test, integration, or runtime checks can reproduce the expected and adverse paths? |

Workers return bounded evidence packets to the controller. Do not let a green test result erase a conflicting runtime observation, and do not infer runtime success from reachable code. When a check mutates data, isolate it, document the preconditions, and avoid repeating a non-idempotent operation blindly.

## Verification trace

For each feature, update or add evidence records with stable IDs such as `ev.<feature>.<kind>.<short-name>`. Record:

- the exact question and scope inspected;
- the path or scenario exercised and its preconditions;
- observed result, including output, state transition, error, timing, or contradiction;
- source refs for code, configuration, tests, commands, logs, and baseline;
- confidence and what remains unproven;
- `depends_on` links to the feature, decision, or prior evidence.

Use separate records for a claim and its refutation. Classify the feature only after considering the available evidence, and distinguish “not working” from “not demonstrated.” A useful finding is specific enough for alignment to decide whether to keep, change, remove, or redesign the capability.

Trace at least the project-appropriate boundary cases:

- invalid, empty, oversized, duplicated, stale, or corrupted input;
- repeated calls, retries, cancellation, timeout, startup, shutdown, and partial failure;
- concurrent or interleaved operations, races, lost updates, and lifecycle cleanup;
- missing or slow external services, permissions, secrets, network, storage, or dependencies;
- UI state versus backend state, serialization, migrations, and backward compatibility;
- platform, locale, timezone, process, browser, or environment differences when relevant.

Attempt to disprove the happy path. Keep test names and commands as evidence references, not as proof that untested behavior is safe. If runtime evidence is impossible, record the reason and the strongest static or test evidence available.

## Review and handoff

Write `.revibe/<run-id>/handoffs/verify.md` with a concise feature-by-feature truth table, execution traces, contradictions, confidence, open issues, risks, and verification limits. Link every conclusion to evidence IDs and stable source refs. Keep raw logs in a durable run artifact only when they can be reproduced or are needed to explain a failure.

Set `verify` to `awaiting_review`. Present each meaningful classification and mismatch to the user, with options to confirm, correct, narrow scope, defer, or request another check. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Incorporate the response, mark new or superseded evidence, and set `complete` plus `next_stage: align` only after the review is addressed. If the user changes the feature surface, mark dependent verification and later stages stale.

## Edge cases and recovery

- If tests are flaky, record each attempt, environment, and failure pattern; classify confidence accordingly and do not average away a meaningful failure.
- If a test passes only with unavailable credentials, network, data, or services, record the precondition and leave runtime behavior unverified.
- If a build or test cannot start, separate setup failure from product failure and trace the exact boundary that could not be reached.
- If behavior is nondeterministic, capture timing, seed, concurrency, or lifecycle conditions and recommend a focused reproduction.
- If code is generated or external, verify the generator/configuration and the integration boundary rather than pretending the source is authoritative.
- If a feature has no executable path, mark it unreachable or impossible to verify with the evidence available; do not upgrade an implementation claim to working.
- For partial runs, preserve completed packets and the last scenario attempted, leave the stage `in_progress`, and resume only from unverified scopes.
- For an interrupted state write or conflicting worker result, preserve both candidates, choose neither silently, and follow the protocol's recovery and contradiction rules.
