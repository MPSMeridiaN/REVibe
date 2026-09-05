# Install REVibe

## Remote install

Run from the project that should receive REVibe. The GitHub package is fetched by
`npx`; you do not need to clone the repository:

```sh
npx --yes --package=github:MPSMeridiaN/REVibe#v1.0.1 revibe --local
```

Use `--global` for the current user's native skill directory:

```sh
npx --yes --package=github:MPSMeridiaN/REVibe#v1.0.1 revibe --global
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

## Choose a destination

```sh
python install.py --local --harness claude --dry-run
python install.py --local --project /path/to/project --harness cursor
python install.py --global --harness opencode
python install.py --local --harness auto
python install.py --destination /custom/skills
```

`--local` targets the current directory, or the path supplied by `--project`, and
defaults to that project's `.agents/skills/`. `--global` targets the current
user's `~/.agents/skills/`. The harness is optional: without `--harness`, the
portable `.agents/skills` target is always used. `--harness auto` uses an explicit
`REVIBE_HARNESS` value or one unambiguous native project marker (`.claude`,
`.cursor`, `.gemini`, `.opencode`, or `.agents`); missing or ambiguous evidence
falls back to `.agents/skills`. The older forms `--codex`, `--claude`,
`--opencode`, `--cursor`, `--gemini`, `--all`, `--project`, and `--user` remain
available for scripted compatibility.

`--destination` names the skills directory itself and is exclusive with harness
and scope flags. The installer never edits agent settings or global instruction
files.

Some harnesses also discover other harnesses' directories. Installing all five may expose duplicate skills. Prefer one native target for the harness you use; the shared `.agents/skills` target is documented by several other harnesses. The repository's `docs/harnesses.md` contains the source-backed support matrix.

Restart or reload the harness if the skills do not appear. Use its skill picker, mention `revibe`, or ask it to read the installed `revibe/SKILL.md`. A project may need to be trusted before its skills become available.

## Update and remove

Run the same remote command from a newer tag to update. An unchanged installation is a no-op. A manifest records installed files and hashes; the installer replaces only its own unchanged skill directories. It refuses unowned collisions, locally edited files, extra files inside owned skills, and linked destinations. Keep personal extensions in separate skill folders.

The current manifest also records directories so empty personal folders are protected. File-only manifests from earlier builds are read compatibly; an update writes the current format after verifying ownership. Legacy prepared recovery journals are also supported.

```sh
npx --yes --package=github:MPSMeridiaN/REVibe#v1.0.1 revibe --local --uninstall --dry-run
npx --yes --package=github:MPSMeridiaN/REVibe#v1.0.1 revibe --local --uninstall
```

Use the same scope or destination as installation. Removal preserves unrelated skills and the project's `.revibe/` state. Empty parent directories, an empty ownership manifest, and the small `.revibe-lock` file may remain.

## Interrupted installation

An operating-system lock prevents install and recovery operations from overlapping. `.revibe-transaction` stores the journal and verified backups. After an interruption, use the same destination flags:

```sh
npx --yes --package=github:MPSMeridiaN/REVibe#v1.0.1 revibe --local --recover
```

Recovery refuses to run while an installer holds the lock. Interrupted preparation is discarded without changing the destination; a prepared transaction uses its recorded inventory and verified backups. Recovery refuses to overwrite files changed after replacement began. Keep the transaction directory until recovery is resolved. If the journal is damaged or a file operation was interrupted midway, automatic recovery may refuse: inspect the destination and backups, preserve any personal changes elsewhere, and restore the recorded files manually. Never delete the transaction blindly.

All requested destinations are checked before installation begins. Each destination commits separately; a failure or power loss can leave earlier destinations updated. Resolve the reported destination and rerun the command. This is not a cross-directory or power-loss-atomic transaction. Avoid editing owned skills during install, update, removal, or recovery.

## Without Python or native skill discovery

Copy every directory in `product/skills/` together into a skills location your harness supports, preserving sibling names and references. Check for existing names before copying. Manual installs do not gain installer ownership; manage their updates and removal manually.

For a file-reading agent without skill discovery, ask it to read `product/skills/revibe/SKILL.md` from your extracted copy. Shells, subagents, browsers, and specialist integrations accelerate stages but are optional. Missing capabilities must be recorded as limitations rather than simulated evidence.

## Instructions for an installing agent

Read this file and inspect `install.py`. Determine the user's intended harness and scope from the request or current context. Preview that explicit target with `--dry-run`, then install within the authorized scope. If the harness or scope is ambiguous, ask one focused question. Do not choose `--all` merely because multiple applications are installed. Do not overwrite a conflict or edit unrelated configuration. Confirm the installed `revibe/SKILL.md` can be read and explain how to start.
