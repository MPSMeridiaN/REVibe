"""Read-only development checker for a saved REVibe state and its handoffs."""
from pathlib import Path
import argparse
import json
import os
import re

COLLECTIONS = ("features", "evidence", "decisions", "risks", "questions", "constraints", "relationships", "assumptions", "tasks")
STAGES = ("discover", "verify", "align", "design", "strategize", "plan", "implement", "validate", "cohere", "finalize")
STATUSES = {"pending", "in_progress", "awaiting_review", "complete", "stale"}
RUN_STATUSES = {"active", "paused", "blocked", "complete"}
RUN_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
HANDOFF_STATUSES = {"complete", "awaiting_review"}
HANDOFF_HEADER_PATTERN = re.compile(r"^- ([a-z_]+): (.+)$", re.M)


def valid_run_id(run_id: object) -> bool:
    """Return whether *run_id* is safe to use as a single run directory name."""
    return isinstance(run_id, str) and RUN_ID_PATTERN.fullmatch(run_id) is not None


def _same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def _resolved(path: Path) -> Path:
    return path.resolve(strict=False)


def _safe_legacy_artifact(project: Path, artifact: str) -> tuple[Path | None, str | None]:
    """Resolve a schema1 handoff without following it outside .revibe."""
    try:
        revibe = project / ".revibe"
        revibe_real = _resolved(revibe)
        path = project / artifact
        path_real = _resolved(path)
        if not path_real.is_relative_to(revibe_real):
            return None, "handoff path escapes .revibe"
        return path, None
    except (OSError, RuntimeError, ValueError):
        return None, "handoff path cannot be resolved safely"


def _safe_run_artifact(project: Path, artifact: str, run_id: str, stage: str) -> tuple[Path | None, str | None]:
    """Resolve a schema2 handoff and reject run or symlink crossovers."""
    try:
        revibe = project / ".revibe"
        run_dir = revibe / run_id
        handoffs = run_dir / "handoffs"
        path = project / artifact

        revibe_real = _resolved(revibe)
        run_real = _resolved(run_dir)
        expected_run = revibe_real / run_id
        if not _same_path(run_real, expected_run):
            return None, "handoff path escapes the selected run"

        handoffs_real = _resolved(handoffs)
        expected_handoffs = expected_run / "handoffs"
        if not _same_path(handoffs_real, expected_handoffs):
            return None, "handoff path escapes the selected run"

        path_real = _resolved(path)
        expected_path = expected_handoffs / f"{stage}.md"
        if not _same_path(path_real, expected_path):
            return None, "handoff path escapes the selected run"
        return path, None
    except (OSError, RuntimeError, ValueError):
        return None, "handoff path cannot be resolved safely"


def _safe_run_state(project: Path, run_id: str) -> tuple[Path | None, str | None]:
    """Resolve a selected schema2 state without following it into another run."""
    try:
        revibe = project / ".revibe"
        run_dir = revibe / run_id
        state_path = run_dir / "state.json"
        revibe_real = _resolved(revibe)
        run_real = _resolved(run_dir)
        expected_run = revibe_real / run_id
        if not _same_path(run_real, expected_run):
            return None, "state path escapes the selected run"
        state_real = _resolved(state_path)
        if not _same_path(state_real, expected_run / "state.json"):
            return None, "state path escapes the selected run"
        return state_path, None
    except (OSError, RuntimeError, ValueError):
        return None, "state path cannot be resolved safely"


def _safe_legacy_state(project: Path) -> tuple[Path | None, str | None]:
    try:
        revibe = project / ".revibe"
        state_path = revibe / "state.json"
        revibe_real = _resolved(revibe)
        state_real = _resolved(state_path)
        if not state_real.is_relative_to(revibe_real) or state_real.parent != revibe_real:
            return None, "legacy state path escapes .revibe"
        return state_path, None
    except (OSError, RuntimeError, ValueError):
        return None, "legacy state path cannot be resolved safely"


def discover_run_ids(project: Path) -> list[str]:
    """Return run directory names that contain a state.json, in stable order."""
    revibe = project / ".revibe"
    if not revibe.is_dir():
        return []
    try:
        return sorted(
            child.name
            for child in revibe.iterdir()
            if child.is_dir() and (child / "state.json").is_file()
        )
    except OSError:
        return []


def select_state_path(project: Path, run_id: str | None = None, legacy: bool = False) -> tuple[Path | None, str | None, list[str]]:
    """Select a state file for the checker CLI.

    The returned tuple is ``(path, selected_run_id, errors)``. Legacy state is
    intentionally opt-in, while one schema2 run can be selected implicitly.
    """
    if legacy:
        path, error = _safe_legacy_state(project)
        if error:
            return None, None, [error]
        if not path.is_file():
            return None, None, ["Legacy state not found at .revibe/state.json; create a run or pass a valid project"]
        return path, None, []

    if run_id is not None:
        if not valid_run_id(run_id):
            return None, None, ["Invalid run ID; use lowercase letters, digits, and hyphens (1-80 characters)"]
        path, error = _safe_run_state(project, run_id)
        if error:
            return None, run_id, [error]
        if not path.is_file():
            available = discover_run_ids(project)
            detail = f" Available runs: {', '.join(available)}." if available else ""
            return None, run_id, [f"Run '{run_id}' state not found at .revibe/{run_id}/state.json.{detail}"]
        return path, run_id, []

    run_ids = discover_run_ids(project)
    if len(run_ids) > 1:
        return None, None, [f"Multiple REVibe runs found; specify --run with one of: {', '.join(run_ids)}"]
    if len(run_ids) == 1:
        selected = run_ids[0]
        path, error = _safe_run_state(project, selected)
        if error:
            return None, selected, [error]
        if not path.is_file():
            return None, selected, [f"Run '{selected}' state is not a regular file"]
        return path, selected, []

    legacy_path, legacy_error = _safe_legacy_state(project)
    if legacy_error:
        return None, None, [legacy_error]
    if legacy_path.is_file():
        return None, None, ["Legacy state found at .revibe/state.json; pass --legacy to inspect it"]
    return None, None, ["No REVibe run state found under .revibe"]


def _validate_run_metadata(state: dict, errors: list[str], expected_run_id: str | None) -> str | None:
    run = state.get("run")
    if not isinstance(run, dict):
        errors.append("run must be an object")
        return None

    run_id = run.get("id")
    if not valid_run_id(run_id):
        errors.append("run.id must be lowercase letters, digits, and hyphens (1-80 characters)")
        run_id = None
    elif expected_run_id is not None and run_id != expected_run_id:
        errors.append(f"run.id does not match selected run '{expected_run_id}'")

    request = run.get("request")
    if not isinstance(request, str) or not request.strip():
        errors.append("run.request must be nonempty")
    if run.get("status") not in RUN_STATUSES:
        errors.append("run.status must be one of: active, paused, blocked, complete")
    return run_id


def _check_handoff(
    project: Path,
    record: dict,
    stage: str,
    artifact: str,
    run_id: str | None,
    schema_version: int,
    errors: list[str],
) -> None:
    if schema_version == 2 and run_id is not None:
        path, path_error = _safe_run_artifact(project, artifact, run_id, stage)
    else:
        path, path_error = _safe_legacy_artifact(project, artifact)
    if path_error:
        errors.append(f"stage:{stage}: {path_error}")
        return
    if path is None or not path.is_file():
        errors.append(f"stage:{stage}: missing handoff")
        return
    try:
        header = dict(HANDOFF_HEADER_PATTERN.findall(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError) as exc:
        errors.append(f"stage:{stage}: unreadable handoff ({exc})")
        return
    if schema_version == 2 and header.get("run_id") != run_id:
        errors.append(f"stage:{stage}: handoff run_id mismatch")
    if header.get("output_revision") != str(record.get("output_revision")):
        errors.append(f"stage:{stage}: handoff revision mismatch")
    if header.get("input_revision") != str(record.get("input_revision")):
        errors.append(f"stage:{stage}: handoff input mismatch")
    if header.get("status") != record.get("status"):
        errors.append(f"stage:{stage}: handoff status mismatch")


def check(state: dict, project: Path | None = None, expected_run_id: str | None = None) -> list[str]:
    errors = []
    if not isinstance(state, dict):
        return ["State must be an object"]
    schema_version = state.get("schema_version")
    if schema_version not in {1, 2}:
        errors.append("Unsupported schema_version")
        return errors
    run_id = None
    if schema_version == 2:
        run_id = _validate_run_metadata(state, errors, expected_run_id)
    elif expected_run_id is not None:
        errors.append("schema_version 1 is legacy; use --legacy for .revibe/state.json")
    revision = state.get("revision")
    if type(revision) is not int or revision < 0:
        return errors + ["revision must be a nonnegative integer"]
    stages = state.get("stages")
    if not isinstance(stages, dict) or set(stages) != set(STAGES):
        return errors + ["stages must contain the ten known stage keys"]
    if state.get("next_stage") is not None and state["next_stage"] not in STAGES:
        errors.append("Unknown next_stage")
    nodes = {}
    for name, record in stages.items():
        if not isinstance(record, dict):
            errors.append(f"stage:{name}: expected object")
            continue
        nodes["stage:" + name] = record
        if record.get("status") not in STATUSES:
            errors.append(f"stage:{name}: unknown status")
        for field in ("input_revision", "output_revision"):
            value = record.get(field)
            if type(value) is not int or not 0 <= value <= revision:
                errors.append(f"stage:{name}: invalid {field}")
        artifact = record.get("artifact")
        expected_artifact = (
            f".revibe/{run_id}/handoffs/{name}.md"
            if schema_version == 2 and run_id is not None
            else f".revibe/handoffs/{name}.md"
        )
        if artifact != expected_artifact:
            errors.append(f"stage:{name}: unexpected artifact path")
        elif project is not None and record.get("status") in {"complete", "awaiting_review"}:
            _check_handoff(project, record, name, artifact, run_id, schema_version, errors)
    for collection in COLLECTIONS:
        records = state.get(collection, [] if collection == "tasks" else None)
        if not isinstance(records, list):
            errors.append(f"{collection}: expected array")
            continue
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("id"), str):
                errors.append(f"{collection}: record needs string id")
                continue
            key = record["id"]
            if key in nodes or key.startswith("stage:"):
                errors.append(f"Duplicate or reserved id: {key}")
                continue
            nodes[key] = record
            if "status" not in record:
                errors.append(f"{key}: missing status")
            if not isinstance(record.get("source_refs", []), list):
                errors.append(f"{key}: invalid source_refs")
            if collection == "decisions" and record.get("status") == "accepted" and not record.get("user_feedback"):
                errors.append(f"{key}: accepted decision lacks user feedback")
    graph = {}
    for key, record in nodes.items():
        deps = record.get("depends_on", [])
        if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
            errors.append(f"{key}: invalid depends_on")
            continue
        graph[key] = deps
        for dep in deps:
            if dep not in nodes:
                errors.append(f"{key}: unknown dependency {dep}")
            if key.startswith("stage:") and dep.startswith("stage:") and dep[6:] in STAGES and STAGES.index(dep[6:]) >= STAGES.index(key[6:]):
                errors.append(f"{key}: forward stage dependency {dep}")
            if record.get("status") == "complete" and dep in nodes and nodes[dep].get("status") == "stale":
                errors.append(f"{key}: complete result depends on stale {dep}")
        evidence_ids = record.get("evidence_ids", [])
        if not isinstance(evidence_ids, list) or any(not isinstance(item, str) for item in evidence_ids):
            errors.append(f"{key}: invalid evidence_ids")
            evidence_ids = []
        for evidence_id in evidence_ids:
            if evidence_id not in nodes:
                errors.append(f"{key}: unknown evidence {evidence_id}")
    visited, active = set(), set()
    def visit(key):
        if key in active:
            errors.append(f"Dependency cycle at {key}")
            return
        if key in visited:
            return
        active.add(key)
        for dep in graph.get(key, []):
            visit(dep)
        active.remove(key)
        visited.add(key)
    for key in graph:
        visit(key)
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--run", dest="run_id", metavar="ID", help="select a schema2 run by ID")
    selection.add_argument("--legacy", action="store_true", help="explicitly inspect legacy .revibe/state.json")
    args = parser.parse_args()
    state_path, selected_run_id, selection_errors = select_state_path(args.project, args.run_id, args.legacy)
    if selection_errors:
        failures = selection_errors
    else:
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            failures = check(state, args.project, selected_run_id)
        except (OSError, ValueError) as exc:
            failures = [str(exc)]
    print("\n".join(failures) if failures else "State references and handoffs are coherent.")
    raise SystemExit(bool(failures))
