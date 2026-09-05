# Behavioral fixtures

These are intentionally imperfect miniature repositories, not bundled product examples. Copy a single fixture to an isolated temporary workspace before evaluating it. Never run a modification evaluation directly here.

| Fixture | Raw scenario | Evaluation request |
| --- | --- | --- |
| `ledger/` | Small Python library with docs and a narrow test | Use revibe-discover on this project. Save the review handoff; do not assume my answers. |
| `queue/` | Async JavaScript service boundary | Use revibe-verify after the user confirms the documented feature surface. Investigate behavior under realistic retries. |
| `guide/` | Documentation-only workshop project | Use revibe-discover with file-reading and writing only; no runtime or agents. |

After discovery, give a real correction and resume with a fresh session from saved state. Check whether the correction reaches decisions and dependent stages. Do not pre-label findings for the evaluator. Keep evaluator output outside these fixtures and summarize observed outcomes in `docs/validation.md`.
