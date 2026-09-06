# Validation record

This record separates checks run against REVibe from claims about arbitrary
projects. Passing these checks does not guarantee that an executing agent will
make every project correct.

## Automated checks

- `python -m unittest discover -s tests -v`: installer, stateless update/cleanup,
  workflow state, and distribution regression coverage.
- `python tools/validate.py`: skill metadata, state template, product links,
  and release metadata.
- `python tools/package.py`: reproducible standalone Python archive.
- `npm pack --dry-run`: npm projection contains the launcher, installer, and
  product only.

The distribution tests build the archive twice, compare bytes, extract it
outside the repository, install and uninstall from the extracted copy, and
exercise all nine native target families in an isolated project. The product
projection excludes tests, tools, documentation, and development prompts.

## Remote install acceptance

The release gate is the remote command documented in the README:

```sh
npx -y MPSMeridiaN/REVibe --local
npx -y MPSMeridiaN/REVibe --global
```

Acceptance checks use a clean project and a fresh temporary user directory. Each
run confirms that the agent-facing package can be fetched from GitHub without a
manual clone, the requested scope is respected, the selected harness directory
contains all 11 skills and no direct files or installer state, the shared
references are readable, a repeat install is a no-op, and no duplicate skill
tree is created. Explicit harness targets are checked across the nine native
targets; auto-detection is checked with representative unambiguous markers and
an ambiguous-marker fallback. The documented
clone-and-copy path is also smoke-tested as a product-only install without
Node.js or Python. The shared `.agents/skills` claims for Amp and Warp are
documentation-verified but are not live application tests in CI.

## Behavioral scope

The fixtures under `tests/fixtures/` cover a small Python library, an
asynchronous queue, and a documentation-only project. They exist to exercise
the workflow's evidence, review, and capability-limit contracts; their outputs
are not treated as proof of arbitrary real-world reliability.

## Controller contract review — 2026-09-06

An independent agent reviewed the router and shared protocol against six
simulated situations: a missing test artifact despite a worker's `done` result;
changed upstream intent during active writes; resumption from partial artifacts;
plain-text review without subagents; an unrelated revision increase; and
substantive changes requested in the final addition answer.

The review kept incomplete evidence in progress, required stopping obsolete
writers before replacement, resumed only from durable evidence, accepted actual
plain-text answers, reconciled revision age by dependency impact, and reran
changed scope before completion. This was an instruction-level scenario review,
not a live multi-agent execution or proof of every harness's cancellation behavior.
Worker cancellation remains harness-dependent; replacement writes must wait
until ownership is resolved.

## Known limits

- Skill discovery depends on the executing harness and agent following the
  installed instructions.
- Live execution inside every native harness application is not part of the
  automated suite.
- Multi-target installation commits each destination separately rather than as
  one cross-directory transaction.
- The installer keeps no persistent recovery journal. A process or power loss
  during the final update may require inspecting the reserved `revibe*` entries
  and rerunning the command.
- The installer owns the reserved `revibe` / `revibe-*` namespace; personal
  skills should use another name.
