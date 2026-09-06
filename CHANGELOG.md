# Changelog

All notable REVibe releases are recorded here. The release command stays short
and floating; use a tag only when an exact historical build is required.

## [1.3.1] - 2026-09-06

### Changed

- Reworked the README as a focused product landing page with a clear pain point,
  controller-led flow, isolated-run example, install and uninstall paths, and
  direct documentation links.
- Removed two unreferenced legacy diagram assets from `docs/assets/`.
- Replaced the cached diagram path with `revibe-flow-v2.svg` so GitHub renders
  the new mobile-readable flow asset instead of a stale CDN copy.

## [Unreleased]

### Changed

- Redesigned the README run-loop infographic for readable rendering at narrow
  widths: five clear controller-loop moments, larger type, and a separate stage
  rail.

## [1.3.0] - 2026-09-06

### Changed

- `/revibe <task>` now dispatches delegated work and continues between stages
  automatically after actual review answers and verified state/handoff writes.
  User-requested pauses, pending answers, blockers, and completion remain explicit.
- Schema-2 state isolates each assignment under `.revibe/<run-id>/`, with run
  identity on worker packets and handoffs, explicit resume selection, and a
  non-destructive legacy-copy procedure.
- Review questions now require a subject, current claim, evidence references,
  impact, and one decision; subagent capability discovery must result in an
  actual dispatch for every substantive stage lane.
- State checks cover run selection and cross-run artifact isolation; README
  visuals and install/uninstall guidance now describe the same continuous loop.
- Uninstall now removes only exact shipped REVibe skill names, preserving unknown
  third-party `revibe-*` directories as well as unrelated skills.
- Updates use the same ownership boundary and no longer remove unknown prefixed
  directories.
- Releases now use the semantic version from `VERSION` (`v1.3.0` for this
  update), with the matching changelog section, tested ZIP, and checksum.
- CI creates or updates that versioned release after validation; commit-hash
  releases are retired automatically while historical semantic versions remain.
- Every workflow stage now uses a controller-led delegation loop: bounded worker
  assignments, verified result packets, focused follow-ups, and user review.
- Handoffs now retain controller checkpoints for partial work, evidence checks,
  feedback, and the next owning stage without changing the state schema.
- User feedback that requires work reruns the affected scope before completion;
  router review reuses the stage's review cycle instead of duplicating questions.
- Review guidance handles asynchronous answers and permitted plain-text fallback
  explicitly while preserving the final open-ended addition question.
- README and workflow documentation explain the controller loop with a shorter
  introduction, installation path, and clearer continuation guidance.

## [1.2.0] - 2026-09-06

### Changed

- Distributed skills now discover user-question tools by capability and schema
  across harnesses, use them for every stage review when available, present
  recommended choices with tradeoffs, finish with an open-ended addition check,
  and state the exact command for continuing to the next stage.
- Workflow and harness documentation now describe the question sequence,
  capability-based discovery, and continuation guidance.

## [1.1.0] - 2026-09-05

### Added

- Harness coverage for GitHub Copilot, Cline, Qwen Code, Kiro, Amp, and Warp.
- Native installer targets: `--copilot`, `--cline`, `--qwen`, and `--kiro`.
- A README support summary and an evidence-backed project/global path matrix.

### Changed

- The installer now validates all nine native target families in distribution
  tests while keeping `.agents/skills` as the portable default.

## [1.0.5] - 2026-09-05

### Added

- A documented clone-and-copy installation path for users who do not want Node.js
  or Python.
- Release changelog packaging for both npm and the standalone archive.

### Changed

- The installer is fully stateless. It no longer creates manifests, locks,
  journals, caches, or other persistent installer bookkeeping.
- `.agents/skills/` stays product-only: exactly the 11 REVibe skill directories,
  with unrelated skill names preserved.
- Older installer bookkeeping is cleaned up on the next successful install.
- README and installation guidance now distinguish installer state from the
  workflow's optional `.revibe/` runtime state.

### Trade-off

- There is no automatic recovery journal after a process or power interruption.
  Rerun the install after inspecting any partially updated `revibe*` directory.

## [1.0.4] - 2026-09-05

- Moved installer bookkeeping outside the harness skill directory. Superseded by
  the stateless installer in 1.0.5.

## [1.0.3] - 2026-09-05

- Made the GitHub install command float with the repository's default branch.
- Fixed macOS path handling and CI coverage.

## [1.0.2] - 2026-09-05

- Shortened the remote GitHub install command.
- Fixed cross-platform destination handling.

## [1.0.1] - 2026-09-05

- Polished installer defaults and release documentation.

## [1.0.0] - 2026-09-05

- Initial public REVibe release.

[Unreleased]: https://github.com/MPSMeridiaN/REVibe/compare/v1.3.1...HEAD
[1.3.1]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.3.1
[1.3.0]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.3.0
[1.2.0]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.2.0
[1.1.0]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.1.0
[1.0.5]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.5
[1.0.4]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.4
[1.0.3]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.3
[1.0.2]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.2
[1.0.1]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.1
[1.0.0]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.0
