---
name: revibe-design
description: Turn an accepted target into a coherent whole-system design covering boundaries, state, data, interfaces, lifecycle, UX, and operational consequences.
---

# REVibe coherence design

Read [the shared protocol](../revibe/references/protocol.md). Consume complete discovery, verification, and alignment handoffs. Design is the bridge between “what the user wants” and “what a safe solution must mean across the system.” It does not become an implementation checklist yet.

## Entry and objective

Require `align` to be `complete` and use its accepted decisions, priorities, non-goals, constraints, and acceptance signals as the design boundary. Set `design` to `in_progress` with the current `input_revision`.

Produce a target model that explains, in repository terms where evidence allows:

- component and responsibility boundaries, ownership, and dependencies;
- domain objects, data flow, state transitions, lifecycle, persistence, and events;
- APIs, schemas, integration contracts, compatibility, and migration behavior;
- UI or interaction flows and their relationship to backend state;
- failure, recovery, cancellation, retries, concurrency, security, and performance;
- test seams, observability, documentation, configuration, build, release, and operational impact;
- what is deliberately out of scope and which assumptions still require verification.

Seek simplification. Remove accidental duplication and coupling when the evidence and accepted target justify it. Preserve an existing abstraction when it is coherent and useful; do not redesign for novelty.

## Orchestration

**Controller loop.** Act as this stage's controller under the shared protocol: delegate substantive work, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Apply feedback through the same rerun/review loop. When delegation is unavailable or forbidden, record the limitation and perform worker/controller roles sequentially without claiming independent review.

Discover available architecture, domain, UX, data-flow, dependency-graph, and risk-review capabilities. Delegate independent read-only lanes for separate concerns, then have the controller synthesize them because a state or boundary choice affects the whole product.

| Lane | Required question |
| --- | --- |
| Architecture and ownership | Which components own each responsibility, and where should boundaries move? |
| Domain, data, and state | What are the objects, invariants, transitions, storage, events, and migration rules? |
| Interfaces and experience | How do APIs, UI flows, commands, integrations, and error states express the target? |
| Reliability and operations | How do failure, recovery, security, performance, observability, deployment, and rollback work? |
| Verification seams | Which tests, harnesses, fixtures, and runtime checks can establish the design's invariants? |

The controller assigns each worker a target decision or boundary and a stopping condition. Workers return concise evidence packets or design proposals with alternatives and tradeoffs. Do not let parallel workers silently choose incompatible names, state models, or contracts; the controller synthesizes and records conflicts.

## Design trace

Create stable decision IDs such as `dec.design.<topic>` and relationship IDs such as `rel.target.<from>.<to>`. Each important design choice should link to the accepted alignment decision and the evidence that makes it necessary. Record:

- the target responsibility or invariant;
- current boundary and proposed boundary;
- affected features, components, data, interfaces, and lifecycle states;
- alternatives considered and why the selected shape fits the target;
- migration, compatibility, failure, security, performance, and test consequences;
- confidence, assumptions, and questions needing user or implementation feedback.

Use a state transition trace for nontrivial behavior:

```text
trigger → preconditions → state/data transition → side effects → observable result
       ↘ invalid/cancelled/timeout/retry/recovery paths
owner: <component or boundary>
invariants: <must remain true>
evidence: <source refs and accepted decision IDs>
```

Check that frontend and backend expectations agree, every persistent or external change has a recovery story, and every shared abstraction has a clear owner. Name compatibility and migration behavior explicitly; “update the schema” or “refactor the service” is not a sufficient design.

## Review and handoff

Write `.revibe/handoffs/design.md` with the target architecture, component responsibilities, state/data/interface model, important relationships, invariants, alternatives, migration and recovery implications, verification seams, non-goals, risks, assumptions, and unresolved questions. Keep it reviewable; link to stable diagrams or source refs only when they add information.

Set `design` to `awaiting_review`. Present material boundary, contract, state, UX, migration, security, performance, and compatibility choices. Offer recommendations and tradeoffs, then allow the user to confirm, reject, correct, or defer each item. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Incorporate feedback, mark superseded decisions and affected downstream stages stale, then set `complete` and `next_stage: strategize` only after the target design is coherent enough for a strategy choice.

## Edge cases and recovery

- If an alignment decision is pending, defer the dependent design choice and route back to `align`; do not convert a design preference into user intent.
- If the repository has several viable architectures, compare them at the boundary, risk, migration, and maintenance level; retain an explicit unresolved alternative when evidence cannot select one.
- If an external contract, schema, platform, or generated client is controlled elsewhere, mark the dependency and compatibility limit rather than designing an imaginary edit.
- If data migration is destructive or difficult to roll back, require an explicit migration, backup, dual-read/write, or recovery story and surface the user choice.
- If concurrency, lifecycle, or error behavior is unknown, add an invariant or verification question with low confidence rather than hiding it in the happy path.
- If a capability is unavailable, use static reasoning and documented contracts as bounded evidence and record the unsupported runtime or analysis capability.
- For a partial design, preserve completed lanes and their alternatives, leave synthesis `in_progress`, and resume from unresolved conflicts.
- If user correction invalidates the design, retain the prior artifact, mark dependent strategy through finalization stages `stale`, and rebuild only the affected model.
