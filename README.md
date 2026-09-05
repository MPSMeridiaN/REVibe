# REVibe

### Understand the project. Then change it.

The code runs. The docs sound right. Nobody knows what a small change will break.

REVibe gives your coding agent a workflow for reconstructing what exists, testing what is true, and aligning the result with what you actually want.

![REVibe journey: inspect the existing system, confirm the target, execute and verify. Evidence and user decisions travel between stages.](docs/assets/journey.svg)

## Install from the repository URL

Run this from the project that should receive REVibe. No repository clone is needed:

```sh
npx --yes --package=github:MPSMeridiaN/REVibe#v1.0.0 revibe --local
```

For a user-wide installation, use `--global` instead:

```sh
npx --yes --package=github:MPSMeridiaN/REVibe#v1.0.0 revibe --global
```

The remote launcher requires Node.js 18+ and Python 3.10+. Add `--harness claude`,
`--harness cursor`, `--harness gemini`, `--harness opencode`, or `--harness codex`
when the target is known. Without an explicit harness, REVibe adapts only when the
project has one clear native marker; otherwise it uses the portable `.agents/skills`
location. Rerun the same command to reinstall or update safely.

For a downloaded release archive or a development checkout, run from the target
project and invoke the extracted script directly:

```sh
python /path/to/revibe/install.py --local
python /path/to/revibe/install.py --global
```

Then ask your agent:

> Use revibe to understand this project. Start with discovery, show me what you found, and help me decide what should change.

## What is installed

The product is **11 skills and their shared reference files** under `product/skills/`.
The installer copies them into the selected harness directory and records ownership
so repeat installs, updates, removal, and recovery do not duplicate or overwrite
unrelated skills. No service, account, MCP server, or background process is added.

The repository also contains tests, documentation, packaging, and release tooling;
those are development resources and are not installed into a project.

[Installation, removal, and recovery →](INSTALL.md)

## A process you can resume

| Stage | The question it resolves |
| --- | --- |
| `revibe` | Where should this run start or resume? |
| `revibe-discover` | What is here, and what does it claim to do? |
| `revibe-verify` | How does it actually behave, and why? |
| `revibe-align` | What do you want it to become? |
| `revibe-design` | What does that target mean across the system? |
| `revibe-strategize` | Which solution and tradeoffs should we accept? |
| `revibe-plan` | What work can be executed in what order? |
| `revibe-implement` | How do we coordinate changes without drifting? |
| `revibe-validate` | What survives attempts to break it? |
| `revibe-cohere` | Does the result make sense as one product? |
| `revibe-finalize` | Can someone build, use, and maintain it? |

Each stage reviews meaningful findings and choices with you. You can confirm, correct, reject, defer, or give a custom direction. Recommendations become intent only when you accept them.

Evidence and decisions live in your project's `.revibe/` directory. A fresh session can resume there. If a decision changes, dependent work becomes stale and gets reconciled before it is reused.

<details>
<summary>What makes the workflow different?</summary>

- **Claims stay distinct from evidence.** Documentation, source inspection, tests, and runtime observations retain their provenance and limitations.
- **Orchestration adapts to the harness.** Independent investigations can use agents and specialist tools; a single agent can run the same stages sequentially.
- **Execution stays connected to intent.** Design, implementation tasks, and verification trace back to reviewed decisions.
- **Confidence has a scope.** A passing build is useful evidence, not proof that every feature works.

![Handoff contract: evidence, user decisions, and dependencies produce a reviewed stage handoff. Corrections invalidate dependent work.](docs/assets/handoff.svg)

</details>

[Workflow and state](docs/workflow.md) · [Harness support and research](docs/harnesses.md) · [Development and validation](CONTRIBUTING.md) · [MIT license](LICENSE)

REVibe is an instruction-based engineering workflow, not a guarantee of correctness. See the [validation record](docs/validation.md) for what has actually been exercised.
