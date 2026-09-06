---
name: revibe-align
description: Reconcile verified behavior with documented expectations and explicit user intent, producing the reviewed target product definition.
---

# REVibe alignment

Read [the shared protocol](../revibe/references/protocol.md). Consume complete discovery and verification handoffs. This is the point where REVibe stops assuming the current system should survive and asks what it should become.

## Entry and objective

Require `verify` to be `complete`. Set `align` to `in_progress` with the current `input_revision`. For each meaningful feature, system concern, and verified mismatch, build a trace:

`current expectation → actual implementation → actual behavior → user intent → desired target`

Help the user decide whether the capability should remain, change, be redesigned, merge, simplify, disappear, be replaced, or be added. Define enough target behavior, priorities, non-goals, acceptance signals, and constraints for design to work without guessing. Preserve user authority when the evidence does not determine intent.

## Orchestration and decision framing

**Controller loop.** Act as this stage's controller under the shared protocol: delegate substantive work, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Apply feedback through the same rerun/review loop. When delegation is unavailable or forbidden, record the limitation and perform worker/controller roles sequentially without claiming independent review.

Discover available product, domain, UX, architecture, and requirement-review capabilities. Delegate preparation of independent feature decision packets, then have the controller serialize synthesis because one target choice can change another feature's meaning.

For every meaningful item, present a compact decision packet:

```text
item: feature or system concern
evidence: what is claimed and what verification found
conflict: where expectation and behavior differ
options: retain | change | redesign | merge | simplify | remove | replace | add | custom
recommendation: the evidence-backed choice, if any
tradeoffs: material user, compatibility, cost, risk, or complexity effects
questions: what only the user can decide
```

Create stable decision IDs such as `dec.target.<feature>`. A recommendation remains `proposed` until the user responds. Record accepted, rejected, deferred, corrected, and custom choices with the user's words or a faithful concise paraphrase. Add acceptance criteria as decisions or constraints rather than hiding them in prose.

Resolve scope explicitly for competing stakeholders, multiple products, legacy compatibility, and externally imposed constraints. Do not infer that a user wants a feature because it is implemented, documented, popular, or easy to preserve. If the desired target is intentionally “leave this unknown,” record that as a decision and its verification boundary.

## Target trace and handoff

For each target item, link the decision to feature and evidence IDs, affected relationships, constraints, risks, and assumptions. Add target relationships when a user choice changes ownership, lifecycle, data flow, UX, or compatibility. State what remains unchanged where that boundary prevents accidental redesign.

Write `.revibe/handoffs/align.md` with:

- a short target-product statement;
- the expectation/actual/intent/target table;
- accepted, rejected, deferred, and still-proposed decisions;
- priorities, non-goals, acceptance signals, constraints, and assumptions;
- risks and questions that design must resolve;
- a recommendation for `design` or a return to `verify`.

Set `align` to `awaiting_review` and walk through every meaningful target choice. Offer a recommended option with tradeoffs and a custom direction. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Incorporate the response before setting `complete` and `next_stage: design`. A missing response leaves the decision pending. Do not let design proceed on a pending choice that materially changes architecture or scope.

## Edge cases and recovery

- If verification is incomplete, contradictory, or stale, route back to the owning verification scope and show the specific evidence gap.
- If the user gives a new requirement that conflicts with an accepted choice, preserve the old decision, add a superseding decision, and mark dependent design, strategy, plan, implementation, validation, and finalization stages stale.
- If multiple stakeholders or products are in scope, keep their target decisions separate and record the boundary instead of averaging them into vague intent.
- If a requested behavior conflicts with a hard constraint, state the conflict and offer feasible alternatives; do not silently relax the constraint.
- If the user cannot decide yet, defer the decision, state the consequence, and keep `next_stage` at `align` when downstream work would otherwise guess.
- If the project has no explicit user intent, use evidence to frame choices but ask for intent before accepting a target.
- For partial work, preserve completed decision packets and leave unresolved items pending. Resume from those packets rather than reopening settled choices without cause.
- If state or handoff recovery is needed, preserve the prior target and rebuild only from traceable evidence; record the recovery and confidence in the new artifact.
