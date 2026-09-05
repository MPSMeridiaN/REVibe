# Harness support

The product uses the standard `SKILL.md` entrypoint with `name` and `description`
frontmatter. The same workflow files are copied to every target; there are no
harness-specific workflow forks. The remote launcher accepts `--local` or
`--global` plus an optional `--harness`; `auto` adapts only when one native
project marker is unambiguous and otherwise uses `.agents/skills`.

Installation locations verified against primary documentation on 2026-09-05:

| Flag | Project location | User location | Source |
| --- | --- | --- | --- |
| `--codex` | `.agents/skills` | `~/.agents/skills` | [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) |
| `--claude` | `.claude/skills` | `~/.claude/skills` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| `--opencode` | `.opencode/skills` | `~/.config/opencode/skills` | [OpenCode skills](https://opencode.ai/docs/skills/) |
| `--cursor` | `.cursor/skills` | `~/.cursor/skills` | [Cursor skills](https://cursor.com/docs/skills) |
| `--gemini` | `.gemini/skills` | `~/.gemini/skills` | [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) |

OpenCode user installs respect an absolute `XDG_CONFIG_HOME` when set. Explicit `--destination` handles other configurations. Native path support is not a claim of having run every harness: see [validation](validation.md).

Codex, Cursor, Gemini CLI, and OpenCode document `.agents/skills` discovery. Claude and OpenCode also describe compatibility paths and precedence rules. Avoid redundant copies if your harness discovers multiple roots. Cursor's local user skills and cloud skill availability differ; this installer configures the local filesystem only. OpenAI also recommends plugins for distributing bundles; REVibe currently uses native skill-directory installation to preserve a single cross-harness package.

## Capability adaptation

| Capability present | Use | Fallback |
| --- | --- | --- |
| Native skill discovery | Route by concise skill descriptions | Read the entrypoint directly |
| Structured questions | Review findings and decisions in manageable batches | Plain-text choices plus custom response |
| Subagents | Scoped independent investigations and review | Sequential role passes by the orchestrator |
| Shell and test runtime | Reproduce behavior with commands and artifacts | Source-only findings with explicit confidence limits |
| Browser/debugger | Inspect UI, lifecycle, runtime state | Record unavailable checks and a reproduction recipe |
| Graph, search, language server | Follow relationships efficiently | Targeted source search and manual tracing |
| Filesystem writes | Durable state and handoffs | Return a structured handoff for the user to save; report persistence unavailable |

Discover actual capabilities in the current session. Do not hardcode tool names, model names, agent counts, or hidden harness features in the core. An unavailable tool never means a check passed.

## Design research

[Agent Skills](https://agentskills.io/specification) supplies the portable discovery format and progressive disclosure model. REVibe keeps the entrypoints focused and loads shared references only when needed.

[obra/superpowers](https://github.com/obra/superpowers) demonstrates composable engineering workflows, reviewable design, dependency-aware execution, and explicit verification. REVibe adopts those useful principles without copying its layout or activation hooks. REVibe's organizing unit is the reviewed stage handoff: reconstruction of an existing system precedes target decisions, and both remain durable across the rest of the run.

These are design influences, not runtime dependencies. No upstream source or generated asset is bundled.
