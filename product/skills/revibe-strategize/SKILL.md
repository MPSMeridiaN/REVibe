---
name: revibe-strategize
description: Compare feasible solution directions for an accepted REVibe design and produce a user-reviewable strategy, migration path, and risk posture before planning.
---

# REVibe solution strategy

Read [the shared protocol](../revibe/references/protocol.md). Consume the complete design handoff and accepted alignment decisions. Strategy is a deliberate choice about how to reach the target; it is not a detailed task list and it is not permission to implement.

## Entry and objective

Require `design` to be `complete`. Set `strategize` to `in_progress` with the current `input_revision`. Explain the recommended solution at a level the user can meaningfully judge:

- what changes, what remains, and which boundaries move;
- architectural direction and major tradeoffs;
- migration, rollout, compatibility, rollback, and recovery approach;
- dependency, staffing, time, cost, platform, and operational impact when evidence supports it;
- key risks, assumptions, unknowns, and how implementation or validation will retire them;
- why the recommendation best satisfies the accepted target and constraints.

## Orchestration and options

**Controller loop.** Act as this stage's controller under the shared protocol: delegate substantive work, wait for final packets, verify evidence, and return gaps as scoped follow-ups. Own canonical state, handoff, routing, and user review; worker completion is never stage acceptance. Apply feedback through the same rerun/review loop. When delegation is unavailable or forbidden, record the limitation and perform worker/controller roles sequentially without claiming independent review.

Discover available architecture, delivery, migration, risk, and feasibility review capabilities. Delegate independent option analyses where useful, then have the controller synthesize one coherent recommendation. Do not create false precision from unavailable estimates or tool output.

Compare a small set of genuinely distinct options. For each option record:

```text
strategy: stable ID and short name
target fit: which accepted decisions it satisfies or compromises
changes: components, data, interfaces, UX, operations
migration: steps, compatibility window, rollback and recovery
tradeoffs: complexity, risk, performance, maintainability, cost, speed
evidence: design, repository, and verification references
unknowns: what must be checked before commitment
recommendation: selected | alternative | rejected | deferred
```

Prefer the smallest strategy that meets the target and leaves a coherent system. Make reversibility and stopping points visible. If a strategy relies on an external owner, credential, environment, or capability, record that dependency and a fallback. If implementation may reveal an invalid assumption, define the review point and the choice that must return to the user.

## Review and handoff

Write `.revibe/handoffs/strategize.md` with the target restatement, options table, recommended strategy, scope boundaries, migration and rollback shape, risks, assumptions, feasibility gaps, and the decision needed before planning. Store recommendation decisions with stable IDs such as `dec.strategy.<name>` and link their sources and dependencies.

Set `strategize` to `awaiting_review` and obtain explicit user direction on the recommendation and any material tradeoffs. Present alternatives and a custom direction. Ask, “Is there anything REVibe missed, misunderstood, or that you want to add?” Record accepted, rejected, deferred, and corrected strategy choices before setting `complete` and `next_stage: plan`. If no option is acceptable, keep the stage awaiting review and route back to `design` or `align` as appropriate.

Do not let silence select the recommendation. Do not let a planning convenience silently change scope, compatibility, data ownership, or user priorities.

## Edge cases and recovery

- If the design is incomplete or contains conflicting boundaries, return to the specific design decision rather than comparing strategies built on incompatible assumptions.
- If there is one technically feasible option, still show its constraints, irreversible effects, and user choice; feasibility does not equal acceptance.
- If estimates are speculative, label them as assumptions and use ranges or qualitative impact instead of invented numbers.
- If a migration cannot be rolled back safely, surface the recovery boundary and require an explicit strategy decision before planning.
- If external dependencies, credentials, vendor behavior, or platform support are uncertain, state the feasibility gap and a bounded fallback path.
- If the user changes the target during review, preserve the strategy artifact, mark dependent plan through finalization stages `stale`, and route to the affected upstream stage.
- For interrupted work, preserve option analyses, leave `in_progress`, and resume synthesis without re-running mutations.
- If state recovery finds multiple valid revisions, do not combine them by guess; record the conflict and await user direction.
