# Install REVibe

REVibe is a portable set of 11 instruction-based skills. It adds no service,
account, background process, or project configuration. Run the installer from the
project the agent should work on unless you are intentionally installing for the
current user.

## Quick install

The remote launcher needs Node.js 18+ and Python 3.10+:

```sh
# project-local, portable target: <project>/.agents/skills/
npx -y MPSMeridiaN/REVibe --local

# current-user global, portable target: ~/.agents/skills/
npx -y MPSMeridiaN/REVibe --global
```

For a checkout or downloaded archive, run the same installer directly:

```sh
python /path/to/REVibe/install.py --local
python /path/to/REVibe/install.py --global
```

On Windows, use `py -3` in place of `python` when needed. The installer has no
third-party Python dependencies.

## Choose a destination

Without `--harness`, `--local` and `--global` use the portable `.agents/skills/`
target. Native targets are selected explicitly when the host expects another
directory:

```sh
npx -y MPSMeridiaN/REVibe --local --harness claude
npx -y MPSMeridiaN/REVibe --global --harness opencode
npx -y MPSMeridiaN/REVibe --local --harness auto
```

Supported names are `codex`, `copilot`, `claude`, `opencode`, `cursor`,
`gemini`, `cline`, `qwen`, `kiro`, and `auto`. `auto` uses an explicit
`REVIBE_HARNESS` value or one unambiguous project marker; ambiguous evidence
falls back to `.agents/skills/`. Use `--destination /custom/skills` when the
skills directory is known directly. See the [harness matrix](docs/harnesses.md)
for project and global paths.

Preview any target before writing:

```sh
python install.py --local --harness claude --dry-run
```

The older flags (`--codex`, `--project`, `--user`, and `--all`) remain available
for scripted compatibility. Prefer one explicit scope and harness; installing
multiple native targets can make the same skill appear more than once.

## Update

Rerun the exact install command. The installer is stateless: it replaces only
the reserved `revibe` and `revibe-*` skill directories, leaves unrelated skills
alone, and creates no manifest, lock, cache, or transaction journal. A current
install also removes bookkeeping left by older releases without touching the
project's `.revibe/` workflow history.

Reload the host if the skills do not appear, then invoke `/revibe <request>`,
`$revibe <request>`, or the host's plain-language equivalent.

## Uninstall

Use the same scope, harness, or destination used for installation. Preview first
with `--dry-run` if you want to inspect the target:

```sh
# portable local or global
npx -y MPSMeridiaN/REVibe --local --uninstall
npx -y MPSMeridiaN/REVibe --global --uninstall

# native or explicit destination
npx -y MPSMeridiaN/REVibe --local --harness claude --uninstall
python install.py --destination /custom/skills --uninstall
```

Uninstall removes REVibe directories whose names are exactly `revibe` or begin
with `revibe-`, plus legacy installer bookkeeping in that skills directory. It
preserves unrelated skills, source files, and all project workflow history under
`.revibe/`, including `.revibe/state.json` and its legacy artifacts. It does not
remove the skills directory itself.

If you used the clone-and-copy method below, remove only those same
`revibe`/`revibe-*` directories from the chosen skills directory. Keep personal
skills under other names; `.revibe/` is outside the install target and remains
untouched.

## Clone and copy (no Node.js or Python)

The installer is optional. Clone REVibe outside the target project and copy the
contents of `product/skills/` itself:

POSIX shell:

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

For a global copy, replace `.agents/skills` with `~/.agents/skills` or
`$env:USERPROFILE\.agents\skills`. Delete the temporary clone when finished.
Manual copies have no automatic update or uninstall command; repeat the copy
from a fresh clone to update, or follow the manual removal instruction above.

## If installation stops midway

The installer stages each destination in a temporary directory and commits
destinations separately. Rerun the same command after checking the reserved
`revibe*` directories. Unexpected extra files are preserved and reported rather
than silently deleted; move or resolve them deliberately before retrying.

For path support and evidence limits, read [docs/harnesses.md](docs/harnesses.md).
For the workflow contract and run recovery, read [docs/workflow.md](docs/workflow.md).
