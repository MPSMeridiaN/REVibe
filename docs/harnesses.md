# Harness support

The product uses the standard `SKILL.md` entrypoint with `name` and `description`
frontmatter. The same workflow files are copied to every target; there are no
harness-specific workflow forks. The remote launcher accepts `--local` or
`--global` plus an optional `--harness`. Without a harness flag it always uses
the predictable `.agents/skills` convention; `auto` is opt-in and adapts only
when one native project marker is unambiguous.

Installation locations verified against primary documentation on 2026-09-05:

| Flag / host | Project discovery | User discovery | REVibe route | Source |
| --- | --- | --- | --- | --- |
| `--codex` · Codex CLI, IDE, desktop | `.agents/skills` | `~/.agents/skills` | Default or native flag | [OpenAI: Build skills](https://learn.chatgpt.com/docs/build-skills) |
| `--copilot` · GitHub Copilot | `.github/skills`, `.agents/skills`, `.claude/skills` | `~/.copilot/skills`, `~/.agents/skills` | Default shared path or native flag | [GitHub: agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills), [Copilot CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference) |
| `--claude` · Claude Code | `.claude/skills` | `~/.claude/skills` | Native flag | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| `--opencode` · OpenCode | `.opencode/skills`, `.claude/skills`, `.agents/skills` | `~/.config/opencode/skills`, `~/.claude/skills`, `~/.agents/skills` | Default shared path or native flag | [OpenCode skills](https://opencode.ai/docs/skills/) |
| `--cursor` · Cursor | `.agents/skills`, `.cursor/skills` | `~/.agents/skills`, `~/.cursor/skills` | Default shared path or native flag | [Cursor skills](https://cursor.com/docs/skills) |
| `--gemini` · Gemini CLI | `.agents/skills`, `.gemini/skills` | `~/.agents/skills`, `~/.gemini/skills` | Default shared path or native flag | [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) |
| `--cline` · Cline | `.cline/skills`, `.clinerules/skills`, `.claude/skills` | `~/.cline/skills` | Native flag | [Cline skills](https://docs.cline.bot/customization/skills) |
| `--qwen` · Qwen Code | `.qwen/skills` | `~/.qwen/skills` | Native flag | [Qwen Code skills](https://github.com/QwenLM/qwen-code/blob/main/docs/users/features/skills.md) |
| `--kiro` · Kiro IDE, CLI, web | `.kiro/skills` | `~/.kiro/skills` (IDE/CLI) | Native flag | [Kiro CLI skills](https://kiro.dev/docs/cli/skills/) |
| Amp | `.agents/skills`, `.claude/skills` | `~/.config/agents/skills`, `~/.agents/skills`, `~/.claude/skills` | Default shared path | [Amp skills](https://ampcode.com/docs/customize/skills) |
| Warp | `.agents/skills`, `.warp/skills` | `~/.agents/skills` or configured equivalent | Default shared path | [Warp AI objects](https://docs.warp.dev/knowledge-and-collaboration/warp-drive/ai-objects) |

OpenCode user installs respect an absolute `XDG_CONFIG_HOME` when set. Explicit
`--destination` handles other configurations. Native path support means the
path and `SKILL.md` contract are documented; it is not a claim that every host
application has been run in CI. See [validation](validation.md).

The `.agents/skills` default is deliberately the lowest-friction interoperable
choice. Avoid redundant copies when a host discovers both `.agents/skills` and a
native or compatibility directory. Cursor's local user skills and cloud skill
availability differ; this installer configures the local filesystem only. OpenAI
and other hosts may offer plugin or marketplace distribution as well; REVibe
currently keeps one portable skill package and installs it into native folders
only when requested.

## Capability adaptation

| Capability present | Use | Fallback |
| --- | --- | --- |
| Native skill discovery | Route by concise skill descriptions | Read the entrypoint directly |
| Structured questions | Discover the capability by schema/description; use it for every review question with a `Recommended` choice and a final open-ended addition check | Plain-text questions plus custom response; record the capability limit |
| Subagents | Delegate substantive stage work; controller checks final packets and owns state and user review | Sequential worker/controller roles with reduced independence recorded |
| Shell and test runtime | Reproduce behavior with commands and artifacts | Source-only findings with explicit confidence limits |
| Browser/debugger | Inspect UI, lifecycle, runtime state | Record unavailable checks and a reproduction recipe |
| Graph, search, language server | Follow relationships efficiently | Targeted source search and manual tracing |
| Filesystem writes | Durable state and handoffs | Return a structured handoff for the user to save; report persistence unavailable |

Discover actual capabilities in the current session. For user questions, inspect
the exposed tool/function catalog, schemas, and descriptions for a capability
that presents choices or free text and returns the user's response. Names such
as `request_user_input`, `ask_user`, `elicitation`, `prompt_user`, `question`,
or `clarify` are only search hints; do not assume one exists or treat a generic
message, screen, approval, or notification tool as equivalent. Do not hardcode
tool names, model names, agent counts, or hidden harness features in the core.
An unavailable tool never means a check passed.

Use capabilities only when permitted in the current mode. An asynchronous
question stays pending until its answer arrives. Explicit plain-text answers
can complete a fallback review; missing tools or elapsed time cannot. Delegation
follows the same controller loop at every stage, without requiring a particular
agent count or model.

## Design research

[Agent Skills](https://agentskills.io/specification) supplies the portable discovery format and progressive disclosure model. REVibe keeps the entrypoints focused and loads shared references only when needed.

[obra/superpowers](https://github.com/obra/superpowers) demonstrates composable engineering workflows, reviewable design, dependency-aware execution, and explicit verification. REVibe adopts those useful principles without copying its layout or activation hooks. REVibe's organizing unit is the reviewed stage handoff: reconstruction of an existing system precedes target decisions, and both remain durable across the rest of the run.

These are design influences, not runtime dependencies. No upstream source or generated asset is bundled.
