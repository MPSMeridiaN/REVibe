#!/usr/bin/env python3
"""Install the canonical REVibe skills. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile

VERSION = "1.1.0"
SOURCE = Path(__file__).resolve().parent / "product" / "skills"
DIRECTORY_HASH = hashlib.sha256(b"directory").hexdigest()
PATHS = {
    "codex": ".agents/skills",
    "copilot": ".github/skills",
    "claude": ".claude/skills",
    "opencode": ".opencode/skills",
    "cursor": ".cursor/skills",
    "gemini": ".gemini/skills",
    "cline": ".cline/skills",
    "qwen": ".qwen/skills",
    "kiro": ".kiro/skills",
}
GLOBAL_PATHS = {
    "codex": ".agents/skills",
    "copilot": ".copilot/skills",
    "claude": ".claude/skills",
    "opencode": ".config/opencode/skills",
    "cursor": ".cursor/skills",
    "gemini": ".gemini/skills",
    "cline": ".cline/skills",
    "qwen": ".qwen/skills",
    "kiro": ".kiro/skills",
}
HARNESS_MARKERS = {
    "codex": ".agents",
    "copilot": ".github/skills",
    "claude": ".claude",
    "opencode": ".opencode",
    "cursor": ".cursor",
    "gemini": ".gemini",
    "cline": ".cline",
    "qwen": ".qwen",
    "kiro": ".kiro",
}


class Conflict(Exception):
    pass


def check_path(path: Path) -> None:
    """Reject symlinks/junctions before resolving or touching a destination."""
    for part in (path, *path.parents):
        try:
            attributes = part.lstat()
        except FileNotFoundError:
            continue
        linked = stat.S_ISLNK(attributes.st_mode) or getattr(attributes, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        # macOS exposes /var (and sometimes /tmp) as root-level aliases to
        # /private/var and /private/tmp. These OS aliases are safe; a link
        # anywhere below the filesystem root is still an unsafe destination.
        system_alias = os.name != "nt" and part.parent == Path(part.anchor)
        if linked and not system_alias:
            raise Conflict(f"Linked path is not supported: {part}")


def normalized(path: Path) -> Path:
    check_path(path)
    return path.resolve()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(directory: Path) -> dict[str, str]:
    check_path(directory)
    if not directory.is_dir():
        raise Conflict(f"Expected directory: {directory}")
    result = {}
    for path in sorted(directory.rglob("*")):
        check_path(path)
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = digest(path)
        elif path.is_dir():
            result[path.relative_to(directory).as_posix() + "/"] = DIRECTORY_HASH
        else:
            raise Conflict(f"Unsupported filesystem entry: {path}")
    return result


def validate_manifest(value: dict) -> dict:
    if not isinstance(value, dict) or value.get("format") not in (1, 2) or not isinstance(value.get("skills"), dict):
        raise Conflict("Unknown installation manifest format")
    for name, files in value["skills"].items():
        if not isinstance(name, str) or not name.startswith("revibe") or any(
            c not in "abcdefghijklmnopqrstuvwxyz0123456789-" for c in name
        ):
            raise Conflict("Unsafe skill name in manifest")
        if not isinstance(files, dict) or "SKILL.md" not in files:
            raise Conflict(f"Invalid inventory: {name}")
        for filename, checksum in files.items():
            if (not isinstance(filename, str) or "\\" in filename or ":" in filename
                    or filename.startswith("/") or any(p in ("", ".", "..") for p in filename.rstrip("/").split("/"))
                    or filename.endswith("//")):
                raise Conflict("Unsafe file name in manifest")
            if not isinstance(checksum, str) or len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum):
                raise Conflict("Invalid checksum in manifest")
            if filename.endswith("/") and checksum != DIRECTORY_HASH:
                raise Conflict("Invalid directory checksum in manifest")
    if value["format"] == 1:
        # File paths prove the nonempty parent directories in legacy inventories.
        # Empty directories remain unowned unless explicitly recorded.
        skills = {}
        for name, files in value["skills"].items():
            expanded = dict(files)
            for filename in files:
                parts = filename.rstrip("/").split("/")
                for end in range(1, len(parts)):
                    expanded["/".join(parts[:end]) + "/"] = DIRECTORY_HASH
            skills[name] = expanded
        return {"format": 2, "skills": skills}
    return value


def source_manifest(source: Path = SOURCE) -> dict:
    check_path(source)
    if not source.is_dir():
        raise Conflict(f"Product missing: {source}")
    skills = {}
    for path in sorted(source.iterdir()):
        check_path(path)
        if not path.is_dir():
            raise Conflict(f"Unexpected product entry: {path}")
        skills[path.name] = inventory(path)
    if not skills:
        raise Conflict("Product has no skills")
    return validate_manifest({"format": 2, "skills": skills})


LEGACY_STATE_FILES = (".revibe-install.json", ".revibe-lock")
LEGACY_TRANSACTION = ".revibe-transaction"


def is_revibe_skill(name: str) -> bool:
    return name == "revibe" or name.startswith("revibe-")


def remove_tree(path: Path, parent: Path) -> None:
    check_path(path)
    if path.parent.resolve() != parent.resolve():
        raise Conflict(f"Removal outside intended parent: {path}")
    inventory(path)
    shutil.rmtree(path)


def cleanup_persistent_state(root: Path) -> bool:
    """Remove bookkeeping created by older installers; current installs create none."""
    changed = False
    for name in LEGACY_STATE_FILES:
        path = root / name
        if path.exists():
            check_path(path)
            if not path.is_file():
                raise Conflict(f"Expected legacy state file: {path}")
            path.unlink()
            changed = True

    transaction = root / LEGACY_TRANSACTION
    if transaction.exists():
        remove_tree(transaction, root)
        changed = True

    adjacent_state = root.parent / ".revibe" / root.name
    if adjacent_state.exists():
        remove_tree(adjacent_state, adjacent_state.parent)
        changed = True
        if adjacent_state.parent.exists() and not any(adjacent_state.parent.iterdir()):
            adjacent_state.parent.rmdir()
    return changed


def preflight(root: Path, new: dict) -> None:
    check_path(root)
    if root.exists() and not root.is_dir():
        raise Conflict(f"Not a directory: {root}")
    if not root.exists():
        return

    for child in root.iterdir():
        if is_revibe_skill(child.name):
            check_path(child)
            if not child.is_dir():
                raise Conflict(f"Expected REVibe skill directory: {child}")

    for name, files in new["skills"].items():
        path = root / name
        check_path(path)
        if path.exists():
            existing = inventory(path)
            unexpected = sorted(set(existing) - set(files))
            if unexpected:
                raise Conflict(
                    f"Existing REVibe skill contains extra files; preserve or move them before retrying: {path}"
                )


def apply(root: Path, new: dict, source: Path = SOURCE, uninstall: bool = False) -> str:
    root = normalized(root)
    source = normalized(source)
    new = validate_manifest(new)
    preflight(root, new)

    if uninstall:
        changed = False
        if root.exists():
            for child in sorted(root.iterdir(), key=lambda path: path.name):
                if is_revibe_skill(child.name):
                    remove_tree(child, root)
                    changed = True
        changed = cleanup_persistent_state(root) or changed
        return f"Uninstalled: {root}"

    root.parent.mkdir(parents=True, exist_ok=True)
    changed = False
    with tempfile.TemporaryDirectory(prefix=".revibe-", dir=str(root.parent)) as temporary:
        staged_root = Path(temporary) / "skills"
        staged_root.mkdir()
        for name, files in new["skills"].items():
            source_skill = source / name
            if inventory(source_skill) != files:
                raise Conflict("Product changed before preparation")
            shutil.copytree(source_skill, staged_root / name)
            if inventory(staged_root / name) != files:
                raise Conflict("Product changed while preparing installation")

        root.mkdir(parents=True, exist_ok=True)
        desired_names = set(new["skills"])
        for child in sorted(root.iterdir(), key=lambda path: path.name):
            if is_revibe_skill(child.name) and child.name not in desired_names:
                remove_tree(child, root)
                changed = True

        for name, files in new["skills"].items():
            destination = root / name
            if destination.exists() and inventory(destination) == files:
                continue
            if destination.exists():
                remove_tree(destination, root)
                changed = True
            os.replace(staged_root / name, destination)
            changed = True

    changed = cleanup_persistent_state(root) or changed
    return f"{'Installed' if changed else 'Already current'}: {root}"


def detect_harness(base: Path, scope: str) -> str:
    """Choose a native target only when the project gives one clear signal."""
    requested = os.environ.get("REVIBE_HARNESS", "").strip().lower()
    if requested:
        if requested not in PATHS:
            raise Conflict("REVIBE_HARNESS must be one of: " + ", ".join(PATHS))
        return requested
    if scope == "local":
        matches = [harness for harness, marker in HARNESS_MARKERS.items() if (base / marker).is_dir()]
        if len(matches) == 1:
            return matches[0]
    return "codex"


def destinations(args: argparse.Namespace) -> list[Path]:
    modern_scope = getattr(args, "local", False) or getattr(args, "global_scope", False)
    requested_harness = getattr(args, "harness", None)
    legacy_harnesses = [h for h in PATHS if getattr(args, h, False)]
    if args.destination:
        if (args.all or legacy_harnesses or args.project or args.user or modern_scope or requested_harness):
            raise Conflict("--destination cannot be combined with harness or scope flags")
        return [Path(args.destination).expanduser().absolute()]
    if modern_scope or requested_harness:
        if args.all or legacy_harnesses:
            raise Conflict("Use --harness with --local or --global, not legacy harness flags")
        if not modern_scope:
            raise Conflict("--harness requires --local or --global")
        if args.global_scope and args.project:
            raise Conflict("--global cannot be combined with --project")
        if args.local and args.user:
            raise Conflict("--local cannot be combined with --user")
        scope = "local" if args.local else "global"
        base = Path(args.project).expanduser().absolute() if args.project else (
            Path.cwd() if scope == "local" else Path.home()
        )
        harness = requested_harness or "codex"
        if harness == "auto":
            harness = detect_harness(base, scope)
        relative = PATHS[harness] if scope == "local" else GLOBAL_PATHS[harness]
        if harness == "opencode" and scope == "global":
            config = Path(os.environ.get("XDG_CONFIG_HOME", str(base / ".config"))).expanduser()
            if not config.is_absolute():
                raise Conflict("XDG_CONFIG_HOME must be absolute")
            return [config / "opencode" / "skills"]
        return [base / relative]
    selected = list(PATHS) if args.all else legacy_harnesses
    if args.all and any(getattr(args, h) for h in PATHS):
        raise Conflict("Choose --all or individual harness flags")
    if not selected:
        raise Conflict("Select --local, --global, a legacy harness flag, --all, or --destination PATH")
    base = Path(args.project).expanduser().absolute() if args.project else Path.home()
    roots = []
    for harness in selected:
        relative = PATHS[harness] if args.project else GLOBAL_PATHS[harness]
        if harness == "opencode" and not args.project:
            config = Path(os.environ.get("XDG_CONFIG_HOME", str(base / ".config"))).expanduser()
            if not config.is_absolute():
                raise Conflict("XDG_CONFIG_HOME must be absolute")
            roots.append(config / "opencode" / "skills")
        else:
            roots.append(base / relative)
    return list(dict.fromkeys(roots))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=f"REVibe {VERSION}")
    for harness in PATHS:
        parser.add_argument(f"--{harness}", action="store_true")
    parser.add_argument("--all", action="store_true", help="Install to all configured native locations")
    parser.add_argument("--harness", choices=("auto", *PATHS), help="Native target; omit for portable .agents/skills, or use auto for evidence-based adaptation")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--local", action="store_true", help="Install in the current project (the default portable target is .agents/skills)")
    scope.add_argument("--global", dest="global_scope", action="store_true", help="Install for the current user")
    legacy_scope = parser.add_mutually_exclusive_group()
    legacy_scope.add_argument("--project", metavar="PATH", help="Legacy form: install inside this project")
    legacy_scope.add_argument("--user", action="store_true", help="Legacy form: install for current user")
    parser.add_argument("--destination", metavar="PATH", help="Explicit skills directory for another harness")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Check and print changes without writing")
    args = parser.parse_args(argv)
    try:
        roots = destinations(args)
        new = source_manifest()
        for root in roots:
            preflight(root, new)  # All destinations checked before any mutation.
        for root in roots:
            if args.dry_run:
                action_text = "uninstall REVibe skills from" if args.uninstall else f"install {len(new['skills'])} skills to"
                print(f"Would {action_text}: {root}")
            else:
                print(apply(root, new, uninstall=args.uninstall))
        return 0
    except (Conflict, OSError) as exc:
        print(f"REVibe: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
