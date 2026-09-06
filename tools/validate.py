"""Validate product discovery, local links, and distribution boundaries."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import install

RUN_ID_PATTERN = re.compile(r"[a-z0-9][a-z0-9-]{0,79}\Z")
EXPECTED_TEMPLATE_RUN = {
    "id": "new-run",
    "request": "Describe the requested work",
    "status": "active",
}


def validate(root: Path = ROOT) -> list[str]:
    errors = []
    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        package = json.loads((root / "package.json").read_text(encoding="utf-8"))
        if version != install.VERSION or package.get("version") != version:
            errors.append("Release version metadata is inconsistent")
        if package.get("bin", {}).get("revibe") != "bin/revibe.mjs":
            errors.append("npm launcher metadata is invalid")
        if "product" not in package.get("files", []):
            errors.append("npm package does not include the product")
    except (OSError, ValueError, AttributeError) as exc:
        errors.append(f"Invalid release metadata: {exc}")
    skills = root / "product" / "skills"
    try:
        manifest = install.source_manifest(skills)
    except (install.Conflict, OSError) as exc:
        return [str(exc)]
    for name in manifest["skills"]:
        path = skills / name / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
        if not match:
            errors.append(f"{path}: missing frontmatter")
            continue
        fields = dict(re.findall(r"^([a-z_-]+):\s*(.+)$", match[1], re.M))
        if fields.get("name") != name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append(f"{path}: invalid skill name")
        if not 1 <= len(fields.get("description", "")) <= 1024:
            errors.append(f"{path}: invalid description")
    template = skills / "revibe" / "references" / "state-template.json"
    try:
        state = json.loads(template.read_text(encoding="utf-8"))
        if state["schema_version"] != 2 or state["revision"] != 0:
            errors.append("Unexpected initial state schema/revision")
        run = state.get("run")
        if run != EXPECTED_TEMPLATE_RUN:
            errors.append("Unexpected initial run metadata")
        run_id = run.get("id") if isinstance(run, dict) else None
        if not isinstance(run_id, str) or RUN_ID_PATTERN.fullmatch(run_id) is None:
            errors.append("Invalid initial run ID")
        for stage, record in state["stages"].items():
            if "revibe-" + stage not in manifest["skills"]:
                errors.append(f"State references missing skill: {stage}")
            if record["status"] != "pending" or record["input_revision"] != 0:
                errors.append(f"Initial stage is not pending: {stage}")
            if run_id is not None and record.get("artifact") != f".revibe/{run_id}/handoffs/{stage}.md":
                errors.append(f"Initial stage artifact is not run-scoped: {stage}")
            if any(dep not in {"stage:" + key for key in state["stages"]} for dep in record.get("depends_on", [])):
                errors.append(f"Unknown dependency: {stage}")
        if state["next_stage"] not in state["stages"]:
            errors.append("Unknown initial next stage")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"Invalid state template: {exc}")
    # Check actual filesystem targets, including references shared between skills.
    documents = [root / "README.md", root / "INSTALL.md", root / "CONTRIBUTING.md"]
    documents += list((root / "docs").rglob("*.md")) + list(skills.rglob("*.md"))
    for path in documents:
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#") or target.startswith("mailto:"):
                continue
            target = target.split("#")[0]
            if not (path.parent / target).exists():
                errors.append(f"{path.relative_to(root)}: broken link {target}")
        if path.is_relative_to(skills):
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if "://" not in target and not target.startswith("#"):
                    resolved = (path.parent / target.split("#")[0]).resolve()
                    if not resolved.is_relative_to(skills.resolve()):
                        errors.append(f"Product depends on repository-only resource: {path}: {target}")
    return errors


if __name__ == "__main__":
    failures = validate()
    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        raise SystemExit(1)
    print("Product discovery, state template, and local links validated.")
