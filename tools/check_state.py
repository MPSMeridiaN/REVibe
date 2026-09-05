"""Read-only development checker for a saved REVibe state and its handoffs."""
from pathlib import Path
import argparse
import json
import re

COLLECTIONS = ("features", "evidence", "decisions", "risks", "questions", "constraints", "relationships", "assumptions", "tasks")
STAGES = ("discover", "verify", "align", "design", "strategize", "plan", "implement", "validate", "cohere", "finalize")
STATUSES = {"pending", "in_progress", "awaiting_review", "complete", "stale"}


def check(state: dict, project: Path | None = None) -> list[str]:
    errors = []
    if not isinstance(state, dict):
        return ["State must be an object"]
    if state.get("schema_version") != 1:
        errors.append("Unsupported schema_version")
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
        if artifact != f".revibe/handoffs/{name}.md":
            errors.append(f"stage:{name}: unexpected artifact path")
        elif project is not None and record.get("status") in {"complete", "awaiting_review"}:
            path = project / artifact
            if not path.is_file():
                errors.append(f"stage:{name}: missing handoff")
            else:
                header = dict(re.findall(r"^- (status|input_revision|output_revision|next_stage): (.+)$", path.read_text(encoding="utf-8"), re.M))
                if header.get("output_revision") != str(record.get("output_revision")):
                    errors.append(f"stage:{name}: handoff revision mismatch")
                if header.get("input_revision") != str(record.get("input_revision")):
                    errors.append(f"stage:{name}: handoff input mismatch")
                if header.get("status") != record.get("status"):
                    errors.append(f"stage:{name}: handoff status mismatch")
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
    args = parser.parse_args()
    try:
        failures = check(json.loads((args.project / ".revibe" / "state.json").read_text(encoding="utf-8")), args.project)
    except (OSError, ValueError) as exc:
        failures = [str(exc)]
    print("\n".join(failures) if failures else "State references and handoffs are coherent.")
    raise SystemExit(bool(failures))
