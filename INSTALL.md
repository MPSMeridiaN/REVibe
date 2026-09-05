# Install REVibe

## Remote install

Run from the project that should receive REVibe. The GitHub package is fetched by
`npx`; you do not need to clone the repository:

```sh
npx -y MPSMeridiaN/REVibe --local
```

Use `--global` for the current user's native skill directory:

```sh
npx -y MPSMeridiaN/REVibe --global
```

The remote launcher requires Node.js 18+ and Python 3.10+. A direct archive or
checkout uses the same Python installer; run it while your shell is in the target
project:

```sh
python /path/to/revibe/install.py --local
python /path/to/revibe/install.py --global
```

On Windows, `py -3 /path/to/revibe/install.py --local` is equivalent when the
Python launcher is installed. No dependency installation is needed. The command
copies the canonical skills into the selected harness's native skill directory. It
never edits agent settings or global instruction files.

## Clone and copy (no Node.js or Python)

The installer is optional. From the project that should receive REVibe, clone the
repository outside the project and copy the contents of `product/skills/`:

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

Copy `product/skills/*` itself, not the parent `product` directory. The target
will contain exactly the 11 REVibe skill directories and no installer manifest,
lock, transaction journal, cache, or other state. For a global install, replace
`.agents/skills` with `~/.agents/skills` or `$env:USERPROFILE\.agents\skills` in
PowerShell. Delete the temporary clone afterward if it is no longer needed.

Manual copies have no automatic update or uninstall command. Repeat the copy
from a fresh clone to update, or remove only the `revibe` and `revibe-*`
directories to uninstall. Keep personal skills under another name.

## Choose a destination

```sh
python install.py --local --harness claude --dry-run
python install.py --local --project /path/to/project --harness cursor
python install.py --local --harness copilot
python install.py --local --harness cline
python install.py --local --harness qwen
python install.py --local --harness kiro
python install.py --global --harness opencode
python install.py --local --harness auto
python install.py --destination /custom/skills
```

`--local` targets the current directory, or the path supplied by `--project`, and
defaults to that project's `.agents/skills/`. `--global` targets the current
user's `~/.agents/skills/`. The harness is optional: without `--harness`, the
portable `.agents/skills` target is always used. `--harness auto` uses an explicit
`REVIBE_HARNESS` value or one unambiguous native project marker (`.claude`,
`.cursor`, `.gemini`, `.opencode`, `.agents`, `.github/skills`, `.cline`, `.qwen`,
or `.kiro`); missing or ambiguous evidence falls back to `.agents/skills`.
Native targets also cover GitHub Copilot (`.github/skills`), Cline
(`.cline/skills`), Qwen Code (`.qwen/skills`), and Kiro (`.kiro/skills`). The
portable target is additionally documented by Amp and Warp. See
`docs/harnesses.md` for the complete project/global path matrix and evidence
limits. The older forms `--codex`, `--copilot`, `--claude`, `--opencode`,
`--cursor`, `--gemini`, `--cline`, `--qwen`, `--kiro`, `--all`, `--project`, and
`--user` remain available for scripted compatibility.

`--destination` names the skills directory itself and is exclusive with harness
and scope flags. The installer never edits agent settings or global instruction
files.

Some harnesses also discover other harnesses' directories. Installing all nine
native targets may expose duplicate skills. Prefer one native target for the
harness you use; the shared `.agents/skills` target is documented by several
other harnesses. The repository's `docs/harnesses.md` contains the source-backed
support matrix.

Restart or reload the harness if the skills do not appear. Use its skill picker, mention `revibe`, or ask it to read the installed `revibe/SKILL.md`. A project may need to be trusted before its skills become available.

## Update and remove

Run the same no-ref remote command to update; it follows the repository's default
branch. Pin a release tag only when a reproducible automation input is required.
An unchanged installation is a no-op. The installer replaces stale directories in
the reserved `revibe` / `revibe-*` namespace, removes stale REVibe skill names,
and leaves unrelated skill names alone. It refuses linked destinations and
existing REVibe directories with unexpected extra files; preserve or move those
files before retrying. Keep personal skills under another name.

Current installs create no manifest, lock, transaction journal, cache, or other
persistent installer state. A temporary staging directory is removed when the
command finishes. Installers from older releases may have left state behind; a
successful current install removes that legacy bookkeeping without touching
workflow state in the project's `.revibe/` directory.

```sh
npx -y MPSMeridiaN/REVibe --local --uninstall --dry-run
npx -y MPSMeridiaN/REVibe --local --uninstall
```

Use the same scope or destination as installation. Removal preserves unrelated
skills and the project's `.revibe/` workflow state. The harness skill directory
contains only skill directories, with no installer bookkeeping.

## Interrupted or partial installation

There is no persistent installer lock or recovery journal. The installer stages
the product in a temporary directory, then updates the destination. If the
process or machine stops during the final update, inspect the reserved
`revibe*` directories and rerun the same command. Unexpected extra files are
never silently deleted; preserve user changes or remove them deliberately before
retrying.

All requested destinations are checked before installation begins. Each destination
commits separately; a failure can leave earlier destinations updated. This is not
a cross-directory or power-loss-atomic transaction. Avoid editing REVibe skills
during install, update, or removal.

For a file-reading agent without skill discovery, ask it to read `product/skills/revibe/SKILL.md` from your extracted copy. Shells, subagents, browsers, and specialist integrations accelerate stages but are optional. Missing capabilities must be recorded as limitations rather than simulated evidence.

## Instructions for an installing agent

Read this file and inspect `install.py`. Determine the user's intended harness and scope from the request or current context. Preview that explicit target with `--dry-run`, then install within the authorized scope. If the harness or scope is ambiguous, ask one focused question. Do not choose `--all` merely because multiple applications are installed. Do not overwrite a conflict or edit unrelated configuration. Confirm the installed `revibe/SKILL.md` can be read and explain how to start.
