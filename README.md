# REVibe

### The engineering operating system for AI coding agents.

[![Release](https://img.shields.io/github/v/release/MPSMeridiaN/REVibe?display_name=tag&sort=semver)](https://github.com/MPSMeridiaN/REVibe/releases)
[![CI](https://github.com/MPSMeridiaN/REVibe/actions/workflows/check.yml/badge.svg)](https://github.com/MPSMeridiaN/REVibe/actions/workflows/check.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-111827.svg)](LICENSE)

Give an agent a repository URL. REVibe gives it a disciplined way to understand
what exists, separate evidence from assumptions, align changes with your intent,
and carry decisions all the way through implementation and validation.

> **inspect → verify → align → design → strategize → plan → implement → validate → cohere → finalize**

![REVibe workflow: inspect the existing system, confirm the target, execute and verify. Evidence and user decisions travel between stages.](docs/assets/journey.svg)

## Install in one command

Run the command from the project you want the agent to work on. No repository
clone is needed.

### Project-local — recommended

Installs only into the current project:

```sh
npx -y MPSMeridiaN/REVibe --local
```

Result: `./.agents/skills/`

This is the floating latest install: the GitHub package follows the repository's
default branch, so the command does not need a version edit for each release.
(`@latest` is npm registry syntax; for the current GitHub distribution, omitting
the ref is the equivalent.)

### User-global

Installs once for the current user:

```sh
npx -y MPSMeridiaN/REVibe --global
```

Result: `~/.agents/skills/`

The portable `.agents/skills` convention is the default because it is predictable
and recognized by multiple agent harnesses. Use a native target only when you
want one explicitly:

```sh
npx -y MPSMeridiaN/REVibe --local --harness claude
npx -y MPSMeridiaN/REVibe --local --harness cursor
npx -y MPSMeridiaN/REVibe --local --harness copilot
npx -y MPSMeridiaN/REVibe --local --harness cline
npx -y MPSMeridiaN/REVibe --local --harness qwen
npx -y MPSMeridiaN/REVibe --local --harness kiro
```

If you want evidence-based adaptation, opt in explicitly with `--harness auto`.
It adapts only when `REVIBE_HARNESS` or one unambiguous project marker provides a
clear signal; otherwise it safely falls back to `.agents/skills`.

### No Node.js or Python — clone and copy

The installer is optional. If you only want the product files, Git and a file
copy command are enough. Run this from the target project:

macOS, Linux, or another POSIX shell:

```sh
git clone --depth 1 https://github.com/MPSMeridiaN/REVibe.git ../REVibe-source
mkdir -p .agents/skills
cp -R ../REVibe-source/product/skills/. .agents/skills/
```

Windows PowerShell:

```powershell
git clone --depth 1 https://github.com/MPSMeridiaN/REVibe.git ..\REVibe-source
New-Item -ItemType Directory -Force .agents\skills
Copy-Item -Path ..\REVibe-source\product\skills\* -Destination .\.agents\skills -Recurse -Force
```

Copy the contents of `product/skills/`, not the `product` directory itself.
The result is exactly the 11 REVibe skill directories under `.agents/skills/`;
no manifest, lock file, installer state, or other metadata is created. For a
user-global install, copy to `~/.agents/skills/` (PowerShell:
`$env:USERPROFILE\.agents\skills`) instead. Remove the temporary clone when
you are done. To target another supported harness manually, copy the same
contents into the project or user path listed in the [harness matrix](docs/harnesses.md).
Manual copies do not auto-update or uninstall; repeat the copy from a fresh
clone when you want the latest release.

The remote launcher requires Node.js 18+ and Python 3.10+. A downloaded release
archive or development checkout can use the same installer directly:

```sh
python /path/to/revibe/install.py --local
python /path/to/revibe/install.py --global
```

Then tell your agent:

> Use revibe to understand this project. Start with discovery, show me what you found, and help me decide what should change.

## What changes after installation

REVibe adds 11 instruction-based skills and their shared references. It does not
add a service, account, MCP server, background process, or project configuration.

| Scope | Default destination | Best for |
| --- | --- | --- |
| Local | `<project>/.agents/skills/` | A repo-specific workflow and handoffs |
| Global | `~/.agents/skills/` | Making REVibe available across projects |
| Native harness | Harness-specific skills directory | An explicit host target when its native path is preferred |

### Harness coverage

REVibe uses the portable Agent Skills format: one directory per skill with a
`SKILL.md` entrypoint. Path support below is verified against each host's primary
documentation; live execution inside every host application is not part of CI.

| Coverage | Hosts | Install route |
| --- | --- | --- |
| Shared `.agents/skills` path | Codex, GitHub Copilot, Cursor, Gemini CLI, OpenCode, Amp, Warp | Omit `--harness` |
| Native target paths | Codex, GitHub Copilot, Claude Code, OpenCode, Cursor, Gemini CLI, Cline, Qwen Code, Kiro | `--harness <name>` |

See the [full harness matrix](docs/harnesses.md) for project/global paths,
precedence, compatibility aliases, and the evidence boundary for each claim.

The installer is intentionally stateless. Reinstalling is a no-op when current,
updates replace stale REVibe skills, removes old `revibe*` entries, and leaves
unrelated skill names alone. It writes no manifest, lock, transaction journal,
cache, or other bookkeeping into the project.

The destination stays clean: `.agents/skills/` contains only the 11 skill
directories. REVibe owns the reserved `revibe` / `revibe-*` namespace; keep
personal skills under another name.

## The workflow

REVibe is a connected process, not a folder of unrelated prompts:

1. **Discover** what the project contains and claims.
2. **Verify** how it actually behaves.
3. **Align** the target with the user's intent.
4. **Design** the whole-system shape and boundaries.
5. **Strategize** the feasible solution and tradeoffs.
6. **Plan** executable work with dependencies and acceptance criteria.
7. **Implement** changes without losing the decisions behind them.
8. **Validate** by trying to disprove the result.
9. **Cohere** the system, documentation, tests, and behavior into one product.
10. **Finalize** the repository for use and maintenance.

Every stage produces a durable handoff and pauses for review where user judgment
matters. The agent discovers the current harness's question capability by
behavior and schema rather than assuming one tool name; when available, it uses
that capability for every review question, marks an evidence-backed
recommendation, asks a final open-ended addition question, and states the exact
command for continuing. Findings, decisions, risks, questions, and stage
progress live in the project's `.revibe/` directory so a fresh session can
resume without pretending that missing context never existed. This is workflow
runtime data created when an agent runs REVibe; it is separate from installer
state and is not created by installation alone.

![REVibe handoff contract: evidence, user decisions, and dependencies produce a reviewed stage result.](docs/assets/handoff.svg)

## The skill suite

| Skill | Question it answers |
| --- | --- |
| `revibe` | Where should this run start or resume? |
| `revibe-discover` | What is here, and what does it claim to do? |
| `revibe-verify` | How does it actually behave, and why? |
| `revibe-align` | What do you want it to become? |
| `revibe-design` | What does that target mean across the system? |
| `revibe-strategize` | Which solution and tradeoffs should we accept? |
| `revibe-plan` | What work can be executed in what order? |
| `revibe-implement` | How do we coordinate changes without drifting? |
| `revibe-validate` | What survives attempts to break it? |
| `revibe-cohere` | Does the result make sense as one product? |
| `revibe-finalize` | Can someone build, use, and maintain it? |

## Why it holds up under real work

- **Truth stays separate from intent.** A document, a test, a runtime observation,
  and a user decision are not silently collapsed into one claim.
- **Review is part of the workflow.** Recommendations become accepted direction
  only after the user can confirm, correct, reject, defer, or replace them.
- **Continuity is explicit.** Handoffs carry evidence, uncertainty, dependencies,
  and revision context into the next stage.
- **Capability adapts honestly.** Agents can use tools, subagents, and harness
  features when available without treating missing capabilities as passing checks.

## Repository and product

| Repository | Product |
| --- | --- |
| Tests, validation, docs, packaging, CI, and release tooling | `product/skills/` and the installer |
| Maintainer-facing and development-only | The files copied into the selected skills directory |
| [Workflow docs](docs/workflow.md), [harness matrix](docs/harnesses.md), and [validation record](docs/validation.md) | The 11 skills plus shared protocol and workflow state template |

## Learn more

- [Installation, removal, and advanced targets](INSTALL.md)
- [How state and handoffs work](docs/workflow.md)
- [Harness support and portable discovery](docs/harnesses.md)
- [Development and release checks](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [MIT license](LICENSE)

REVibe is an engineering reasoning workflow, not a guarantee of correctness. Its
confidence is only as strong as the evidence the executing agent actually gathers.
