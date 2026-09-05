# Changelog

All notable REVibe releases are recorded here. The release command stays short
and floating; use a tag only when an exact historical build is required.

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

[1.0.5]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.5
[1.0.4]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.4
[1.0.3]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.3
[1.0.2]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.2
[1.0.1]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.1
[1.0.0]: https://github.com/MPSMeridiaN/REVibe/releases/tag/v1.0.0
