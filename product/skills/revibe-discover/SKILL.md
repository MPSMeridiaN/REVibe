---
name: revibe-discover
description: Build a bounded, reviewable inventory of an unfamiliar project's structure, toolchain, entry points, feature claims, and validation surface.
---

# REVibe discovery

Read [the shared protocol](../revibe/references/protocol.md) and, when initializing state, [the state template](../revibe/references/state-template.json). This stage establishes what appears to exist. It does not present documentation or a static code reading as proof of runtime behavior.

## Entry and objective

Consume the project baseline and any existing state. If the `discover` stage is `stale`, retain its prior artifact for provenance and explain what changed. Set `stages.discover.status` to `in_progress` with the current `input_revision` before collecting new evidence.

Create a compact model that lets the user review the project's surface area:

- project type, languages, frameworks, runtime, build and execution model;
- repository shape, major packages or services, boundaries, and likely ownership;
- entry points, user-visible flows, APIs, jobs, commands, integrations, and persistence;
- documentation claims, specifications, configuration, scripts, CI, deployment, and release signals;
- existing tests and validation tools, including what they appear to cover;
- candidate features and important cross-feature relationships;
- constraints, assumptions, unknowns, and the questions verification must answer.

Keep the inventory high level. Follow a path deeply only when a shallow check is ambiguous or needed to identify an entry point. Do not redesign or modify the project during discovery.

## Orchestration

**Controller loop.** Act as this stage's controller under the shared protocol: discover and call the permitted subagent-dispatch capability for each substantive lane, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Use the selected run throughout. Every question must include its named feature/claim, evidence refs, impact, and one decision; ask one at a time. After actual review answers, persist and read back the state/handoff, then dispatch the next stage automatically or rerun affected work; no new invocation is required. If the harness catalog proves no dispatch capability exists, record that evidence and use the sequential fallback; a failed dispatch keeps the stage in progress or blocked.

Discover available repository search, parsers, language servers, build tools, test runners, agents, and harness capabilities. Use them when present, but retain a manual targeted path. Delegate independent read-only lanes where useful:

| Lane | Question | Typical scope |
| --- | --- | --- |
| Shape and toolchain | What can be built, run, or packaged, and from where? | top-level tree, manifests, lockfiles, scripts, CI, containers |
| Runtime and boundaries | What are the processes, entry points, packages, services, and external edges? | bootstrap files, routes, commands, workers, adapters, storage |
| Feature surface | What capabilities are claimed or visibly represented? | docs, UI routes, API schemas, commands, examples, fixtures |
| Validation and operations | What evidence can later stages collect? | tests, checks, environments, observability, deploy/release config |

The controller gives each worker one lane or bounded path and the question it must answer. Require an evidence packet containing scope, finding, source refs, confidence, gaps, and a recommendation. The controller merges packets by stable feature and evidence IDs; preserve disagreements. Avoid asking every worker to read the full repository.

## Feature and evidence trace

For each candidate feature, create a stable `feat.<short-name>` record with:

- a user-readable name and neutral claim;
- the source references that led to the candidate;
- `review_status: candidate`, `confirmed`, `rejected`, or `deferred` as appropriate after review, while leaving `runtime_status: unknown` until verification;
- linked evidence IDs and `depends_on` relationships;
- a short note about what verification must trace.

Use separate evidence records for documentation, specification, configuration, implementation, or test claims. A discovery finding should say “the repository exposes” or “the docs claim,” rather than “the feature works.” Record confidence and conditions. Add relationship records for package ownership, data flow hints, shared abstractions, or feature coupling only when evidence supports them.

Useful discovery traces include:

```text
question: What is the project's primary executable surface?
scope: package.json, src/main.*, deployment/
action: inspected scripts, entry modules, and deployment command
finding: <bounded result or contradiction>
evidence: <stable paths, lines, revision, or command>
confidence: <level and reason>
gap: <what runtime verification must establish>
```

Do not inflate a feature list with implementation helpers, generated files, vendor code, or every route. Merge aliases that clearly describe one user capability, and keep genuinely different modes separate. Mark generated or external surfaces as constraints when they cannot be inspected.

## Review and handoff

Write `.revibe/<run-id>/handoffs/discover.md` using the protocol sections. Include the project profile, feature inventory, evidence and confidence, source disagreements, open questions, constraints, and a recommended verification focus. Keep raw logs outside the handoff and reference them by stable artifact path if they matter.

Set the stage to `awaiting_review` and review each meaningful candidate feature with the user individually. Offer confirm, reject, correct, merge, split, defer, and custom choices. Explain when a choice changes verification scope. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Record every response, including “not sure yet,” before setting the stage `complete` and `next_stage: verify`. An unanswered feature remains pending and must not be treated as confirmed.

Discovery is complete only when the project baseline is explicit, candidate features have a reviewed status, the important validation surface is recorded, and verification questions are traceable. If the user supplies a new capability or removes one, update the feature records and retain the correction as user evidence.

## Edge cases and recovery

- For a monorepo, inventory packages and deployable units separately, then add relationships instead of flattening them into one feature list.
- For generated, vendored, or symlinked code, identify the owner and source of generation; do not claim to understand generated behavior from output alone.
- For missing manifests, absent docs, an empty repository, or an unbuildable project, record the absence and continue with the files that exist. Create open questions rather than guessing the stack.
- For multiple competing entry points or environments, list each with its conditions and ask the user which are in scope.
- For an unavailable search tool, agent, runtime, network, credential, or package manager, use the narrowest manual fallback and add a constraint plus a low-confidence gap.
- If discovery is interrupted, keep the partial handoff, leave the stage `in_progress`, and resume from its trace. Do not restart or mark unknown paths complete.
- If the state write fails, preserve the original state and follow the protocol's `.tmp`/`.bak` recovery procedure. The handoff may be rebuilt from durable evidence, but confidence must reflect the recovery.
