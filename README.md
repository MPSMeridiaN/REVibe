# REVibe

### The engineering operating system for AI coding agents.

[![Release](https://img.shields.io/github/v/release/MPSMeridiaN/REVibe?display_name=tag)](https://github.com/MPSMeridiaN/REVibe/releases/latest)
[![CI](https://github.com/MPSMeridiaN/REVibe/actions/workflows/check.yml/badge.svg)](https://github.com/MPSMeridiaN/REVibe/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-111827.svg)](LICENSE)

Turn an unfamiliar repository and a change request into a traceable, reviewed
path from evidence to release. REVibe keeps reality, intent, implementation,
and validation connected without making the next session depend on yesterday's
conversation.

> **inspect → verify → align → design → strategize → plan → implement → validate → cohere → finalize**

![REVibe workflow: inspect the existing system, confirm the target, execute and verify. Evidence and user decisions travel between stages.](docs/assets/journey.svg)

## Install

Run this from the project you want the agent to work on. The remote installer
requires Node.js 18+ and Python 3.10+.

### Project-local · recommended

```sh
npx -y MPSMeridiaN/REVibe --local
```

Installs the 11 skills into `<project>/.agents/skills/`.

The command follows `main`. Every push to `main` that passes validation also
publishes a [release](https://github.com/MPSMeridiaN/REVibe/releases/latest)
with its commit-specific tag, changelog, ZIP, and checksum.

### User-global

```sh
npx -y MPSMeridiaN/REVibe --global
```

Installs into `~/.agents/skills/` for the current user. For a native harness
directory, add `--harness <name>` (`codex`, `copilot`, `claude`, `opencode`,
`cursor`, `gemini`, `cline`, `qwen`, `kiro`, or `auto`). See the [installation
guide](INSTALL.md) and [harness matrix](docs/harnesses.md) for the full path
matrix and behavior.

No Node.js or Python? Use the [clone-and-copy path](INSTALL.md#clone-and-copy-no-nodejs-or-python).

## Start here

```text
Use revibe to understand this project. Start with discovery, show me what you found, and help me decide what should change.
```

To continue after an interruption or in a new session:

```text
Use revibe to resume from this project's saved state.
```

## What it adds

REVibe adds 11 instruction-based skills and shared references. It adds no service,
account, MCP server, background process, or project configuration.

| Scope | Destination |
| --- | --- |
| Local | `<project>/.agents/skills/` |
| Global | `~/.agents/skills/` |
| Native harness | Harness-specific skills directory |

The installer is stateless: reinstalling updates only the reserved `revibe` /
`revibe-*` namespace and leaves unrelated skills alone. See the [harness
matrix](docs/harnesses.md) for path support and evidence boundaries.

## One controller, one handoff loop

The [`revibe`](product/skills/revibe/SKILL.md) router is the workflow controller.
For every stage, the active controller delegates bounded work to available
workers, checks their evidence, keeps the user in the review loop, and owns the
canonical state and handoff.
Workers return narrow evidence packets; they do not ask the user, approve a
recommendation, write `.revibe/state.json`, or advance a stage.

When delegation is unavailable or prohibited, the agent performs the worker and
controller roles sequentially and records the reduced independence of review.

The same contract runs at every stage boundary:

1. **Load and assign.** Validate the current state and prerequisite handoffs,
   set the stage `in_progress`, and issue assignments with a baseline, revision,
   scope, question, completion criteria, and expected evidence.
2. **Receive and check.** Wait for final worker packets, inspect their source or
   artifact references, reproduce material claims where feasible, and preserve
   contradictions or evidence limits.
3. **Repair gaps.** Send unsupported claims, conflicts, or missing deliverables
   back as focused follow-ups. Preserve valid partial work and rerun only the
   affected scope.
4. **Review with the user.** Write a matched `awaiting_review` state and handoff.
   Ask every meaningful decision with an evidence-backed `Recommended` choice,
   tradeoffs, and a custom path, then finish with: “Is there anything REVibe
   missed, misunderstood, or that you want to add?”
5. **Apply feedback and route.** Record the actual response before changing
   status. Complete only when the stage criteria and feedback are incorporated.
   Corrections mark dependent work `stale` and route to the earliest affected
   stage; otherwise `next_stage` recommends the next eligible stage.
6. **Resume from artifacts.** The next controller reads the saved state and
   relevant handoff, not worker IDs or conversation memory, and reports the
   exact command to continue.

![REVibe handoff contract: evidence, user decisions, and dependencies produce a reviewed stage result.](docs/assets/handoff.svg)

## The ten stages

| Stage | Purpose |
| --- | --- |
| [`discover`](product/skills/revibe-discover/SKILL.md) | Inventory the project and its candidate features. |
| [`verify`](product/skills/revibe-verify/SKILL.md) | Trace confirmed features through implementation and behavior. |
| [`align`](product/skills/revibe-align/SKILL.md) | Reconcile expectation, reality, and user intent into a target. |
| [`design`](product/skills/revibe-design/SKILL.md) | Design one coherent system around the accepted target. |
| [`strategize`](product/skills/revibe-strategize/SKILL.md) | Compare feasible solution directions and tradeoffs. |
| [`plan`](product/skills/revibe-plan/SKILL.md) | Turn the accepted direction into dependency-aware work. |
| [`implement`](product/skills/revibe-implement/SKILL.md) | Coordinate scoped changes and continuous checks. |
| [`validate`](product/skills/revibe-validate/SKILL.md) | Try to disprove the implemented result. |
| [`cohere`](product/skills/revibe-cohere/SKILL.md) | Check behavior, docs, tests, and responsibilities as one product. |
| [`finalize`](product/skills/revibe-finalize/SKILL.md) | Leave the repository ready for use, maintenance, or release. |

Every stage produces a reviewed handoff before the next one can consume it.

## What persists

| Artifact | Carries forward |
| --- | --- |
| `.revibe/state.json` | Canonical revision, stage status, dependencies, findings, decisions, risks, questions, and `next_stage`. |
| `.revibe/handoffs/<stage>.md` | Outcome, evidence and confidence, open issues, recommendations, user feedback, and controller trace. |
| `.revibe/runs/` | Optional bounded evidence files and logs referenced by the handoffs. |

The state is a compact index, not a transcript. If a baseline, assumption, or
user decision changes, the controller preserves the earlier result, marks
dependent work stale, and routes the affected stages back through verification
and review.

## Learn more

- [Workflow, handoffs, and recovery](docs/workflow.md)
- [Shared operating protocol](product/skills/revibe/references/protocol.md)
- [Harness support and portable discovery](docs/harnesses.md)
- [Installation and maintenance](INSTALL.md)
- [Development and release checks](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [MIT license](LICENSE)

If REVibe gives your agent a calmer, more accountable way to change code, [star
the repository](https://github.com/MPSMeridiaN/REVibe) so more builders can find
it.

REVibe is an engineering reasoning workflow, not a guarantee of correctness. Its
confidence is only as strong as the evidence the executing agent actually gathers.
