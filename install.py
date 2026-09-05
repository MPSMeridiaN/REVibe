#!/usr/bin/env python3
"""Install the canonical REVibe skills. Python 3.10+, standard library only."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys

VERSION = "1.0.3"
SOURCE = Path(__file__).resolve().parent / "product" / "skills"
MANIFEST = ".revibe-install.json"
TRANSACTION = ".revibe-transaction"
LOCK = ".revibe-lock"
DIRECTORY_HASH = hashlib.sha256(b"directory").hexdigest()
PATHS = {
    "codex": ".agents/skills",
    "claude": ".claude/skills",
    "opencode": ".opencode/skills",
    "cursor": ".cursor/skills",
    "gemini": ".gemini/skills",
}
HARNESS_MARKERS = {
    "codex": ".agents",
    "claude": ".claude",
    "opencode": ".opencode",
    "cursor": ".cursor",
    "gemini": ".gemini",
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


@contextmanager
def operation_lock(root: Path):
    """OS locks are released on process exit; recovery obeys the same lock."""
    root.mkdir(parents=True, exist_ok=True)
    path = root / LOCK
    check_path(path)
    with path.open("a+b") as stream:
        if path.stat().st_size == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise Conflict(f"Another installation or recovery is active: {root}") from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


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


def read_json(path: Path) -> dict:
    check_path(path)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise Conflict(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise Conflict(f"Expected JSON object: {path}")
    return value


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


def installed(root: Path) -> dict:
    path = root / MANIFEST
    check_path(path)
    return validate_manifest(read_json(path)) if path.exists() else {"format": 2, "skills": {}}


def preflight(root: Path, new: dict) -> dict:
    check_path(root)
    if root.exists() and not root.is_dir():
        raise Conflict(f"Not a directory: {root}")
    if (root / TRANSACTION).exists():
        raise Conflict(f"Interrupted or active operation at {root}; stop other installers, then use --recover")
    old = installed(root)
    for name, files in old["skills"].items():
        if inventory(root / name) != files:
            raise Conflict(f"Locally modified installed skill; preserve or move it before retrying: {root / name}")
    for name in new["skills"]:
        path = root / name
        check_path(path)
        if path.exists() and name not in old["skills"]:
            raise Conflict(f"Unowned skill would be overwritten: {path}")
    return old


def write_json(path: Path, data: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def remove_tree(path: Path, parent: Path) -> None:
    check_path(path)
    if path.parent.resolve() != parent.resolve():
        raise Conflict(f"Removal outside intended parent: {path}")
    inventory(path)  # Inspect all descendants for links before recursive removal.
    shutil.rmtree(path)


def _recover_locked(root: Path) -> str:
    check_path(root)
    tx = root / TRANSACTION
    check_path(tx)
    if not tx.exists():
        return f"No transaction: {root}"
    if not (tx / "journal.json").exists() and not list(tx.iterdir()):
        tx.rmdir()
        return f"Discarded empty preparation: {root}"
    journal = read_json(tx / "journal.json")
    journal_root = journal.get("root")
    if not isinstance(journal_root, str) or normalized(Path(journal_root)) != root:
        raise Conflict("Transaction belongs to another destination")
    old = validate_manifest(journal.get("old", {}))
    new = validate_manifest(journal.get("new", {}))
    if journal.get("phase") == "preparing":
        # The journal advances to prepared before the first destination mutation.
        remove_tree(tx, root)
        return f"Discarded interrupted preparation; destination preserved: {root}"
    if journal.get("phase", "prepared") != "prepared":
        raise Conflict("Unknown transaction phase; manual recovery required")
    names = sorted(set(old["skills"]) | set(new["skills"]))
    # A fully committed manifest means cleanup, not rollback.
    current = installed(root)
    committed = (tx / "committed").is_file()
    for name in names:
        path = root / name
        if path.exists():
            observed = inventory(path)
            allowed = [m["skills"].get(name) for m in (old, new)]
            if observed not in allowed:
                raise Conflict(f"Changed during interrupted operation; manual recovery required: {path}")
    if committed:
        if current != new:
            raise Conflict("Committed manifest changed; manual recovery required")
        for name, files in new["skills"].items():
            if inventory(root / name) != files:
                raise Conflict("Committed product changed; manual recovery required")
        remove_tree(tx, root)
        return f"Finished committed operation: {root}"
    if current not in (old, new):
        raise Conflict("Installation manifest changed; manual recovery required")
    for name, files in old["skills"].items():
        backup = tx / "old" / name
        if inventory(backup) != files:
            raise Conflict(f"Invalid recovery backup: {backup}")
    # Everything has been checked before restoring any path.
    for name in names:
        path = root / name
        if path.exists():
            remove_tree(path, root)
        if name in old["skills"]:
            shutil.copytree(tx / "old" / name, path)
    manifest = root / MANIFEST
    check_path(manifest)
    if old["skills"]:
        replacement = tx / "restore.json"
        if replacement.exists():
            replacement.unlink()
        write_json(replacement, old)
        os.replace(replacement, manifest)
    elif manifest.exists():
        manifest.unlink()
    remove_tree(tx, root)
    return f"Restored previous installation: {root}"


def recover(root: Path) -> str:
    root = normalized(root)
    if not root.exists():
        return f"No transaction: {root}"
    with operation_lock(root):
        return _recover_locked(root)


def _apply_locked(root: Path, new: dict, source: Path) -> str:
    old = preflight(root, new)
    if old == new:
        return f"Already current: {root}"
    root.mkdir(parents=True, exist_ok=True)
    tx = root / TRANSACTION
    tx.mkdir()  # Exclusive lock; never steal a live or interrupted transaction.
    prepared = False
    try:
        manifest_path = root / MANIFEST
        prior_manifest_hash = digest(manifest_path) if manifest_path.exists() else None
        journal = {"root": str(root), "old": old, "new": new, "phase": "preparing"}
        write_json(tx / "journal.json", journal)
        (tx / "old").mkdir()
        (tx / "new").mkdir()
        for name in old["skills"]:
            shutil.copytree(root / name, tx / "old" / name)
            if inventory(tx / "old" / name) != old["skills"][name]:
                raise Conflict("Backup verification failed; destination was not changed")
        for name, files in new["skills"].items():
            if inventory(source / name) != files:
                raise Conflict("Product changed before preparation")
            shutil.copytree(source / name, tx / "new" / name)
            if inventory(tx / "new" / name) != files:
                raise Conflict("Product changed while preparing installation")
        # Recheck source ownership after preparation, before any replacement.
        for name, files in old["skills"].items():
            if inventory(root / name) != files:
                raise Conflict("Installed skills changed while preparing installation")
        for name in set(new["skills"]) - set(old["skills"]):
            check_path(root / name)
            if (root / name).exists():
                raise Conflict(f"Unowned skill appeared while preparing: {root / name}")
        check_path(manifest_path)
        if (digest(manifest_path) if manifest_path.exists() else None) != prior_manifest_hash:
            raise Conflict("Manifest changed while preparing installation")
        journal["phase"] = "prepared"
        write_json(tx / "prepared.json", journal)
        os.replace(tx / "prepared.json", tx / "journal.json")
        prepared = True
        for name in sorted(set(old["skills"]) | set(new["skills"])):
            path = root / name
            check_path(path)
            if path.exists():
                if name not in old["skills"] or inventory(path) != old["skills"][name]:
                    raise Conflict(f"Destination changed before replacement: {path}")
                remove_tree(path, root)
            if name in new["skills"]:
                os.replace(tx / "new" / name, path)
        check_path(manifest_path)
        if (digest(manifest_path) if manifest_path.exists() else None) != prior_manifest_hash:
            raise Conflict("Manifest changed before commit")
        write_json(tx / "manifest.json", new)
        os.replace(tx / "manifest.json", root / MANIFEST)
        (tx / "committed").write_text("committed\n", encoding="utf-8")
        remove_tree(tx, root)
    except Exception:
        if tx.exists():
            if prepared:
                _recover_locked(root)
            else:
                remove_tree(tx, root)
        raise
    return f"{'Installed' if new['skills'] else 'Uninstalled'}: {root}"


def apply(root: Path, new: dict, source: Path = SOURCE) -> str:
    root = normalized(root)
    source = normalized(source)
    new = validate_manifest(new)
    preflight(root, new)
    with operation_lock(root):
        return _apply_locked(root, new, source)


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
        relative = PATHS[harness]
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
        relative = PATHS[harness]
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
    parser.add_argument("--all", action="store_true", help="Install to all five native locations")
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
    action.add_argument("--recover", action="store_true", help="Recover after stopping any other installer")
    parser.add_argument("--dry-run", action="store_true", help="Check and print changes without writing")
    args = parser.parse_args(argv)
    try:
        roots = destinations(args)
        if args.recover:
            if args.dry_run:
                raise Conflict("--recover cannot be combined with --dry-run")
            for root in roots:
                print(recover(root))
            return 0
        new = {"format": 1, "skills": {}} if args.uninstall else source_manifest()
        for root in roots:
            preflight(root, new)  # All destinations checked before any mutation.
        for root in roots:
            if args.dry_run:
                print(f"Would {'uninstall owned skills from' if args.uninstall else 'install ' + str(len(new['skills'])) + ' skills to'}: {root}")
            else:
                print(apply(root, new))
        return 0
    except (Conflict, OSError) as exc:
        print(f"REVibe: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
