<div align="center">

# REVibe

### The 11-Skill Autonomous Engineering Suite for AI Coding Agents

<p align="center">
  <b>Turn ambiguous coding requests into verified, evidence-backed, resumable runs.</b><br/>
  One controller · Bounded subagents · Contextual review questions · Resumable state isolation.
</p>

<p align="center">
  <a href="https://github.com/MPSMeridiaN/REVibe/releases/latest"><img src="https://img.shields.io/github/v/release/MPSMeridiaN/REVibe?display_name=tag&label=release&color=0284c7" alt="Latest release"></a>
  <a href="https://github.com/MPSMeridiaN/REVibe/actions/workflows/check.yml"><img src="https://img.shields.io/github/actions/workflow/status/MPSMeridiaN/REVibe/check.yml?label=CI&color=10b981" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-64748b.svg" alt="License: MIT"></a>
  <a href="#the-11-skills"><img src="https://img.shields.io/badge/skills-11%20native-6366f1.svg" alt="11 Native Skills"></a>
</p>

<br/>

<img src="docs/assets/revibe-workflow.svg" alt="REVibe 11-Skill Architecture and Workflow Lifecycle" width="100%">

<br/>
<br/>

</div>

## Overview

**REVibe** is not a bloated framework, heavy runtime, or closed SaaS. It is an ultra-lean suite of **11 native agent skills** designed to install directly into your AI coding assistant—including Claude Code, Cursor, Windsurf, OpenCode, Gemini, Cline, Kiro, and Qwen.

Instead of letting agents hallucinate, modify files prematurely, or accept unverified worker output, REVibe enforces a disciplined engineering lifecycle:

- **Orchestration**: A single Controller coordinates run-isolated state in `.revibe/<run-id>/` and dispatches bounded work.
- **Specialized Workers**: Subagents operate strictly within assigned file scopes and return structured evidence packets (`scope`, `finding`, `evidence`, `gaps`).
- **Contextual Review**: Critical decisions require 6-part context (Subject, Meaning, Origin, Observed, Impact, Decision) before consulting the human.
- **Autonomous Continuation**: Automatically cycles through 10 engineering stages from initial discovery through final release.

---

## Quickstart

### 1. Install Skills

```sh
# Local installation into repository (recommended)
npx -y MPSMeridiaN/REVibe --local

# Or global installation for current user
npx -y MPSMeridiaN/REVibe --global
```

*Compatible with Claude Code, Cursor, Windsurf, OpenCode, Gemini, Cline, Kiro, and Qwen.*

### 2. Run Any Task

```text
/revibe Refactor authentication to support session revocation
```

### 3. Resume Seamlessly

```text
/revibe resume <run-id>
```

---

## The 11 Skills

REVibe ships as 11 decoupled, cohesive native skills mapped across 4 deliberate engineering phases:

| Phase | Skill | Role & Primary Objective |
| :--- | :--- | :--- |
| **Router** | [`revibe`](product/skills/revibe/SKILL.md) | **Controller**: Manages run state, dispatches workers, audits evidence, gates stages |
| **1. Understand** | [`revibe-discover`](product/skills/revibe-discover/SKILL.md) | **Repo Inventory**: Catalogs structure, tools, entry points, and baseline claims |
| | [`revibe-verify`](product/skills/revibe-verify/SKILL.md) | **Runtime Trace**: Gathers behavioral proof, separating codebase reality from doc claims |
| | [`revibe-align`](product/skills/revibe-align/SKILL.md) | **Intent Reconciliation**: Reconciles codebase facts with user goals into an accepted target |
| **2. Blueprint** | [`revibe-design`](product/skills/revibe-design/SKILL.md) | **Architecture**: Models whole-system boundaries, interfaces, schemas, and security |
| | [`revibe-strategize`](product/skills/revibe-strategize/SKILL.md) | **Trade-offs**: Evaluates migration paths, solution directions, and operational risk |
| | [`revibe-plan`](product/skills/revibe-plan/SKILL.md) | **Task DAG**: Generates atomic, dependency-aware work packets with verification gates |
| **3. Execute** | [`revibe-implement`](product/skills/revibe-implement/SKILL.md) | **Subagent Coordination**: Coordinates parallel subagents to apply surgical, verified changes |
| | [`revibe-validate`](product/skills/revibe-validate/SKILL.md) | **Adversarial Testing**: Proves system correctness through edge-case and lifecycle checks |
| **4. Deliver** | [`revibe-cohere`](product/skills/revibe-cohere/SKILL.md) | **Cross-layer Audit**: Detects cross-layer contradictions, stale documentation, and debris |
| | [`revibe-finalize`](product/skills/revibe-finalize/SKILL.md) | **Release Readiness**: Audits repository hygiene, dependencies, and deployment readiness |

---

## State Isolation

Every workflow run is isolated under `.revibe/<run-id>/` to guarantee determinism and auditability:

```text
.revibe/<run-id>/
├── state.json       # Canonical state machine, stage statuses, and dependency DAG
├── handoffs/        # Durable evidence, trade-offs, and verification traces
└── evidence/        # Reproduction proofs, benchmark outputs, and diffs
```

---

## Documentation

- [Workflow & Review Protocol](docs/workflow.md)
- [Installation & Harnesses](INSTALL.md)
- [Harness Capability Matrix](docs/harnesses.md)
- [Validation Contract](docs/validation.md)
- [Development & Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

<div align="center">
<sub>MIT License · Maintained by <a href="https://github.com/MPSMeridiaN">MPSMeridiaN</a></sub>
</div>
