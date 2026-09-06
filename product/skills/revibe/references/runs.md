# Run identity and continuity

Read this reference before selecting, creating, or resuming a run. A run is one
user-requested assignment through the REVibe stages, not one conversation turn
or one stage. Its directory is `.revibe/<run-id>/` under the examined project.

## Select the work before reading its state

- `/revibe <new task>` starts a new run. The equivalent skill invocation or
  natural-language request in another harness has the same meaning.
- Feedback, an answer to the controller's question, or continuing the same
  assignment stays in its existing run. Do not create a run per answer or stage.
- `/revibe resume <run-id>` selects that run. “Continue” in the same conversation
  can use its already established ID after checking the directory and request.
- In a fresh session, inspect only run IDs, requests, statuses, and baselines to
  resolve an unqualified resume. One matching unfinished run can be selected;
  multiple plausible matches require a focused selection question. Never choose
  by timestamp alone, merge histories, or turn a new task into an old run because
  only one directory exists. Completed runs remain historical; a new pass gets a
  new ID unless the user explicitly reopens the old assignment.

Use a unique, readable ID such as `20260906-143000-checkout-fix-a1b2c3d4`.
IDs must match `[a-z0-9][a-z0-9-]{0,79}`. Create the directory exclusively; if it
already exists, choose a new suffix. Never overwrite or reuse it by accident.
Resolve the selected directory inside the project's `.revibe/`; reject traversal
or linked paths escaping that location. Do not maintain a global “active run”
pointer: separate sessions may own different runs.

## Initialize and persist

Copy the state template into the new run. Replace `new-run` in `run.id` and every
stage artifact path; set `run.request` to a faithful description of the task,
`run.status` to `active`, and `project.root`/`project.baseline` to the examined
checkout. The template is a shape, never a preselected run. Keep revision `0`
until the first write after initialization.

```text
.revibe/<run-id>/
  state.json
  handoffs/<stage>.md
  evidence/                 # referenced worker packets and checks, as needed
  archive/                  # superseded evidence and handoffs, as needed
```

Paths stored in state are relative to the project root. Run-owned artifacts,
temporary files, backups, evidence, and archives stay under this run directory.
Every handoff names `run_id`; every worker assignment and return packet carries
it. The controller rejects a packet or handoff from another run before merging.
Record IDs and revisions are local to a run: two runs may both have `dec.target`
and revision `4` without sharing a decision. `depends_on` resolves only inside
the selected state. Prior-run findings are historical references; importing one
requires a new local record, explicit source run/artifact, and a current-baseline
check. User acceptance in one run does not automatically approve another task.

Run status is separate from stage status:

| Run status | Meaning |
| --- | --- |
| `active` | Working or waiting for an actual review answer; continue when resolved |
| `paused` | User explicitly requested a stop/pause; save the resume point |
| `blocked` | No authorized or feasible next action until a named dependency changes |
| `complete` | Finalization is reviewed and complete; no required stage remains |

Before each next-stage dispatch or rerun, commit the revised state and handoff,
including user feedback, invalidations, outstanding work, and the next owner.
Read back the matching run ID and revisions. A failed persistence check blocks
dispatch. On a pause, stop affected workers, reconcile partial changes, and save
the current stage without declaring unfinished work complete. An explicit resume
sets the run active after revalidating its baseline and outstanding work.

Separate state does not isolate source files. Before overlapping runs edit the
same checkout, inspect known active assignments and working-tree changes. Use
separate worktrees/checkouts where supported, or serialize conflicting writes.
Record the actual checkout in each run; never let a second run silently overwrite
the first run's changes.

## Legacy schema-1 projects

`.revibe/state.json` is a legacy run, never the default destination for new work.
Keep it and its artifacts intact. To resume it with this contract, select that
legacy assignment explicitly, validate its coherent state/handoff pair, and copy
it into a fresh run directory. Set schema `2` and run metadata, remap run-owned
paths under `.revibe/` (old `runs/` logs become `evidence/`), and add `run_id` to
copied handoffs. Preserve original IDs, revisions, feedback, and statuses. Record
the migration source and evidence limits in the next checkpoint; validate copied
files before activating the new run. External source refs remain unchanged.
Never move/delete the originals, merge them into another run, or repair a
malformed legacy state by silently initializing over it. If multiple candidates
or a missing artifact prevents a supported migration, ask the user to resolve it.
