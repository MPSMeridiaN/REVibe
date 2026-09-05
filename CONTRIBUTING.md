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

For a saved run, `python tools/check_state.py /path/to/project` checks state references, dependency cycles, recorded decision feedback, and handoff revision consistency. It is a read-only development aid, not a required workflow runtime and not proof that the user actually gave the recorded approval.

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
