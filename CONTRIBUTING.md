# Develop REVibe

`product/skills/` is the installable workflow. `install.py`, `bin/revibe.mjs`,
`package.json`, `VERSION`, `INSTALL.md`, `CHANGELOG.md`, and `LICENSE` make up
the remote and archive installers. Everything in `tests/`, `tools/`, `docs/`,
and `.github/` serves development, validation, or repository presentation and
is excluded from the user package.

Use Python 3.10+; development checks use the standard library:

```sh
python -m unittest discover -s tests -v
python tools/validate.py
python tools/package.py
npm pack --dry-run
```

The archive is written to `dist/revibe.zip` with `dist/SHA256SUMS`. Packaging uses sorted paths and fixed archive timestamps. Extract it and run its installer into a temporary destination before distributing. CI defines the same checks on Windows, Linux, and macOS; a workflow definition is not proof those remote jobs have run.

For a saved run, `python tools/check_state.py /path/to/project --run <run-id>` checks run identity, state references, dependency cycles, recorded decision feedback, and handoff revision consistency. Omit `--run` only when there is one unambiguous run; `--legacy` checks the old `.revibe/state.json` without migration. It is a read-only development aid, not a required workflow runtime and not proof that the user actually gave the recorded approval.

## Automatic releases

Every push to `main` runs the complete validation matrix, then publishes or
updates the semantic-version release named `v<VERSION>` with the tested
Ubuntu/Python 3.12 archive, checksum, and matching changelog section. Other
branches, pull requests, and manual validation runs do not publish. Failed
checks prevent publication; rerun the failed workflow after resolving
infrastructure problems.

When behavior changes, choose the next version using SemVer: patch for fixes,
minor for backward-compatible capabilities, and major for breaking contracts.
Update `VERSION`, `package.json`, `install.py`, and the matching dated
`CHANGELOG.md` section in the same commit. Keep `## [Unreleased]` for work not
yet assigned to a release. The bot creates the tag and release; no manual tag
or release command is needed. Repeated pushes at the same version update that
version's release assets and notes.

Publishing first creates a draft, attaches both verified assets, then publishes.
A retry resumes the draft or updates the same version. Obsolete commit-hash
releases are removed automatically; historical semantic versions remain. The
install command continues to follow `main`; a release ZIP pins the exact
validated commit. The workflow uses the repository's built-in token with
`contents: write` only in the release job; no additional secret is required.

## Changes worth making

Keep one canonical workflow. Give each stage a distinct question, concrete evidence requirements, a durable handoff, and a user review gate. Load prior findings instead of re-investigating without cause. Add deterministic scripts only where they improve a fragile operation; do not turn the instruction suite into a mandatory runtime framework.

When changing the state contract, update its template and downstream consumers together. Define compatibility and recovery behavior. Test correction propagation and session resumption, not just the presence of headings. Keep generated state and experiment output out of the product.

Installer changes need regression coverage for reserved-namespace ownership,
stateless cleanup, collisions, linked paths, and interrupted writes. Never test
against your real global skills directory. Use temporary destinations and verify
that only the 11 product skill directories remain. A new harness needs primary
documentation for its discovery paths and an honest distinction between path
verification and live harness execution.

## Behavioral evaluation

Use an isolated repository fixture and a fresh agent with the installed skill, the user request, and raw fixture files. Do not give the evaluator the expected answer. Cover a small library, a stateful service, and a documentation-only project across full and limited tool capability. Inspect actual output for provenance, correction handling, pending reviews, appropriate delegation, and honest uncertainty. Capture the scope and result in `docs/validation.md` without claiming that simulated cases prove arbitrary real-world reliability.

The editable infographics are plain SVG in `docs/assets/`. Keep labels legible at README width and verify rendered output after changes. `tools/render-diagrams.cjs` optionally renders PNG previews using a supplied `sharp` module path; this visual aid is outside the Python checks and product package. Favor a few diagrams that explain behavior over decorative assets.
